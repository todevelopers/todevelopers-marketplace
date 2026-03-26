---
name: vs-mcp
description: Activate VS MCP semantic mode for C# development. Use when working with .cs, .csproj, or .sln files, or when asked to find symbols, refactor, or analyze a C# codebase connected to a running VS MCP Server.
triggers:
  - pattern: "\\.(cs|csproj|sln)$"
    description: Triggered when a C# source, project, or solution file is opened or mentioned
  - pattern: "(find|search|locate).*(class|method|interface|symbol|type|property)"
    description: Triggered when searching for C# code elements by name
  - pattern: "(refactor|rename|find usages|find references|go to definition)"
    description: Triggered when performing semantic code operations
  - mcp_server: "vs-mcp"
    description: Triggered when the vs-mcp MCP server is connected in the session
exclude:
  - pattern: "\\.(py|js|ts|go|rs|java|rb|php)$"
    description: Do not trigger for non-C# languages
---

# VS MCP Semantic Mode

You are connected to the VS MCP Server — a Visual Studio 2022 extension that exposes the C# Roslyn compiler and VS debugger via MCP.

**Always prefer VS MCP semantic tools over text-based search when working on C# code:**

| Instead of | Use |
|---|---|
| Grep / Glob for symbols | `FindSymbols` |
| Text search for a definition | `FindSymbolDefinition` (F12 equivalent) |
| Grep for usages/references | `FindSymbolUsages` (Shift+F12 equivalent) |
| LS / Glob for project structure | `GetSolutionTree` |
| Manual call tracing | `GetMethodCallers` / `GetMethodCalls` |
| Reading inheritance manually | `GetInheritance` |
| Building to check errors | `GetDiagnostics` |
| Manual rename across files | `RenameSymbol` (compiler-verified, safe) |

**Why:** These tools use Roslyn for semantic analysis — ~90% fewer tokens than text search, and compiler-accurate results that account for overloads, generics, and implicit conversions.

For debugging tasks, use the 19 preview debugging tools (breakpoints, call stack, variable inspection) instead of adding print statements.
