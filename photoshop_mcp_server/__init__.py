# -*- coding: utf-8 -*-
"""Photoshop MCP Server package."""

# Import local modules
from photoshop_mcp_server.app import mcp, __version__

# Import tools and resources for easier access
from photoshop_mcp_server.ps_adapter.application import PhotoshopApp

__all__ = [
    "__version__",
    "mcp",
    "PhotoshopApp",
]
