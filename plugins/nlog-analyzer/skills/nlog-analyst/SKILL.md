# NLog Analyst Skill

**Triggers:** activate this skill automatically when the user says phrases like "analyzuj logy", "analyze logs", "čo sa deje v logoch", "query the logs", "pozri sa do logov", "preskúmaj logy", "what's in the logs", "log analysis", "trace log", or when working with a `trace_logs.db` SQLite database.

This skill activates when working with NLog trace logs from the C4 framework. Use it to correctly interpret log fields, error patterns, and stack traces.

## On activation

When this skill is triggered, **automatically** perform the following steps before answering the user's question:

1. **Check for existing database** — look for `trace_logs.db` in the current working directory.
2. **If `trace_logs.db` does NOT exist** — run the full import flow:
   - Locate `nlog_import.py` (see `/nlog:import` command for search locations)
   - Run: `python "<path-to-nlog_import.py>" "<current-folder>"`
   - Show import summary to the user
3. **Open the database** — use `plugin_nlog-analyzer_sqlite-logs` MCP server's `open_database` tool with the path to `trace_logs.db`.
4. **Proceed with the user's request** — translate it to SQL, run via the MCP server, and present results.

If the import fails or `nlog_import.py` cannot be found, ask the user for the path.

---

## Log record format

```
{timestamp}|{processId}|{threadId}|{level}|{plugin}|{assembly}|{class}|{method}|{message}
```

### Field meanings

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | TEXT | ISO datetime with milliseconds: `2026-02-20 15:11:09.6951` |
| `process_id` | INTEGER | OS process ID. Each C4 application run has a unique process ID. Multiple process IDs in one log session indicate restarts or multiple running instances. |
| `thread_id` | INTEGER | Thread within the process. High thread_id variance indicates multithreaded activity. Use to correlate concurrent operations. |
| `level` | TEXT | Log severity: `TRACE` < `DEBUG` < `INFO` < `WARN` < `ERROR` < `FATAL` |
| `plugin` | TEXT | C4 plugin name. May be **empty** for framework-level or unhandled exceptions. **Inconsistent format:** values can be a short name (`DeveloperConsole`, `SC_SPCC`) or a full namespace (`Gamanet.C4.Client.Panels.MBSecure.FileImport`). Always filter with `LIKE '%MBSecure%'` instead of exact equality. |
| `assembly` | TEXT | .NET assembly name (e.g. `DeveloperConsole.Shared`, `DeveloperConsoleFramework`). May be empty. |
| `class` | TEXT | .NET class where the log was emitted |
| `method` | TEXT | .NET method where the log was emitted |
| `message` | TEXT | Log message text. May be empty for TRACE entries (method entry/exit markers). |
| `stack_trace` | TEXT | Multiline stack trace if this is an exception record. Last line is always a call chain in format `A => B => C`. NULL if not an exception. |
| `source_file` | TEXT | Original `.log` filename without path |

---

## C4 framework context

**C4** is a modular embedded/industrial framework with a plugin architecture. Each plugin is an independent unit (similar to a module or service) that logs under its own `plugin` name.

### Typical plugin names
- `DeveloperConsole` — developer tooling and diagnostics
- `MBSecure` — security/access control module
- `MBThermal` — thermal management
- `SC_SPCC` — short-name style plugin identifier
- `HttpConnector` appears in `class`, not `plugin` — it's a shared framework component

> **Warning — inconsistent `plugin` format:** the same logical plugin may appear as a short name (`MBSecure`, `SC_SPCC`) in some entries and as a full namespace (`Gamanet.C4.Client.Panels.MBSecure.FileImport`) in others. **Always use `LIKE '%MBSecure%'` instead of `= 'MBSecure'`** when filtering by plugin.

### process_id interpretation
- Single `process_id` = single session/run
- Multiple `process_ids` = application was restarted, or multiple instances ran in parallel
- Filter by `process_id` to isolate a specific run when debugging

### thread_id interpretation
- Main thread typically has low thread_id (1, 4, 8...)
- Background workers and async tasks have higher thread_ids
- Use `WHERE thread_id = X` to follow a single execution thread

---

## TRACE entries

TRACE-level entries with an empty message are method entry/exit markers:
```
2026-02-20 15:11:09.6951|17988|8|TRACE|DeveloperConsole|DeveloperConsole.Shared|AppConfigRepository|SaveData|()
```
The `()` or empty message means the method was entered. These entries are useful for profiling but add noise — filter with `level != 'TRACE'` for error analysis.

---

## Exception records

Exceptions have `level = 'ERROR'` or `'FATAL'` and a non-NULL `stack_trace`.

