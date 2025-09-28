from __future__ import annotations

import os
import datetime
import logging
from typing import Any, Callable, Mapping

from mcp.server.fastmcp import FastMCP
from opentelemetry import trace, metrics
from opentelemetry.context import Context

# Explicit tracer & meter (manual instrumentation since auto-instrumentation not in use)
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

import functools


def with_span(name: str | None = None, attr_fn: Callable[..., Mapping[str, Any]] | None = None):
    """Decorator to wrap a function call in a new span.

    Parameters:
        name: Optional explicit span name (defaults to function __name__).
        attr_fn: Optional callable receiving the original *args/**kwargs and returning
                 a mapping of initial span attributes.
    Usage:
        @mcp.tool()
        @with_span("tool.echo", attr_fn=lambda message: {"tool.name": "echo", "message.length": len(message)})
        def echo(message: str) -> str:
            ...
    """
    def decorator(fn):
        span_name = name or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Start a ROOT span (no parent) by supplying a fresh empty Context()
            with tracer.start_as_current_span(span_name, context=Context()) as span:
                if attr_fn:
                    try:
                        attrs = attr_fn(*args, **kwargs) or {}
                        for k, v in attrs.items():
                            span.set_attribute(k, v)
                    except Exception as exc:  # defensive: don't break tool on attr errors
                        logger.warning("attr_fn for %s raised %s", span_name, exc)
                return fn(*args, **kwargs)
        return wrapper
    return decorator

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
@with_span("tool.echo", attr_fn=lambda message: {"tool.name": "echo", "message.length": len(message)})
def echo(message: str) -> str:
    """Echo the provided message."""
    tool_invocation_counter.add(1, {"tool": "echo"})
    logger.info(f"Echo tool invoked with message: {message[:50]}...")
    return message


@mcp.tool()
@with_span("tool.add", attr_fn=lambda a, b: {"tool.name": "add", "operand.a": a, "operand.b": b})
def add(a: float, b: float) -> dict[str, float]:
    """Add two numbers and return the sum."""
    result = a + b
    trace.get_current_span().set_attribute("result", result)
    tool_invocation_counter.add(1, {"tool": "add"})
    logger.info(f"Add tool invoked: {a} + {b} = {result}")
    return {"a": a, "b": b, "sum": result}


@mcp.tool()
def now() -> dict[str, Any]:
    """Return current UTC time info."""
    # Need dynamic attributes computed inside span; use manual span here for clarity.
    # Root span for this tool invocation
    with tracer.start_as_current_span("tool.now", context=Context()) as span:
        dt = datetime.datetime.utcnow()
        result = {"iso": dt.isoformat() + "Z", "epoch": dt.timestamp()}
        span.set_attribute("tool.name", "now")
        span.set_attribute("timestamp.iso", result["iso"])
        span.set_attribute("timestamp.epoch", result["epoch"])
        tool_invocation_counter.add(1, {"tool": "now"})
        logger.info(f"Now tool invoked: {result['iso']}")
        return result


# -----------------
# Resources
# -----------------
@mcp.resource("pymcp://welcome")
@with_span("resource.welcome", attr_fn=lambda: {"resource.uri": "pymcp://welcome"})
def welcome_resource() -> str:
    logger.info("Welcome resource accessed")
    return "Welcome to the Python MCP server. Use tools: echo, add, now."


# -----------------
# Prompts
# -----------------
@mcp.prompt()
@with_span("prompt.greeting", attr_fn=lambda name: {"prompt.name": "greeting", "user.name": name})
def greeting(name: str) -> list[dict[str, str]]:  # FastMCP prompt format
    logger.info(f"Greeting prompt invoked for: {name}")
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Say hello to {name}."},
    ]


def main() -> None:
    logger.info("Starting PyMCP Server with OpenTelemetry instrumentation (manual spans)")
    logger.info(f"OTEL_EXPORTER_OTLP_ENDPOINT: {os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT', 'Not set')}")
    logger.info(f"OTEL_SERVICE_NAME: {os.environ.get('OTEL_SERVICE_NAME', 'Not set')}")

    # Root span for server startup
    with tracer.start_as_current_span("server.startup", context=Context()) as span:
        span.set_attribute("server.name", "PyMcpServer")
        span.set_attribute("server.transport", "streamable-http")
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
