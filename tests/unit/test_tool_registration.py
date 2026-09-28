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
import json
import pkgutil

import pytest
from mcp.server.fastmcp import FastMCP

import photoshop_mcp_server.tools as tools_package
import photoshop_mcp_server.tools.script_tools as script_tools
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


class FakePhotoshopApp:
    """Stand-in for ``PhotoshopApp`` that returns a canned script payload.

    Only ``execute_javascript`` is faked; every other layer (tool registration,
    the ``execute_jsx`` closure, FastMCP dispatch) is the real production code.
    """

    def __init__(self, result):
        self._result = result
        self.scripts = []

    def execute_javascript(self, script):
        self.scripts.append(script)
        return self._result


def _call_execute_jsx(monkeypatch, app_factory, script="app.activeDocument.name;"):
    """Run the registered ``execute_jsx`` tool against a fake host.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        app_factory: Callable returning the fake host (or raising).
        script: The JavaScript body to execute.

    Returns:
        dict: The decoded tool result.

    """
    monkeypatch.setattr(script_tools, "PhotoshopApp", app_factory)

    server = create_server()
    content = asyncio.run(server.call_tool("photoshop_execute_jsx", {"script": script}))

    # FastMCP serialises the dict return value as JSON text content.
    return json.loads(content[0].text)


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


class TestExecuteJsxFailureContract:
    """A failed script or an unreachable host must report ``success: false``.

    PhotoshopApp.execute_javascript never raises for a script that throws inside
    Photoshop: it returns the failure as a JSON string. Wrapping that string in
    ``{"success": true, "result": ...}`` would tell LLM callers the script worked
    and let the error string be consumed as if it were script output.
    """

    def test_script_failure_is_reported_as_failure(self, clean_registry, monkeypatch):
        """A failure payload from the COM layer is surfaced, not wrapped."""
        result = _call_execute_jsx(
            monkeypatch,
            lambda: FakePhotoshopApp('{"error": "boom", "success": false}'),
        )

        assert result == {"success": False, "error": "boom"}

    def test_unreachable_photoshop_returns_failure(self, clean_registry, monkeypatch):
        """A PhotoshopApp that cannot be constructed is reported, not raised."""

        def _explode():
            raise OSError("Photoshop is not available")

        result = _call_execute_jsx(monkeypatch, _explode)

        assert result == {
            "success": False,
            "error": "Photoshop is not available",
        }

    def test_successful_script_is_still_reported_as_success(
        self, clean_registry, monkeypatch
    ):
        """Ordinary script output keeps the success shape."""
        result = _call_execute_jsx(monkeypatch, lambda: FakePhotoshopApp("42"))

        assert result == {"success": True, "result": "42"}

    def test_error_keyed_json_output_is_not_mistaken_for_failure(
        self, clean_registry, monkeypatch
    ):
        """Script output that happens to contain an error key stays a success."""
        result = _call_execute_jsx(
            monkeypatch,
            lambda: FakePhotoshopApp('{"error": null, "success": true}'),
        )

        assert result == {"success": True, "result": '{"error": null, "success": true}'}
