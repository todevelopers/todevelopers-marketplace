# vs-mcp-client

A Claude Code plugin that connects Claude Code to a local **VS MCP** server via the Model Context Protocol (MCP).

## What it does

This plugin registers the `vs-mcp` MCP server in your Claude Code configuration. It uses `mcp-remote` to connect to a locally running VS MCP server at `http://localhost:3001/sdk/`.

Once installed, Claude Code will have access to all tools and resources exposed by your VS MCP server.

## Requirements

- A running VS MCP server accessible at `http://localhost:3001/sdk/`
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

## Author

**ToDevelopers**
