"""
Nook Image MCP Server — 纯 I/O 桥接器
职责：鉴权 + 转发 + 原样返回。不校验参数、不处理业务逻辑。
所有 Prompt 工程、风格控制、后处理均由调用方 Agent/Skill 负责。
"""

import base64
import os
import sys
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# 环境变量加载（优先 .env 文件，兜底系统环境变量）
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv

    _env_file = Path(__file__).parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass  # dotenv 非必需，.env 不存在时从系统环境变量读取

IMAGINE_URL = os.environ.get("IMAGINE_URL", "")
IMAGINE_KEY = os.environ.get("IMAGINE_KEY", "")

if not IMAGINE_URL or not IMAGINE_KEY:
    print(
        "ERROR: IMAGINE_URL and IMAGINE_KEY must be set "
        "(in .env or as environment variables).",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "nook-image-mcp"
)


@mcp.tool()
def generate_image(
    prompt: str,
    model: str = "gpt-image-2",
    size: str = "1024x1024",
    quality: str = "auto",
    response_format: str = "b64_json",
    n: int = 1,
) -> dict:
    """
    纯粹的 Imagine API 桥接器。
    仅负责：鉴权 + 转发 + 原样返回。
    所有提示词工程、风格控制均由调用方 (Agent / Skill) 处理。

    Args:
        prompt: 图片描述提示词（由调用方生成）
        model:  生图模型名称，默认 gpt-image-2
                可选: gpt-image-1, gpt-image-1.5, gpt-image-2
        size:   图片尺寸，默认 1024x1024
                可选: 1024x1024, 1536x1024, 1024x1536, auto
        quality: 图片质量，默认 auto
                 可选: auto, low, medium, high
        response_format: 返回格式，默认 b64_json
                         可选: b64_json, url
        n:      生成图片数量，默认 1
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "response_format": response_format,
        "n": n,
    }

    try:
        with httpx.Client(timeout=300) as client:
            resp = client.post(
                IMAGINE_URL,
                headers={
                    "Authorization": f"Bearer {IMAGINE_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException:
        return {"error": "请求超时（300s），生图通常需要 30-120s，请稍后重试。"}
    except httpx.HTTPStatusError as e:
        return {
            "error": f"API 返回错误: {e.response.status_code}",
            "detail": e.response.text,
        }
    except Exception as e:
        return {"error": f"请求异常: {str(e)}"}

    # 标准化返回：统一包装为 {"images": [...], "raw": ...}
    images = []
    for item in data.get("data", []):
        if "b64_json" in item:
            images.append({
                "type": "base64",
                "data": item["b64_json"],
                "revised_prompt": item.get("revised_prompt", ""),
            })
        elif "url" in item:
            images.append({
                "type": "url",
                "url": item["url"],
                "revised_prompt": item.get("revised_prompt", ""),
            })

    return {
        "images": images,
        "model": model,
        "size": size,
        "quality": quality,
    }


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()  # 默认 stdio 传输

