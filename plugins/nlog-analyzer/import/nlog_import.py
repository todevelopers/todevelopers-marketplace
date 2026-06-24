#!/usr/bin/env python3
"""
NLog Importer - imports NLog trace log files into SQLite database.
Uses only Python standard library (no external packages required).

Usage:
    python nlog_import.py "C:\\path\\to\\logs"
    python nlog_import.py "C:\\path\\to\\logs" --verbose
"""

import sqlite3
import re
import os
import hashlib
import shutil
import tempfile
import argparse
import logging
from pathlib import Path

# Pattern matching start of a new log record:
# 2026-02-20 15:11:09.6951|17988|8|TRACE|...|...|class|method|message
LOG_LINE_RE = re.compile(
    r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)'  # timestamp
    r'\|(\d*)'                                          # process_id (may be empty)
    r'\|(\d*)'                                          # thread_id (may be empty)
    r'\|([^|]*)'                                        # level
    r'\|([^|]*)'                                        # plugin (may be empty)
    r'\|([^|]*)'                                        # assembly (may be empty)
    r'\|([^|]*)'                                        # class
    r'\|([^|]*)'                                        # method
    r'\|?(.*)?$'                                        # message (may be empty)
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    process_id INTEGER,
    thread_id INTEGER,
    level TEXT,
    plugin TEXT,
    assembly TEXT,
    class TEXT,
    method TEXT,
    message TEXT,
    stack_trace TEXT,
    source_file TEXT NOT NULL,
    UNIQUE(timestamp, process_id, thread_id, class, method, message) ON CONFLICT IGNORE
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_class ON logs(class);
CREATE INDEX IF NOT EXISTS idx_process_id ON logs(process_id);

CREATE TABLE IF NOT EXISTS parse_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    line_number INTEGER,
    raw_line TEXT
);

CREATE TABLE IF NOT EXISTS import_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imported_at TEXT DEFAULT (datetime('now')),
    source_folder TEXT,
    files_processed INTEGER,
    records_imported INTEGER,
    records_skipped INTEGER,
    errors INTEGER
);
"""

INSERT_LOG_SQL = """
INSERT INTO logs
    (timestamp, process_id, thread_id, level, plugin, assembly, class, method, message, stack_trace, source_file)
VALUES
    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

INSERT_ERROR_SQL = """
INSERT INTO parse_errors (source_file, line_number, raw_line) VALUES (?, ?, ?)
"""

INSERT_RUN_SQL = """
INSERT INTO import_runs (source_folder, files_processed, records_imported, records_skipped, errors)
VALUES (?, ?, ?, ?, ?)
"""

BATCH_SIZE = 10_000
PROGRESS_INTERVAL = 10_000


def setup_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def parse_line(line: str):
    """Returns match groups or None if line is not a log header."""
    m = LOG_LINE_RE.match(line)
    if not m:
        return None
    return m.groups()


def to_int_or_none(val: str):
    val = val.strip()
    return int(val) if val else None


def flush_batch(conn: sqlite3.Connection, batch: list, error_batch: list):
    """Insert a batch of records and errors, return (inserted, skipped)."""
    inserted = 0
    skipped = 0
    cur = conn.cursor()
    for row in batch:
        cur.execute(INSERT_LOG_SQL, row)
        if cur.rowcount == 1:
            inserted += 1
        else:
            skipped += 1
    if error_batch:
        cur.executemany(INSERT_ERROR_SQL, error_batch)
    conn.commit()
    return inserted, skipped


def process_file(conn: sqlite3.Connection, log_file: Path, verbose: bool):
    """Stream-process a single log file. Returns (imported, skipped, errors)."""
    source_name = log_file.name
    total_imported = 0
    total_skipped = 0
    total_errors = 0

    log_batch = []
    error_batch = []
    line_number = 0

    # Pending record state
    pending = None          # tuple of parsed fields
    pending_stack = []      # accumulates stack trace lines

    def commit_pending():
        nonlocal pending, pending_stack
        if pending is None:
            return
        ts, pid, tid, level, plugin, assembly, cls, method, message = pending
        stack_trace = '\n'.join(pending_stack) if pending_stack else None
        row = (
            ts,
            to_int_or_none(pid),
            to_int_or_none(tid),
            level.strip(),
            plugin.strip(),
            assembly.strip(),
            cls.strip(),
            method.strip(),
            message.strip(),
            stack_trace,
            source_name,
        )
        log_batch.append(row)
        pending = None
        pending_stack = []

    def maybe_flush(force=False):
        nonlocal total_imported, total_skipped
        if force or len(log_batch) >= BATCH_SIZE:
            imp, skp = flush_batch(conn, log_batch, error_batch)
            total_imported += imp
            total_skipped += skp
            log_batch.clear()
            error_batch.clear()

    with open(log_file, encoding='utf-8-sig', errors='replace') as f:
        for raw_line in f:
            line_number += 1
            line = raw_line.rstrip('\n\r')

            groups = parse_line(line)
            if groups:
                # New log record – commit previous pending record first
                commit_pending()
                pending = groups
            elif pending is not None:
                # Continuation line (stack trace)
                pending_stack.append(line)
            else:
                # Line before any valid log record
                if line.strip():
                    total_errors += 1
                    error_batch.append((source_name, line_number, line))

            if line_number % PROGRESS_INTERVAL == 0:
                maybe_flush()
                if verbose:
                    logging.info(
                        f"  {source_name}: {line_number:,} lines read, "
                        f"{total_imported:,} imported, {total_skipped:,} skipped"
                    )

        # Commit last pending record
        commit_pending()
        maybe_flush(force=True)

    return total_imported, total_skipped, total_errors


