# /nlog:analyze

Analyze NLog data in the SQLite database using natural language. Claude translates your description into SQL, runs it via `mcp-sqlite-tools`, and presents results clearly.

## Usage

```
/nlog:analyze <natural language description>
```

**Examples:**
- `/nlog:analyze show all errors and fatals`
- `/nlog:analyze what happened in the HttpConnector class`
- `/nlog:analyze find all exceptions with stack traces`
- `/nlog:analyze show activity between 15:00 and 16:00`

## How Claude processes the request

0. **Ensure database is ready** — always do this before the first query in a session:
   - **Open:** If no database is currently open in `plugin_nlog-analyzer_sqlite-logs`, find `trace_logs.db` in the current working directory, copy it locally to avoid NTFS issues, and open from the local path:
     ```
     cp "<working-dir>/trace_logs.db" /tmp/nlog-analyzer-analyze.db
     ```
     Then call `open_database` with `/tmp/nlog-analyzer-analyze.db`.
     If `trace_logs.db` is not found, ask the user to run `/nlog:import` first.
   - **Verify:** Call `list_tables` to confirm the `logs` table exists in the opened database.
   - **Schema:** Use the schema reference below — **never guess column names**. The correct columns are `timestamp`, `process_id`, `thread_id`, `level`, `plugin`, `assembly`, `class`, `method`, `message`, `stack_trace`, `source_file`. There is no `logger` column.

1. **Understand intent** — identify what the user is looking for (level filter, class/method filter, time range, exceptions, etc.)
2. **Translate to SQL** — build a query against the `logs` table using only columns from the schema reference
3. **Execute** — run via `mcp-sqlite-tools` `execute_read_query`
4. **Display results** — format as a readable table or list
5. **Suggest follow-ups** — propose 2–3 related queries that might be useful

## Schema reference

```sql
logs (
    id, timestamp, process_id, thread_id,
    level,       -- TRACE, DEBUG, INFO, WARN, ERROR, FATAL
    plugin,      -- C4 plugin name (e.g. DeveloperConsole, MBSecure)
    assembly,    -- .NET assembly name
    class,       -- .NET class name
    method,      -- .NET method name
    message,     -- log message
    stack_trace, -- multiline stack trace (NULL if none)
    source_file  -- source .log filename
)
```

## Common query patterns

### All errors and fatals
```sql
SELECT timestamp, process_id, thread_id, class, method, message
FROM logs
WHERE level IN ('ERROR', 'FATAL')
ORDER BY timestamp;
```

### Specific class or method
```sql
SELECT timestamp, level, class, method, message
FROM logs
WHERE class = 'HttpConnector'
ORDER BY timestamp;
```

### Time range
```sql
SELECT timestamp, level, class, method, message
FROM logs
WHERE timestamp BETWEEN '2026-02-20 15:00:00' AND '2026-02-20 16:00:00'
ORDER BY timestamp;
```

### All entries with stack traces (exceptions)
```sql
SELECT timestamp, level, class, method, message, stack_trace
FROM logs
WHERE stack_trace IS NOT NULL
ORDER BY timestamp;
```

### Specific process
```sql
SELECT timestamp, level, class, method, message
FROM logs
WHERE process_id = 17988
ORDER BY timestamp;
```

### Most frequent errors (grouped by message)
```sql
SELECT message, COUNT(*) AS count, level
FROM logs
WHERE level IN ('ERROR', 'FATAL')
GROUP BY message, level
ORDER BY count DESC
LIMIT 20;
```

### Activity per plugin
```sql
SELECT plugin, COUNT(*) AS count,
       SUM(CASE WHEN level IN ('ERROR','FATAL') THEN 1 ELSE 0 END) AS errors
FROM logs
WHERE plugin != ''
GROUP BY plugin
ORDER BY count DESC;
```

### Thread activity timeline
```sql
SELECT thread_id, COUNT(*) AS entries,
       MIN(timestamp) AS first_seen,
       MAX(timestamp) AS last_seen
FROM logs
GROUP BY thread_id
ORDER BY entries DESC;
```

## Response format

After running the query, Claude will:
- Show results in a formatted table (truncated to 50 rows for readability, with row count)
- Highlight patterns or anomalies noticed in the data
- Suggest 2–3 follow-up queries based on what was found
