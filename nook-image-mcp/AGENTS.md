# Agent Deployment Contract

This repository is designed so any MCP-capable Agent can deploy it from a GitHub link without knowing the user's IDE or CLI in advance.

When the user asks you to "one-click deploy" this repo:

1. Clone or download this repository.
2. Run the cross-platform installer:

   ```bash
   python install.py
   ```

3. If the installer asks for `IMAGINE_URL` and `IMAGINE_KEY`, ask the user for those values and enter them. Never invent a key.
4. The installer creates a local `.env` file. Do not commit or upload `.env`.
5. Register this MCP server in your own MCP configuration as a local stdio server:

   - name: `nook-image-mcp`
   - command: the absolute Python path printed by `install.py`
   - args: the absolute `server.py` path printed by `install.py`
   - transport: `stdio`

6. Do not put `IMAGINE_KEY` in a public config file. `server.py` loads `.env` from its own directory.
7. Restart or reload MCP servers in your host application.
8. Verify that the `generate_image` tool is visible.

If your MCP host supports JSON config shaped like `mcpServers`, use:

```json
{
  "mcpServers": {
    "nook-image-mcp": {
      "command": "ABSOLUTE_PYTHON_PATH",
      "args": ["ABSOLUTE_SERVER_PATH"]
    }
  }
}
```

If your MCP host uses a different schema, translate the same stdio descriptor into that host's native MCP config format.