def find_log_files(folder: Path):
    return sorted(folder.rglob('*.log'))


def get_local_db_path(log_folder: Path) -> Path:
    """Returns a deterministic session-persistent local DB path for this log folder.

    Uses MD5 of the folder path so the same folder always maps to the same local file.
    This allows repeated imports within a session to reuse the existing local copy,
    and lets the MCP server open the DB without NTFS filesystem issues.
    """
    folder_hash = hashlib.md5(str(log_folder).encode('utf-8')).hexdigest()[:12]
    local_dir = Path(tempfile.gettempdir()) / 'nlog-analyzer'
    local_dir.mkdir(exist_ok=True)
    return local_dir / f'{folder_hash}.db'


def main():
    parser = argparse.ArgumentParser(
        description='Import NLog .log files into SQLite database.'
    )
    parser.add_argument('log_folder', help='Path to folder containing .log files')
    parser.add_argument('--verbose', action='store_true', help='Print progress every 10,000 lines')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(message)s')

    log_folder = Path(args.log_folder).resolve()
    if not log_folder.is_dir():
        logging.error(f"Folder not found: {log_folder}")
        raise SystemExit(1)

    db_path = log_folder / 'trace_logs.db'
    # Local path on the native filesystem — avoids NTFS locking/journaling issues.
    # Deterministic per log_folder so repeated imports reuse the same file.
    # The MCP server uses this path; db_path (Windows mount) is for SQLite Browser.
    local_db_path = get_local_db_path(log_folder)

    logging.info(f"Database        : {db_path}")
    logging.info(f"Local DB        : {local_db_path}")

    # Seed local copy from Windows path only when local copy is absent (new session).
    if local_db_path.stat().st_size <= 100 if local_db_path.exists() else True:
        if db_path.exists() and db_path.stat().st_size > 100:
            logging.info("Seeding local DB from existing database...")
            shutil.copy2(db_path, local_db_path)

    conn = setup_db(local_db_path)

    log_files = find_log_files(log_folder)
    if not log_files:
        logging.warning("No .log files found.")
        conn.close()
        return

    logging.info(f"Found {len(log_files)} log file(s).")

    total_files = 0
    total_imported = 0
    total_skipped = 0
    total_errors = 0

    for log_file in log_files:
        logging.info(f"Processing: {log_file.name}")
        try:
            imp, skp, err = process_file(conn, log_file, args.verbose)
            total_files += 1
            total_imported += imp
            total_skipped += skp
            total_errors += err
            logging.info(
                f"  Done: {imp:,} imported, {skp:,} skipped (duplicates), {err:,} parse errors"
            )
        except Exception as e:
            logging.error(f"  Failed to process {log_file.name}: {e}")

    # Record import run
    conn.execute(INSERT_RUN_SQL, (
        str(log_folder), total_files, total_imported, total_skipped, total_errors
    ))
    conn.commit()
    conn.close()

    # Remove leftover SQLite journal/WAL files from previous failed runs before
    # copying — their presence causes SQLite Browser to attempt rollback and fail.
    for suffix in ('-journal', '-wal', '-shm'):
        stale = db_path.parent / (db_path.name + suffix)
        if stale.exists():
            try:
                stale.unlink()
            except OSError:
                pass

    # Copy finished DB to Windows working directory for SQLite Browser access.
    # The local_db_path is kept alive for the MCP server.
    shutil.copyfile(local_db_path, db_path)

    print()
    print("=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"  Files processed : {total_files:,}")
    print(f"  Records imported: {total_imported:,}")
    print(f"  Records skipped : {total_skipped:,}  (duplicates)")
    print(f"  Parse errors    : {total_errors:,}")
    print(f"  Database        : {db_path}")
    print(f"  Local DB        : {local_db_path}")
    print("=" * 60)


if __name__ == '__main__':
    main()
