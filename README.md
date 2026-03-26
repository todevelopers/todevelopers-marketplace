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

## Marketplace Structure

```
claude-marketplace/
├── .claude-plugin/
│   └── marketplace.json       # Marketplace metadata
└── plugins/
    └── vs-mcp-client/
        ├── .claude-plugin/
        │   └── plugin.json    # Plugin metadata
        ├── .mcp.json          # MCP server configuration
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
