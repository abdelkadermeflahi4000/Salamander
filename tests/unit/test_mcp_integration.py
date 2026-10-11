"""
MCP integration tests.
Skipped until the MCP server module is stable and importable.
"""

from __future__ import annotations

import pytest

mcp_available = False
try:
    from salamander.integrations.mcp_server import app  # adjust path if needed
    mcp_available = True
except ImportError:
    try:
        from salamander.mcp_server import app
        mcp_available = True
    except ImportError:
        pass


pytestmark = pytest.mark.skipif(
    not mcp_available,
    reason="MCP server module not available yet"
)


def test_mcp_app_exists():
    assert app is not None


def test_scan_tool_exists():
    # Adjust according to how tools are registered in your MCP server
    tools = getattr(app, "tools", None) or getattr(app, "_tools", None)
    assert tools is not None
