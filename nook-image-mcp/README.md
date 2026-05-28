# Nook Image MCP

极简的 OpenAI-compatible 图片生成 MCP Server。

它只做三件事：读取鉴权配置、转发图片生成请求、返回上游结果。Prompt 工程、风格控制和业务逻辑都应该留在调用方 Agent / Skill。

## 快速开始

### 面向任何 Agent 的一键部署

把这个 GitHub 链接交给任何支持 MCP 的 Agent，并让它阅读本仓库的 `AGENTS.md`。

Agent 应该执行：

```bash
python install.py
```

`install.py` 会完成：

- 安装 Python 依赖
- 引导填写 `IMAGINE_URL` 和 `IMAGINE_KEY`
- 创建本地 `.env`
- 测试 MCP server 是否可启动
- 输出标准 stdio MCP descriptor，方便 Agent 转成自己的配置格式

如果是 Windows 用户自己手动操作，也可以双击：

```text
setup.bat
```

`setup.bat` 只是 `python install.py` 的双击包装。

### Agent 应该怎么接入

所有 MCP 客户端本质上都需要同一组信息：

- name: `nook-image-mcp`
- transport: `stdio`
- command: `python`
- args: `["绝对路径/server.py"]`
- env: 不需要写进客户端配置，`server.py` 会读取同目录 `.env`

不同 IDE / CLI 的配置文件位置和字段名不同，所以本仓库不假设某一个宿主。Agent 拿到 `install.py` 打印的 descriptor 后，应转换成自己宿主支持的 MCP 配置。

### 手动部署

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and fill in IMAGINE_URL / IMAGINE_KEY
```

测试：

```bash
python server.py
```

stdio 模式下没有业务输出是正常的，它会等待 Agent 连接。

## Agent 配置方法

`server.py` 会自动读取同目录的 `.env`，所以 Agent 配置里通常不需要写 key。

通用 JSON 形态：

```json
{
  "mcpServers": {
    "nook-image-mcp": {
      "command": "python",
      "args": ["path/to/nook-image-mcp/server.py"]
    }
  }
}
```

### Claude Code

在项目根目录的 `.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "nook-image-mcp": {
      "command": "python",
      "args": ["path/to/nook-image-mcp/server.py"]
    }
  }
}
```

### Cursor

在 `.cursor/mcp.json`（项目级）或 `~/.cursor/mcp.json`（全局）中添加：

```json
{
  "mcpServers": {
    "nook-image-mcp": {
      "command": "python",
      "args": ["path/to/nook-image-mcp/server.py"]
    }
  }
}
```

### OpenAI Codex

在 `~/.codex/config.toml` 的 `[mcp_servers]` 段添加：

```toml
[mcp_servers.nook-image-mcp]
command = "python"
args = ["path/to/nook-image-mcp/server.py"]
```

### OpenCode

在项目根目录或 OpenCode 配置位置的 `opencode.json` / `opencode.jsonc` 中添加：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "nook-image-mcp": {
      "type": "local",
      "command": ["python", "path/to/nook-image-mcp/server.py"],
      "enabled": true
    }
  }
}
```

OpenCode 官方文档要求本地 MCP server 放在 `mcp` 字段中，`type` 为 `local`，`command` 为启动命令数组。

## 环境变量

在 `.env` 中配置：

```env
IMAGINE_URL=https://your-relay.example.com/v1/images/generations
IMAGINE_KEY=your-api-key-here
```

不要提交 `.env`。公开分享时只提交 `.env.example`。

## 工具接口

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | string | **必填** | 图片描述 |
| `model` | string | `gpt-image-2` | 模型名 |
| `size` | string | `1024x1024` | 尺寸 |
| `quality` | string | `auto` | 质量 |
| `response_format` | string | `b64_json` | 返回格式 |
| `n` | int | `1` | 生成数量 |

## 设计原则

- **MCP = 哑管道**：不处理业务、不存储状态
- **Skill = 业务大脑**：理解项目、生成 Prompt、保持一致性
- **配置分离**：URL/Key 只放在本地 `.env` 或调用方私有环境变量中

