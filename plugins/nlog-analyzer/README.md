# nlog-analyzer

A Claude Code plugin for analyzing NLog trace logs. Imports `.log` files into SQLite and enables natural-language querying via Claude.

---

## What it does

- **Imports** all `.log` files from a folder (recursively) into a SQLite database
- **Deduplicates** records — repeated imports do not add duplicates
- **Handles** multiline entries (stack traces)
- **Enables** natural-language querying via `/nlog:analyze`

---

## Requirements

- **Python 3.8+** — `nlog_import.py` uses only the standard library, no `pip install` needed
- **Node.js / npx** — for `mcp-sqlite-tools` MCP server (auto-downloaded via `npx -y mcp-sqlite-tools`)

---

## Installation

```bash
/plugin install nlog-analyzer@todevelopers-marketplace
```

If you haven't added the marketplace yet:

```bash
/plugin marketplace add todevelopers/claude-marketplace
```

---

## Usage

### 1. Import logs

```
/nlog:import
```

Runs import from the **current working directory**. After import, automatically opens the database via `mcp-sqlite-tools`.

### 2. Analyze

```
/nlog:analyze <description of what you're looking for>
```

Examples:
```
/nlog:analyze show all errors and fatals
/nlog:analyze what did HttpConnector do between 13:00 and 14:00
/nlog:analyze find the most frequent exceptions
/nlog:analyze entries from process 17988
```

### 3. Run import directly (without plugin)

```bash
python import/nlog_import.py "C:\path\to\logs"
python import/nlog_import.py "C:\path\to\logs" --verbose
```

---

## SQLite schema

### Table `logs`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `timestamp` | TEXT | `2026-02-20 15:11:09.6951` |
| `process_id` | INTEGER | OS process ID |
| `thread_id` | INTEGER | Thread ID |
| `level` | TEXT | `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL` |
| `plugin` | TEXT | Plugin name (may be empty) |
| `assembly` | TEXT | .NET assembly name (may be empty) |
| `class` | TEXT | .NET class |
| `method` | TEXT | .NET method |
| `message` | TEXT | Log message |
| `stack_trace` | TEXT | Stack trace (NULL if none) |
| `source_file` | TEXT | Source `.log` filename |

### Table `parse_errors`

Lines that could not be parsed — for diagnostics.

### Table `import_runs`

Import history: when, from where, how many records.

---

## Example SQL queries

```sql
-- All errors and fatals
SELECT timestamp, class, method, message
FROM logs WHERE level IN ('ERROR', 'FATAL')
ORDER BY timestamp;

-- Entries with stack traces (exceptions)
SELECT timestamp, class, method, message, stack_trace
FROM logs WHERE stack_trace IS NOT NULL
ORDER BY timestamp;

-- Specific class
SELECT * FROM logs WHERE class = 'MyClass' ORDER BY timestamp;

-- Time range
SELECT * FROM logs
WHERE timestamp BETWEEN '2026-02-20 15:00:00' AND '2026-02-20 16:00:00';

-- Most frequent errors
SELECT message, COUNT(*) AS n FROM logs
WHERE level = 'ERROR'
GROUP BY message ORDER BY n DESC LIMIT 10;

-- Activity by plugin
SELECT plugin, COUNT(*) AS entries,
       SUM(CASE WHEN level IN ('ERROR','FATAL') THEN 1 ELSE 0 END) AS errors
FROM logs WHERE plugin != ''
GROUP BY plugin ORDER BY entries DESC;
```

---

## NLog format (reference)

```
{timestamp}|{processId}|{threadId}|{level}|{plugin}|{assembly}|{class}|{method}|{message}
```

Example:
```
2026-02-20 15:11:09.6951|17988|8|TRACE|MyPlugin|MyAssembly|MyClass|MyMethod|()
2026-02-20 13:54:36.6961|20740|5|ERROR|||HttpConnector|SendBase|Unhandled Exception: ...
```

---

## Known limitations

- Optimized for the NLog pipe-separated format shown above
- Local DB in `/tmp/nlog-analyzer/` is cleared on system restart — re-import is needed for a new session
- On Windows NTFS mounts in containers, SQLite locking does not work reliably — the plugin uses a local DB copy to work around this

---

## Author

**ToDevelopers** — [gazovic.todevelopers@gmail.com](mailto:gazovic.todevelopers@gmail.com)

## License

MIT