```
2026-02-20 13:54:36.6961|20740|5|ERROR|||HttpConnector|SendBase|Unhandled Exception: It is not possible to process entity...
Gamanet.C4.SimpleInterfaces.ValidationException: ...
   at Gamanet.C4.SapiClientConnector.Internal.HttpConnector.HandleUnsuccessfullStatusCode(...)
   at Gamanet.C4.SapiClientConnector.Internal.HttpConnector.SendBase(...)
DeviceRepository.Create => HttpConnector.SendBase => Tracer.Error
```

Key observations:
- `plugin` and `assembly` are often **empty** for unhandled exceptions (framework catches them before plugin context is set)
- The **last line** of `stack_trace` is always a **call chain**: `A => B => C` — this shows the logical call path, not the .NET stack frames
- Exception type is embedded in `message` after `Unhandled Exception:`

---

## Common error patterns in C4

| Pattern | Meaning |
|---------|---------|
| `Unhandled Exception: It is not possible to process entity` | HTTP response parsing failure, typically API response format mismatch |
| `ValidationException` | Business rule violation or invalid input to a C4 SAPI endpoint |
| `level = 'FATAL'` | Application-terminating error, look at `process_id` change immediately after |
| Empty `plugin` on ERROR | Exception caught at framework level before plugin context was established |
| Multiple ERRORs same timestamp range, different `thread_id` | Concurrent failure — possibly cascading errors from shared resource |

---

## Analysis tips

1. **Start with errors**: `WHERE level IN ('ERROR', 'FATAL')` to get the big picture
2. **Correlate by process**: Group by `process_id` to separate sessions
3. **Find the root cause**: Sort errors by timestamp ASC — the first error is usually the root cause
4. **Use call chains**: The last line of `stack_trace` (the `A => B => C` line) shows the logical path to the error
5. **Cross-reference threads**: If multiple threads failed at the same time, look for a shared class/method in their stack traces
6. **Parse errors table**: Check `parse_errors` table for log lines that couldn't be parsed — may indicate log corruption or format changes

---

## Cross-referencing with source code via VS MCP

When `plugin_nlog-analyzer_vs-mcp` MCP server is available (Visual Studio 2022 open with VS MCP Server extension running), **always enrich log analysis with source code context**. Do this automatically after identifying errors or suspicious patterns — do not wait for the user to ask.

### When to cross-reference

Cross-reference with source code whenever you find:
- An ERROR or FATAL entry with a known `class` and `method`
- A repeating exception type or call chain
- An unexpected sequence of TRACE/DEBUG entries suggesting wrong code path
- A class/method that appears frequently in errors but rarely in normal flow

### How to cross-reference

For each key class/method identified in the logs:

1. **Find the definition** — use `FindSymbolDefinition` with the class or method name from the `class`/`method` log columns.
   - If the class name is ambiguous (multiple matches), narrow by assembly from the `assembly` log column.

2. **Inspect the code** — read the relevant method body. Focus on:
   - Exception handling (`try/catch`) — is the exception swallowed or re-thrown?
   - Null checks — could any parameter be null at the point of failure?
   - Conditions that match the log message text (e.g. a string in `throw new Exception("...")`)

3. **Trace call chains** — if the log `stack_trace` shows a call chain `A => B => C`, use `GetMethodCallers` on the innermost method (`C`) to verify it matches what the logs show. Use `GetMethodCalls` to see what `C` calls further.

4. **Check related callers** — use `GetMethodCallers` on the failing method to understand all places it is called from. If the error only occurs for some callers, the issue may be in how the caller constructs its arguments.

5. **Look for recent changes** — if the source reveals a suspicious pattern, mention it to the user and suggest checking git blame or recent commits for that method.

### How to present combined findings

After cross-referencing, present findings in two layers:

**Layer 1 — Log evidence** (what the logs show):
- Timestamp range, process/thread IDs, frequency
- Error message and exception type
- Call chain from `stack_trace`

**Layer 2 — Source code context** (what VS MCP reveals):
- Actual method body or relevant excerpt
- Whether the exception is thrown explicitly or propagated
- Any suspicious conditions or missing null-guards
- Other callers that could trigger the same path

### Fallback when VS MCP is not available

If `plugin_nlog-analyzer_vs-mcp` is not connected (VS not running or extension not installed), skip source cross-referencing silently and note at the end of your analysis:

> _Source code cross-reference not available — start Visual Studio 2022 with VS MCP Server extension to enable it._

Do **not** fall back to Grep or file-based search as a substitute — without Roslyn semantics the results would be unreliable for .NET codebases.
