# Nook MCP

统一存放 nook 的 MCP servers。

## Servers

- `nook-image-mcp`: OpenAI-compatible image generation MCP bridge. It reads `IMAGINE_URL` and `IMAGINE_KEY` from a local `.env` file, forwards image generation requests, and exposes the `generate_image` MCP tool.

## How Agents Should Deploy

Each MCP server directory contains its own `AGENTS.md`, `install.py`, and `mcp-manifest.json`.

For `nook-image-mcp`:

```bash
cd nook-image-mcp
python install.py
```

The installer will ask for the user's API configuration, create `.env`, verify the server, and print a stdio MCP descriptor that any MCP-capable Agent can translate into its own config format.
