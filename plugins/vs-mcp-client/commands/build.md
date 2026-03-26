---
description: Build the Visual Studio solution using VS MCP
allowed-tools:
  - mcp__vs-mcp__ExecuteCommand
---

Use the `ExecuteCommand` tool from the `vs-mcp` MCP server to build the current Visual Studio solution.

Call the tool with exactly these parameters:

```json
{
  "command": "Build.BuildSolution"
}
```

After the tool call completes, report the result to the user:
- If the build succeeded, confirm it with a brief success message.
- If the build failed or the tool returned an error, display the error output clearly.

Do not read any files, search the codebase, or take any other action. Simply execute the build command and report the outcome.
