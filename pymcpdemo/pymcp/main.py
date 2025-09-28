"""Minimal Python MCP server for Aspire integration.

Run (stdio for local inspector):
  python main.py

Expose Streamable HTTP (recommended) using FastMCP's built-in runner:
  python main.py --transport streamable-http --port 8111

This server demonstrates:
 - Tools (echo, add)
 - Prompts
 - Resources (static text)
 - OpenTelemetry instrumentation with OTLP export
"""

from __future__ import annotations

import os
import datetime
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from opentelemetry import trace, metrics

# Get tracer and meter - let Aspire handle the provider setup
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create some custom metrics
tool_invocation_counter = meter.create_counter(
    name="mcp_tool_invocations_total",
    description="Total number of tool invocations",
    unit="1"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="PyMcpServer",
    instructions=(
        f"Python MCP server providing echo, math, time utilities and a sample resource. "
        f"Instrumented with OpenTelemetry for observability."
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
    with tracer.start_as_current_span("echo_tool") as span:
        span.set_attribute("message.length", len(message))
        span.set_attribute("tool.name", "echo")
        tool_invocation_counter.add(1, {"tool": "echo"})
        logger.info(f"Echo tool invoked with message: {message[:50]}...")
        return message


@mcp.tool()
def add(a: float, b: float) -> dict[str, float]:
    """Add two numbers and return the sum."""
    with tracer.start_as_current_span("add_tool") as span:
        span.set_attribute("operand.a", a)
        span.set_attribute("operand.b", b)
        span.set_attribute("tool.name", "add")
        result = a + b
        span.set_attribute("result", result)
        tool_invocation_counter.add(1, {"tool": "add"})
        logger.info(f"Add tool invoked: {a} + {b} = {result}")
        return {"a": a, "b": b, "sum": result}


@mcp.tool()
def now() -> dict[str, Any]:
    """Return current UTC time info."""
    with tracer.start_as_current_span("now_tool") as span:
        span.set_attribute("tool.name", "now")
        dt = datetime.datetime.utcnow()
        result = {"iso": dt.isoformat() + "Z", "epoch": dt.timestamp()}
        span.set_attribute("timestamp.iso", result["iso"])
        span.set_attribute("timestamp.epoch", result["epoch"])
        tool_invocation_counter.add(1, {"tool": "now"})
        logger.info(f"Now tool invoked: {result['iso']}")
        return result


# -----------------
# Resources
# -----------------
@mcp.resource("pymcp://welcome")
def welcome_resource() -> str:
    with tracer.start_as_current_span("welcome_resource") as span:
        span.set_attribute("resource.uri", "pymcp://welcome")
        logger.info("Welcome resource accessed")
        return "Welcome to the Python MCP server. Use tools: echo, add, now."


# -----------------
# Prompts
# -----------------
@mcp.prompt()
def greeting(name: str) -> list[dict[str, str]]:  # FastMCP prompt format
    with tracer.start_as_current_span("greeting_prompt") as span:
        span.set_attribute("prompt.name", "greeting")
        span.set_attribute("user.name", name)
        logger.info(f"Greeting prompt invoked for: {name}")
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Say hello to {name}."},
        ]


def main() -> None:
    logger.info("Starting PyMCP Server with OpenTelemetry instrumentation")
    logger.info(f"OTEL_EXPORTER_OTLP_ENDPOINT: {os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT', 'Not set')}")
    logger.info(f"OTEL_SERVICE_NAME: {os.environ.get('OTEL_SERVICE_NAME', 'Not set')}")
    
    with tracer.start_as_current_span("server_startup") as span:
        span.set_attribute("server.name", "PyMcpServer")
        span.set_attribute("server.transport", "streamable-http")
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
