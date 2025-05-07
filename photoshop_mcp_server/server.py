"""Photoshop MCP Server main module."""

import logging
import os
import sys
from typing import Any, Dict, Optional, Union

from mcp.server.fastmcp import FastMCP

# Import version
from photoshop_mcp_server.app import __version__

# Import registry
from photoshop_mcp_server.registry import register_all_resources, register_all_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("photoshop-mcp-server")


def create_server(
    name: str = "Photoshop",
    description: str = "Control Adobe Photoshop using MCP",
    version: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> FastMCP:
    """Create and configure the MCP server.

    Args:
        name: The name of the MCP server.
        description: A description of the server's functionality.
        version: The server version (defaults to package version).
        config: Additional configuration options.

    Returns:
        FastMCP: The configured MCP server.

    """
    # Use provided version or fall back to package version
    server_version = version or __version__

    # Create a new MCP server with the provided configuration
    from mcp.server.fastmcp import FastMCP

    server_mcp = FastMCP(name=name, description=description, version=server_version)

    # Register all resources dynamically
    logger.info("Registering resources...")
    registered_resources = register_all_resources(server_mcp)
    logger.info(
        f"Registered resources from modules: {list(registered_resources.keys())}"
    )

    # Register all tools dynamically
    logger.info("Registering tools...")
    registered_tools = register_all_tools(server_mcp)
    logger.info(f"Registered tools from modules: {list(registered_tools.keys())}")

    # Apply additional configuration if provided
    if config:
        logger.info(f"Applying additional configuration: {config}")
        # Example: Set environment variables
        if "env_vars" in config:
            for key, value in config["env_vars"].items():
                os.environ[key] = str(value)

    logger.info(f"Server '{name}' v{server_version} configured successfully")
    return server_mcp


def main():
    """Run the main entry point for the server.

    This function parses command-line arguments and starts the MCP server.
    It can be invoked directly or through the 'ps-mcp' entry point.

    Command-line arguments:
        --name: Server name (default: "Photoshop")
        --description: Server description
        --version: Server version (overrides package version)
        --debug: Enable debug logging
    """
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Photoshop MCP Server")
    parser.add_argument("--name", default="Photoshop", help="Server name")
    parser.add_argument(
        "--description",
        default="Control Adobe Photoshop using MCP",
        help="Server description",
    )
    parser.add_argument("--version", help="Server version (overrides package version)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    logger.info(f"Starting Photoshop MCP Server v{args.version or __version__}...")

    try:
        # Configure and run the server with command-line arguments
        server_mcp = create_server(
            name=args.name, description=args.description, version=args.version
        )
        server_mcp.run()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
