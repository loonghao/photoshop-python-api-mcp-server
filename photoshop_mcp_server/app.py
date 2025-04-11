"""Application configuration for Photoshop MCP Server."""

# Import third-party modules
import importlib.metadata

# Constants
APP_NAME = "photoshop_mcp_server"
APP_DESCRIPTION = "MCP Server for Photoshop integration using photoshop-python-api"

# Get version from package metadata
try:
    __version__ = importlib.metadata.version("photoshop-mcp-server")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0"  # Default version if package is not installed
