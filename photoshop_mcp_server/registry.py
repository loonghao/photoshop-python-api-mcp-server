"""Registry module for Photoshop MCP Server.

This module provides functions for dynamically registering tools and resources with the MCP server.
"""

import importlib
import inspect
import pkgutil
from collections.abc import Callable
from typing import Literal

from loguru import logger
from mcp.server.fastmcp import FastMCP

from photoshop_mcp_server.decorators import debug_tool, log_tool_call

# Set of modules that have been registered
_registered_modules: set[str] = set()


def register_from_module(
    mcp_server: FastMCP, module_name: str, registry_type: Literal["tool", "resource"]
) -> list[str]:
    """Register all tools or resources from a module.

    Args:
        mcp_server: The MCP server instance.
        module_name: The name of the module to register from.
        registry_type: The type of registry ("tool" or "resource").

    Returns:
        List of registered item names.

    """
    registry_key = f"{registry_type}:{module_name}"
    if registry_key in _registered_modules:
        logger.debug(f"Module {module_name} already registered for {registry_type}")
        return []

    try:
        module = importlib.import_module(module_name)
        registered_items = []

        # Check if the module has a register function
        if hasattr(module, "register") and callable(module.register):
            logger.info(
                f"Registering {registry_type}s from {module_name} using register() function"
            )
            module.register(mcp_server)
            _registered_modules.add(registry_key)
            # We can't know what items were registered, so return empty list
            return registered_items

        # Otherwise, look for functions with appropriate decorator
        attr_name = f"__mcp_{registry_type}__"
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, attr_name):
                logger.info(f"Found MCP {registry_type}: {name}")
                registered_items.append(name)

        _registered_modules.add(registry_key)
        return registered_items

    except ImportError as e:
        logger.error(f"Failed to import module {module_name}: {e}")
        return []


def register_all(
    mcp_server: FastMCP, package_name: str, registry_type: Literal["tool", "resource"]
) -> dict[str, list[str]]:
    """Register all tools or resources from all modules in a package.

    Args:
        mcp_server: The MCP server instance.
        package_name: The name of the package to register from.
        registry_type: The type of registry ("tool" or "resource").

    Returns:
        Dictionary mapping module names to lists of registered item names.

    """
    registered_items = {}

    try:
        package = importlib.import_module(package_name)

        # Skip __init__.py and registry.py
        skip_modules = {"__init__", "registry"}

        for _, module_name, is_pkg in pkgutil.iter_modules(
            package.__path__, package.__name__ + "."
        ):
            if module_name.split(".")[-1] in skip_modules:
                continue

            items = register_from_module(mcp_server, module_name, registry_type)
            if items:
                registered_items[module_name] = items

            # If it's a package, register all modules in it
            if is_pkg:
                sub_items = register_all(mcp_server, module_name, registry_type)
                registered_items.update(sub_items)

    except ImportError as e:
        logger.error(f"Failed to import package {package_name}: {e}")

    return registered_items


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
    return register_all(mcp_server, package_name, "tool")


def register_all_resources(
    mcp_server: FastMCP, package_name: str = "photoshop_mcp_server.resources"
) -> dict[str, list[str]]:
    """Register all resources from all modules in a package.

    Args:
        mcp_server: The MCP server instance.
        package_name: The name of the package to register resources from.

    Returns:
        Dictionary mapping module names to lists of registered resource names.

    """
    return register_all(mcp_server, package_name, "resource")


def register_tool(mcp_server: FastMCP, func: Callable, name: str | None = None, namespace: str = "photoshop", debug: bool = True) -> str:
    """Register a function as an MCP tool.

    Args:
        mcp_server: The MCP server instance.
        func: The function to register.
        name: Optional name for the tool. If not provided, the function name is used.
        namespace: Namespace prefix for the tool name. Default is "photoshop".
        debug: Whether to wrap the function with debug_tool decorator. Default is True.

    Returns:
        The name of the registered tool.

    """
    base_name = name or func.__name__

    # Add namespace prefix if not already present
    if namespace and not base_name.startswith(f"{namespace}_"):
        tool_name = f"{namespace}_{base_name}"
    else:
        tool_name = base_name

    # Apply decorators
    if debug:
        # Apply debug_tool decorator to capture detailed error information
        decorated_func = debug_tool(func)
        # Apply log_tool_call decorator to log function calls and results
        decorated_func = log_tool_call(decorated_func)
    else:
        decorated_func = func

    mcp_server.tool(name=tool_name)(decorated_func)
    logger.info(f"Registered tool: {tool_name}")
    return tool_name


def register_resource(mcp_server: FastMCP, func: Callable, path: str) -> str:
    """Register a function as an MCP resource.

    Args:
        mcp_server: The MCP server instance.
        func: The function to register.
        path: The resource path.

    Returns:
        The path of the registered resource.

    """
    mcp_server.resource(path)(func)
    logger.info(f"Registered resource: {path}")
    return path
