---
name: vs-mcp-debug
description: Activate VS MCP debugging mode for C# development. Use when asked to debug, set breakpoints, inspect variables, step through code, attach to a process, or investigate crashes/exceptions in a .NET app connected to a running VS MCP Server.
triggers:
  - pattern: "(debug|breakpoint|callstack|call stack|step over|step into|attach|locals|inspect|watch|exception|crash|stack trace)"
    description: Triggered when debugging-related terms are mentioned
  - pattern: "(debug_start|debug_attach|debug_break|debug_continue|debug_step|debug_get_mode|debug_get_locals|debug_get_callstack|debug_evaluate|breakpoint_set)"
    description: Triggered when VS MCP debug tools are mentioned by name
  - pattern: "(infinite loop|null reference|NullReferenceException|runtime error|hang|frozen|stuck)"
    description: Triggered when diagnosing runtime issues that require a debugger
  - mcp_server: "vs-mcp"
    description: Triggered when the vs-mcp MCP server is connected in the session
exclude:
  - pattern: "\\.(py|js|ts|go|rs|java|rb|php)$"
    description: Do not trigger for non-C# languages
---

# VS MCP Debug Mode

You are connected to the VS MCP Server — a Visual Studio 2022 extension that exposes 19 debugging tools via MCP. The debugger is **state-based**: always check the current mode before calling tools, and use **polling** to detect state changes.

## Debugger Modes

| Mode | Meaning |
|------|---------|
| **Design** | No debug session active (default, or after stop/exit) |
| **Running** | App is executing |
| **Break** | Paused at breakpoint, exception, or manual break |

## Tool Reference

### Debug Control (10 tools)

| Tool | Required Mode | Description |
|------|--------------|-------------|
| `debug_get_mode` | Any | Returns current mode: Design, Running, or Break |
| `debug_start` | Design | Launch startup project with debugger (F5). Returns immediately — poll for mode change |
| `debug_stop` | Running/Break | Stop the debug session |
| `debug_break` | Running | Pause the running application |
| `debug_continue` | Break | Resume execution |
| `debug_step` | Break | Step `"over"`, `"into"`, or `"out"` |
| `immediate_execute` | Break | Execute expression with side effects (e.g. `myVar = 42`) |
| `debug_list_transports` | Any | List available transports (Default, Docker, WSL, etc.) |
| `debug_list_processes` | Any | List processes on a transport for attachment |
| `debug_attach` | Design | Attach to a running process by name or PID |

### Debug Inspection (5 tools)

| Tool | Required Mode | Description |
|------|--------------|-------------|
| `debug_get_callstack` | Break | Get call stack of current thread |
| `debug_get_locals` | Break | Get local variables in current frame |
| `debug_evaluate` | Break | Evaluate expression read-only (e.g. `myList.Count`) |
| `output_read` | Any | Read VS Output window pane (Build, Debug, Tests, etc.) |
| `error_list_get` | Any | Get errors/warnings from VS Error List |

### Breakpoint Management (4 tools)

| Tool | Required Mode | Description |
|------|--------------|-------------|
| `breakpoint_set` | Any | Set breakpoint by file+line or function name |
| `breakpoint_remove` | Any | Remove breakpoint at file+line |
| `breakpoint_list` | Any | List all breakpoints in solution |
| `exception_settings_set` | Any | Configure break-on-exception |

## Core Concept: Polling

MCP is request-response — there are no push notifications. Always poll `debug_get_mode` after `debug_start`, `debug_attach`, `debug_continue`, or `debug_step`.

```
debug_start → returns immediately (VS building + launching in background)
poll debug_get_mode → "Design"   (still building)
wait 3-5 seconds
poll debug_get_mode → "Running"  (app launched)
wait 2 seconds
poll debug_get_mode → "Break"    (breakpoint hit!)
→ now inspect: debug_get_callstack, debug_get_locals, debug_evaluate
```

## Primary Workflow: Attach to a Running Process

