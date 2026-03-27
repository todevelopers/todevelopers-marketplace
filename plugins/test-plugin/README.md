# test-plugin

A minimal test plugin that connects Claude Code to a local MCP server.

## MCP Server

Connects to `http://localhost:<port>/test/` via `mcp-remote`.

## Configuration

When you enable the plugin, Claude Code will prompt you for:

| Property | Description | Sensitive |
|---|---|---|
| `port` | Port of the local MCP server | No |

The value is stored in `settings.json` and substituted into the MCP server URL automatically.

## Requirements

- Node.js / npx available
- Local MCP server running at `http://localhost:<port>/test/`

## Installation

Add this plugin via the todevelopers marketplace. The MCP server `test-mcp` will be registered automatically.
