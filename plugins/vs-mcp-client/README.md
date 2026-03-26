# vs-mcp-client

A Claude Code plugin that connects Claude Code to the **VS MCP Server** — a Visual Studio 2022 extension exposing C#/Roslyn semantic analysis and the VS debugger via the Model Context Protocol (MCP).

## What it does

This plugin registers the `vs-mcp` MCP server in your Claude Code configuration. It uses `mcp-remote` to connect to a locally running VS MCP server at `http://localhost:3001/sdk/`.

Once installed, Claude Code gains access to 41 semantic tools powered by Roslyn and the Visual Studio debugger — enabling accurate code navigation and refactoring without relying on text search.

## Available tools

### Semantic navigation
`FindSymbols`, `FindSymbolDefinition`, `FindSymbolUsages`, `GetDocumentOutline`, `GetSymbolAtLocation`

### Code understanding
`GetInheritance`, `GetMethodCallers`, `GetMethodCalls`

### Code analysis
`GetDiagnostics`

### Refactoring
`RenameSymbol`, `FormatDocument`

### Project & build
`GetSolutionTree`, `GetProjectReferences`, `ExecuteAsyncTest`, `ExecuteCommand`

### Editor
`GetActiveFile`, `GetSelection`

### Debugging (19 preview tools)
Breakpoint management, call stack inspection, variable evaluation, process attachment, Docker/WSL support.

## Requirements

- **Visual Studio 2022** (version 17.13 or later) with the [VS MCP Server](https://marketplace.visualstudio.com/items?itemName=LadislavSopko.mcpserverforvs) extension installed and running
- `npx` available in your `PATH` (comes with Node.js)

## MCP server configuration added

```json
{
  "vs-mcp": {
    "command": "npx",
    "args": [
      "-y",
      "mcp-remote",
      "http://localhost:3001/sdk/"
    ]
  }
}
```

## Installation

Install via the Claude Code marketplace:

```
/plugin install vs-mcp-client
```

## Usage

After installation, invoke the `/vs-mcp` skill to activate semantic mode for your session:

```
/vs-mcp
```

This instructs Claude to use VS MCP semantic tools instead of Grep/Glob/LS when working on C# code — providing ~90% fewer tokens and compiler-accurate results.

## Author

**ToDevelopers**
