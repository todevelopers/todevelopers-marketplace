# mcp-builder

A Claude Code plugin providing skills for building, packaging, and submitting MCP servers and apps.

## Skills

| Skill | Description |
|---|---|
| `build-mcp-server` | Scaffold and implement a new MCP server from scratch |
| `build-mcp-app` | Add interactive UI / widgets to an MCP server |
| `build-mcpb` | Package a local MCP server into a distributable MCPB bundle |
| `mcpb-submission-guide` | Guides through Anthropic MCPB directory submission requirements |

## Installation

```bash
/plugin install mcp-builder@todevelopers-marketplace
```

## Usage

Skills activate automatically based on context. You can also invoke them directly:

```bash
/build-mcp-server
/build-mcp-app
/build-mcpb
/mcpb-submission-guide
```

## Author

**ToDevelopers** — [gazovic.todevelopers@gmail.com](mailto:gazovic.todevelopers@gmail.com)
