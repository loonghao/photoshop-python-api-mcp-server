"""Resource registry for Photoshop MCP Server.

This module provides functions for dynamically registering resources with the MCP server.
"""

import importlib
import inspect
import pkgutil
from collections.abc import Callable

from loguru import logger
from mcp.server.fastmcp import FastMCP

# Set of modules that have been registered
_registered_modules: set[str] = set()


def register_resources_from_module(mcp_server: FastMCP, module_name: str) -> list[str]:
    """Register all resources from a module.

    Args:
        mcp_server: The MCP server instance.
        module_name: The name of the module to register resources from.

    Returns:
        List of registered resource names.

    """
    if module_name in _registered_modules:
        logger.debug(f"Module {module_name} already registered")
        return []

    try:
        module = importlib.import_module(module_name)
        registered_resources = []

        # Check if the module has a register function
        if hasattr(module, "register") and callable(module.register):
            logger.info(
                f"Registering resources from {module_name} using register() function"
            )
            module.register(mcp_server)
            _registered_modules.add(module_name)
            # We can't know what resources were registered, so return empty list
            return registered_resources

        # Otherwise, look for functions with @mcp.resource() decorator
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, "__mcp_resource__"):
                logger.info(f"Found MCP resource: {name}")
                registered_resources.append(name)

        _registered_modules.add(module_name)
        return registered_resources

    except ImportError as e:
        logger.error(f"Failed to import module {module_name}: {e}")
        return []


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
    registered_resources = {}

    try:
        package = importlib.import_module(package_name)

        # Skip __init__.py and registry.py
        skip_modules = {"__init__", "registry"}

        for _, module_name, is_pkg in pkgutil.iter_modules(
            package.__path__, package.__name__ + "."
        ):
            if module_name.split(".")[-1] in skip_modules:
                continue

            resources = register_resources_from_module(mcp_server, module_name)
            if resources:
                registered_resources[module_name] = resources

            # If it's a package, register all modules in it
            if is_pkg:
                sub_resources = register_all_resources(mcp_server, module_name)
                registered_resources.update(sub_resources)

    except ImportError as e:
        logger.error(f"Failed to import package {package_name}: {e}")

    return registered_resources


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
