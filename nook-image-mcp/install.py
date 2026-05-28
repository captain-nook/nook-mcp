#!/usr/bin/env python3
"""
Cross-agent installer for Nook Image MCP.

This script intentionally does not assume a specific IDE or CLI client.
It installs dependencies, creates the local .env file, verifies that the
MCP server can be imported, then prints the exact stdio server descriptor
that any MCP-capable Agent can translate into its own config format.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
SERVER_PATH = ROOT / "server.py"
REQUIREMENTS_PATH = ROOT / "requirements.txt"


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)


def ensure_python() -> str:
    python = sys.executable or shutil.which("python") or shutil.which("python3")
    if not python:
        raise RuntimeError("Python was not found. Install Python 3.10+ first.")
    return str(Path(python).resolve())


def install_dependencies(python: str) -> None:
    run([python, "-m", "pip", "install", "-r", str(REQUIREMENTS_PATH)])


def create_env(imagine_url: str | None, imagine_key: str | None, force: bool) -> None:
    if ENV_PATH.exists() and not force:
        print(".env already exists; keeping it.")
        return

    if not imagine_url:
        imagine_url = input("IMAGINE_URL: ").strip()
    if not imagine_key:
        imagine_key = getpass.getpass("IMAGINE_KEY: ").strip()

    if not imagine_url or not imagine_key:
        raise RuntimeError("IMAGINE_URL and IMAGINE_KEY are required.")

    ENV_PATH.write_text(
        f"IMAGINE_URL={imagine_url}\nIMAGINE_KEY={imagine_key}\n",
        encoding="utf-8",
    )
    print(".env created.")


def verify_server(python: str) -> None:
    run([python, "-c", "import server; print('server import ok')"])


def print_descriptor(python: str) -> None:
    descriptor = {
        "name": "nook-image-mcp",
        "transport": "stdio",
        "command": python,
        "args": [str(SERVER_PATH)],
        "env_file": str(ENV_PATH),
        "required_env": ["IMAGINE_URL", "IMAGINE_KEY"],
        "tools": ["generate_image"],
        "note": "Do not copy IMAGINE_KEY into public config. server.py loads .env from this directory.",
    }

    print("\nMCP stdio descriptor:")
    print(json.dumps(descriptor, ensure_ascii=False, indent=2))

    print("\nGeneric MCP config shape:")
    print(
        json.dumps(
            {
                "mcpServers": {
                    "nook-image-mcp": {
                        "command": python,
                        "args": [str(SERVER_PATH)],
                    }
                }
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    print(
        "\nAgent instruction: register a local/stdio MCP server named "
        "'nook-image-mcp' using the command and args above. The key is already "
        "stored in the local .env file."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Nook Image MCP for any MCP-capable Agent.")
    parser.add_argument("--imagine-url", default=os.environ.get("IMAGINE_URL"))
    parser.add_argument("--imagine-key", default=os.environ.get("IMAGINE_KEY"))
    parser.add_argument("--force-env", action="store_true", help="Overwrite existing .env")
    parser.add_argument("--no-deps", action="store_true", help="Skip pip install")
    args = parser.parse_args()

    python = ensure_python()
    print(f"Nook Image MCP root: {ROOT}")
    print(f"Python: {python}")

    if not args.no_deps:
        install_dependencies(python)
    create_env(args.imagine_url, args.imagine_key, args.force_env)
    verify_server(python)
    print_descriptor(python)
    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

