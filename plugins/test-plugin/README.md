# test-plugin

A minimal test plugin that connects Claude Code to a local MCP server.

## MCP Server

Connects to `http://localhost:${TEST_MCP_PORT}/test/` via `mcp-remote`.

Default port: `3001`.

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `TEST_MCP_PORT` | `3001` | Port of the local MCP server |

To use a different port, set `TEST_MCP_PORT` in your environment or override it in `.mcp.json`.

## Requirements

- Node.js / npx available
- Local MCP server running at `http://localhost:<TEST_MCP_PORT>/test/`

## Installation

Add this plugin via the todevelopers marketplace. The MCP server `test-mcp` will be registered automatically.
