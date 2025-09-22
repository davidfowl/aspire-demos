"""Minimal Python MCP server for Aspire integration.

Run (stdio for local inspector):
  python main.py

Expose Streamable HTTP (recommended) using FastMCP's built-in runner:
  python main.py --transport streamable-http --port 8111

This server demonstrates:
 - Tools (echo, add)
 - Prompts
 - Resources (static text)
"""

from __future__ import annotations

import os
import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="PyMcpServer",
    instructions=(
        f"Python MCP server providing echo, math, time utilities and a sample resource. "
    ),
    debug=True,
    port=os.environ.get("PORT"),
)


# -----------------
# Tools
# -----------------
@mcp.tool()
def echo(message: str) -> str:
    """Echo the provided message."""
    return message


@mcp.tool()
def add(a: float, b: float) -> dict[str, float]:
    """Add two numbers and return the sum."""
    return {"a": a, "b": b, "sum": a + b}


@mcp.tool()
def now() -> dict[str, Any]:
    """Return current UTC time info."""
    dt = datetime.datetime.utcnow()
    return {"iso": dt.isoformat() + "Z", "epoch": dt.timestamp()}


# -----------------
# Resources
# -----------------
@mcp.resource("pymcp://welcome")
def welcome_resource() -> str:
    return "Welcome to the Python MCP server. Use tools: echo, add, now."


# -----------------
# Prompts
# -----------------
@mcp.prompt()
def greeting(name: str) -> list[dict[str, str]]:  # FastMCP prompt format
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Say hello to {name}."},
    ]


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
