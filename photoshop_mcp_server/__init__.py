"""Photoshop MCP Server package."""

# Import local modules
from photoshop_mcp_server.app import __version__

# Import tools and resources for easier access
from photoshop_mcp_server.ps_adapter.application import PhotoshopApp

__all__ = [
    "PhotoshopApp",
    "__version__",
]