**This is the most common AI debugging workflow (90% of cases).** The app is already running; the AI attaches, investigates, and detaches.

```
1. debug_list_processes ()                        → see what's running locally
2. debug_attach (processName: "MyApp")            → attach debugger
3. debug_get_mode                                 → confirm "Running"
4. breakpoint_set (functionName: "HandleRequest") → set breakpoint on hot path
   -- OR --
5. debug_break                                    → pause the app immediately
6. debug_get_callstack                            → see where we are
7. debug_get_locals                               → see all variable values
8. debug_evaluate ("request.Url")                 → drill into specific expression
9. debug_step (direction: "over")                 → step forward
10. debug_get_locals                              → see how values changed
11. debug_continue                                → let it run
12. debug_stop                                    → detach when done
```

## Breakpoint Types

```
# File + line (use full Windows path)
breakpoint_set (file: "D:\\Path\\MyClass.cs", line: 42)

# Function (preferred — more reliable, pre-validated via Roslyn)
breakpoint_set (functionName: "MyClass.MyMethod")

# Conditional
breakpoint_set (functionName: "ProcessItem", condition: "item.Id > 100")
```

**Prefer function breakpoints** — they survive code moves, are validated against Roslyn symbols, and return an immediate error if the function doesn't exist.

## Transport System

| Transport | Qualifier | Use Case |
|-----------|-----------|----------|
| `Default` | `""` or machine name | Local processes |
| `Docker (Linux Container)` | Container name or ID | Docker containers |
| `WSL` | `""` | Windows Subsystem for Linux |

Use `debug_list_transports` first to confirm what's available, then `debug_list_processes` to find the process.

## Variable Tree Navigation

`debug_get_locals` returns root-level variables. Use `debug_evaluate` to drill deeper:

```
debug_get_locals                           → testCases: List<T> (hasMembers: true, memberCount: 7)
debug_evaluate ("testCases")               → expands list: { "[0]": "TestCase", ... }
debug_evaluate ("testCases[0]")            → drills into first item
debug_evaluate ("testCases[0].Data")       → drills into nested object
```

## Key Rules for AI Agents

1. **Prefer `debug_attach`** over `debug_start` when the process is already running.
2. **Poll, don't assume** — always check `debug_get_mode` after any state-changing call.
3. **Never call inspection tools in Design or Running mode** — they return errors.
4. **After `debug_step`**, mode is still Break — no polling needed, inspect immediately.
5. **After `debug_continue`**, poll for the next Break or Design (program exited).
6. **`debug_evaluate` is read-only** — prefer it over `immediate_execute` when just inspecting.
7. **`immediate_execute` modifies state** — use carefully (set variables, flip flags, escape loops).
8. **For tests:** You cannot launch a test in debug mode via MCP. Ask the user to right-click → Debug Test in VS. Once a breakpoint is hit, you have full inspection access.
9. **Use `output_read` and `error_list_get` freely** — they work in any mode.
10. **Check `breakpoint_list`** before adding to avoid duplicates.

## Common Patterns

### Investigate a Crash
```
exception_settings_set ("System.NullReferenceException", breakWhenThrown: true)
→ ask user to run the failing scenario
→ poll debug_get_mode → "Break" (exception hit)
→ debug_get_callstack + debug_get_locals → find the null
```

### Escape an Infinite Loop
```
debug_break                       → pause the stuck app
debug_get_locals                  → confirm done=false
immediate_execute ("done = true") → flip the flag
debug_continue                    → loop exits
```

### Read Output (No Debug Session Needed)
```
output_read (pane: "Build")        → build results
output_read (pane: "Debug")        → debug trace output
error_list_get (severity: "error") → compiler/runtime errors only
```

### Docker Attach
```
debug_list_transports              → verify "Docker (Linux Container)" available
debug_list_processes (transport: "Docker (Linux Container)", qualifier: "my-container")
debug_attach (processName: "dotnet", transport: "Docker (Linux Container)", qualifier: "my-container")
```
