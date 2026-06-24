# /nlog:import

Import NLog `.log` files from the current working directory into a SQLite database for analysis.

## Steps

1. **Determine the log folder** — use the current Cowork working directory as the source of log files.

2. **Locate the import script** — run this command to find `nlog_import.py`:
   ```
   find / -name "nlog_import.py" -path "*/nlog-analyzer/*" 2>/dev/null | head -1
   ```
   If the command returns no result, ask the user for the full path to `nlog_import.py`.

3. **Run the import script**:
   ```
   python "<path-to-nlog_import.py>" "<log-folder-path>"
   ```
   For verbose progress output:
   ```
   python "<path-to-nlog_import.py>" "<log-folder-path>" --verbose
   ```

4. **Display the output** — show all progress lines and the final summary to the user.

5. **Open the database** — parse the `Local DB:` line from the import summary output.
   Use the `plugin_nlog-analyzer_sqlite-logs` MCP server's `open_database` tool with the **local path** (NOT the Windows `Database:` path).
   - The local path avoids NTFS locking/journaling issues on mounted Windows directories.
   - Example: if summary shows `Local DB: /tmp/nlog-analyzer/abc123def456.db`, use that path.

6. **Inform the user** — confirm the database is open and ready. Mention:
   - How many records were imported
   - The Windows path (`Database:` line) is available for SQLite Browser — open it there after import
   - They can now use `/nlog:analyze` to query the logs in natural language
   - Or run raw SQL queries directly

## Example interaction

User: `/nlog:import`

Claude:
> Running import on current folder: `C:\Logs\MyApp`
> Found 5 log files.
> Processing Full.log ... 12,000 imported, 0 skipped, 0 errors
> ...
> IMPORT SUMMARY: 5 files, 48,320 records imported, 210 skipped, 3 errors
> Database  : C:\Logs\MyApp\trace_logs.db
> Local DB  : /tmp/nlog-analyzer/a1b2c3d4e5f6.db
>
> Database opened (local copy). Ready for analysis.
> SQLite Browser: open `C:\Logs\MyApp\trace_logs.db`
> Use `/nlog:analyze` or ask me to query the logs.
