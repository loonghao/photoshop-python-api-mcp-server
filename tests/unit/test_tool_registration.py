"""Tests for tool registration consistency.

Tool modules are discovered dynamically with ``pkgutil.iter_modules``, but the
package ``__init__.py`` also imports them explicitly. Those two paths can drift:
a module that is discovered but never imported in ``__init__.py`` still works
today (discovery imports it on demand) while silently diverging from the
explicit ``__all__`` contract. These tests lock both halves together so a new
tool module cannot be registered without being declared, and so
``execute_jsx`` cannot silently disappear from the server surface again.
"""

import asyncio
import importlib
import pkgutil

import pytest
from mcp.server.fastmcp import FastMCP

import photoshop_mcp_server.tools as tools_package
from photoshop_mcp_server import registry
from photoshop_mcp_server.server import create_server

# Modules that live in the tools package but do not expose tools themselves.
NON_TOOL_MODULES = {"__init__", "registry"}


def _discovered_tool_modules():
    """Return the short names of every tool module found by package discovery."""
    return {
        module_name.split(".")[-1]
        for _, module_name, is_pkg in pkgutil.iter_modules(
            tools_package.__path__, tools_package.__name__ + "."
        )
        if not is_pkg
    } - NON_TOOL_MODULES


@pytest.fixture
def clean_registry():
    """Reset the module registration cache so tools are registered again.

    ``registry._registered_modules`` is process-global, so without this reset a
    second ``create_server()`` call in the same pytest session would skip every
    module and expose no tools at all.
    """
    saved = set(registry._registered_modules)
    registry._registered_modules.clear()
    try:
        yield
    finally:
        registry._registered_modules.clear()
        registry._registered_modules.update(saved)


def _list_tool_names(server):
    """Return the set of tool names exposed by a FastMCP server."""
    return {tool.name for tool in asyncio.run(server.list_tools())}


class TestToolModuleConsistency:
    """The package ``__init__`` must import every discoverable tool module."""

    def test_init_imports_every_tool_module(self):
        """Every module found by discovery is imported in ``tools/__init__``."""
        assert _discovered_tool_modules() == set(tools_package.__all__)

    def test_every_declared_module_is_importable_and_has_register(self):
        """Every declared module imports and exposes a callable ``register``."""
        for module_short_name in tools_package.__all__:
            module = importlib.import_module(
                f"{tools_package.__name__}.{module_short_name}"
            )
            assert callable(getattr(module, "register", None)), (
                f"{module_short_name} has no callable register()"
            )

    def test_script_tools_is_declared(self):
        """``script_tools`` (which provides ``execute_jsx``) is not dropped again."""
        assert "script_tools" in tools_package.__all__
        assert "script_tools" in _discovered_tool_modules()


class TestRegisteredToolSurface:
    """A freshly created server must expose the documented tools."""

    def test_execute_jsx_is_registered(self, clean_registry):
        """``execute_jsx`` shows up under the ``photoshop`` namespace."""
        server = create_server()

        assert isinstance(server, FastMCP)
        assert "photoshop_execute_jsx" in _list_tool_names(server)

    def test_execute_jsx_describes_javascript_execution(self, clean_registry):
        """The registered tool keeps a JSX/JavaScript description for MCP clients."""
        server = create_server()
        tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

        execute_jsx = tools["photoshop_execute_jsx"]
        description = (execute_jsx.description or "").lower()
        assert "javascript" in description or "jsx" in description

    def test_baseline_tools_are_still_registered(self, clean_registry):
        """Document/layer/session tools are not lost when script tools are added."""
        tool_names = _list_tool_names(create_server())

        assert {
            "photoshop_create_document",
            "photoshop_save_document",
            "photoshop_create_text_layer",
            "photoshop_get_session_info",
            "photoshop_execute_jsx",
        } <= tool_names
