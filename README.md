# ToDevelopers Claude Marketplace

A plugin marketplace for Claude Code by [ToDevelopers](https://github.com/todevelopers), providing tools and integrations to extend Claude's capabilities.

## Quick Start

Add this marketplace to Claude Code:

```bash
/plugin marketplace add todevelopers/claude-marketplace
```

Browse and install plugins:

```bash
/plugin
```

Install a specific plugin:

```bash
/plugin install vs-mcp-client@todevelopers-marketplace
```

List installed marketplaces:

```bash
/plugin marketplace list
```

## Available Plugins

### VS MCP client

A Claude Code plugin that connects Claude Code to the [VS MCP Server](https://marketplace.visualstudio.com/items?itemName=LadislavSopko.mcpserverforvs) — a Visual Studio 2022 extension exposing C#/Roslyn semantic analysis and the VS debugger via the Model Context Protocol (MCP).

### mcp-builder

A Claude Code plugin providing skills for building, packaging, and submitting MCP servers and apps. Includes skills for scaffolding MCP servers (`build-mcp-server`), adding interactive UI (`build-mcp-app`), bundling into distributable MCPB packages (`build-mcpb`), and walking through Anthropic's MCPB directory submission (`mcpb-submission-guide`).

### nlog-analyzer

A Claude Code plugin for analyzing NLog trace logs. Imports `.log` files (recursively, with deduplication and multiline stack-trace handling) into a SQLite database, then lets you query them in natural language via `/nlog:import` and `/nlog:analyze`. Bundles the `sqlite-logs` MCP server (`mcp-sqlite-tools`) and an `nlog-analyst` skill. Requires Python 3.8+ (standard library only) and Node.js/npx.

## Marketplace Structure

```
claude-marketplace/
├── .claude-plugin/
│   └── marketplace.json       # Marketplace metadata
└── plugins/
    ├── vs-mcp-client/
    │   ├── .claude-plugin/
    │   │   └── plugin.json    # Plugin metadata
    │   ├── .mcp.json          # MCP server configuration
    │   └── README.md
    ├── mcp-builder/
    │   ├── .claude-plugin/
    │   │   └── plugin.json    # Plugin metadata
    │   ├── skills/
    │   │   ├── build-mcp-server/
    │   │   │   └── SKILL.md
    │   │   ├── build-mcp-app/
    │   │   │   └── SKILL.md
    │   │   ├── build-mcpb/
    │   │   │   └── SKILL.md
    │   │   └── mcpb-submission-guide/
    │   │       └── SKILL.md
    │   └── README.md
    └── nlog-analyzer/
        ├── .claude-plugin/
        │   └── plugin.json    # Plugin metadata
        ├── .mcp.json          # MCP server (sqlite-logs)
        ├── commands/
        │   ├── import.md      # /nlog:import
        │   └── analyze.md     # /nlog:analyze
        ├── skills/
        │   └── nlog-analyst/
        │       └── SKILL.md
        ├── import/
        │   ├── nlog_import.py
        │   └── requirements.txt
        └── README.md
```

## Contributing

To contribute a plugin:

1. Fork this repository
2. Create a new directory under `plugins/` with your plugin name
3. Add the required structure:
   ```
   plugins/your-plugin-name/
   ├── .claude-plugin/
   │   └── plugin.json
   └── .mcp.json              # if your plugin provides an MCP server
   ```
4. Register your plugin in `.claude-plugin/marketplace.json`
5. Submit a pull request

### Plugin metadata (`plugin.json`)

```json
{
  "name": "your-plugin-name",
  "version": "1.0.0",
  "description": "What your plugin does",
  "author": {
    "name": "Your Name"
  }
}
```

## Author

**ToDevelopers** — [gazovic.todevelopers@gmail.com](mailto:gazovic.todevelopers@gmail.com)

## License

MIT
