"""Tool registry for Photoshop MCP Server.

This module provides functions for dynamically registering tools with the MCP server.
"""

import importlib
import inspect
import pkgutil
from collections.abc import Callable

from loguru import logger
from mcp.server.fastmcp import FastMCP

# Set of modules that have been registered
_registered_modules: set[str] = set()


def register_tools_from_module(mcp_server: FastMCP, module_name: str) -> list[str]:
    """Register all tools from a module.

    Args:
        mcp_server: The MCP server instance.
        module_name: The name of the module to register tools from.

    Returns:
        List of registered tool names.

    """
    if module_name in _registered_modules:
        logger.debug(f"Module {module_name} already registered")
        return []

    try:
        module = importlib.import_module(module_name)
        registered_tools = []

        # Check if the module has a register function
        if hasattr(module, "register") and callable(module.register):
            logger.info(
                f"Registering tools from {module_name} using register() function"
            )
            module.register(mcp_server)
            _registered_modules.add(module_name)
            # We can't know what tools were registered, so return empty list
            return registered_tools

        # Otherwise, look for functions with @mcp.tool() decorator
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, "__mcp_tool__"):
                logger.info(f"Found MCP tool: {name}")
                registered_tools.append(name)

        _registered_modules.add(module_name)
        return registered_tools

    except ImportError as e:
        logger.error(f"Failed to import module {module_name}: {e}")
        return []


def register_all_tools(
    mcp_server: FastMCP, package_name: str = "photoshop_mcp_server.tools"
) -> dict[str, list[str]]:
    """Register all tools from all modules in a package.

    Args:
        mcp_server: The MCP server instance.
        package_name: The name of the package to register tools from.

    Returns:
        Dictionary mapping module names to lists of registered tool names.

    """
    registered_tools = {}

    try:
        package = importlib.import_module(package_name)

        # Skip __init__.py and registry.py
        skip_modules = {"__init__", "registry"}

        for _, module_name, is_pkg in pkgutil.iter_modules(
            package.__path__, package.__name__ + "."
        ):
            if module_name.split(".")[-1] in skip_modules:
                continue

            tools = register_tools_from_module(mcp_server, module_name)
            if tools:
                registered_tools[module_name] = tools

            # If it's a package, register all modules in it
            if is_pkg:
                sub_tools = register_all_tools(mcp_server, module_name)
                registered_tools.update(sub_tools)

    except ImportError as e:
        logger.error(f"Failed to import package {package_name}: {e}")

    return registered_tools


def register_tool(mcp_server: FastMCP, func: Callable, name: str | None = None) -> str:
    """Register a function as an MCP tool.

    Args:
        mcp_server: The MCP server instance.
        func: The function to register.
        name: Optional name for the tool. If not provided, the function name is used.

    Returns:
        The name of the registered tool.

    """
    tool_name = name or func.__name__
    mcp_server.tool(name=tool_name)(func)
    logger.info(f"Registered tool: {tool_name}")
    return tool_name
