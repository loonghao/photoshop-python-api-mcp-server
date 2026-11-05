"""Tests for the ``execute_jsx_file`` tool."""

import asyncio
import json

import pytest

import photoshop_mcp_server.tools.script_tools as script_tools
from photoshop_mcp_server import registry
from photoshop_mcp_server.server import create_server


@pytest.fixture
def clean_registry():
    """Reset the module registration cache so tools are registered again."""
    saved = set(registry._registered_modules)
    registry._registered_modules.clear()
    try:
        yield
    finally:
        registry._registered_modules.clear()
        registry._registered_modules.update(saved)


class FakePhotoshopApp:
    """Stand-in for ``PhotoshopApp`` that returns a canned script payload."""

    def __init__(self, result):
        self._result = result
        self.scripts = []

    def execute_javascript(self, script):
        self.scripts.append(script)
        return self._result


def _call(monkeypatch, app_factory, file_path):
    monkeypatch.setattr(script_tools, "PhotoshopApp", app_factory)
    server = create_server()
    content = asyncio.run(
        server.call_tool("photoshop_execute_jsx_file", {"file_path": str(file_path)})
    )
    return json.loads(content[0].text)


def test_execute_jsx_file_is_registered(clean_registry):
    """The tool is exposed under the ``photoshop`` namespace."""
    names = {tool.name for tool in asyncio.run(create_server().list_tools())}

    assert "photoshop_execute_jsx_file" in names


def test_missing_file_is_reported_without_contacting_photoshop(
    clean_registry, monkeypatch, tmp_path
):
    """A path that does not exist fails before Photoshop is reached."""

    def _unreachable():
        raise AssertionError("Photoshop must not be contacted")

    result = _call(monkeypatch, _unreachable, tmp_path / "missing.jsx")

    assert result["success"] is False
    assert "not found" in result["error"]


def test_script_output_is_returned(clean_registry, monkeypatch, tmp_path):
    """The evaluated file's result is returned with the resolved path."""
    jsx = tmp_path / "script.jsx"
    jsx.write_text("42;", encoding="utf-8")
    fake = FakePhotoshopApp("42")

    result = _call(monkeypatch, lambda: fake, jsx)

    assert result == {
        "success": True,
        "file_path": str(jsx.resolve()),
        "result": "42",
    }
    assert "$.evalFile" in fake.scripts[0]


def test_script_failure_is_reported_as_failure(clean_registry, monkeypatch, tmp_path):
    """A failure payload from the COM layer is surfaced, not wrapped."""
    jsx = tmp_path / "script.jsx"
    jsx.write_text("throw new Error('boom');", encoding="utf-8")

    result = _call(
        monkeypatch,
        lambda: FakePhotoshopApp('{"error": "boom", "success": false}'),
        jsx,
    )

    assert result == {
        "success": False,
        "file_path": str(jsx.resolve()),
        "error": "boom",
    }


def test_path_is_embedded_as_a_javascript_string_literal(
    clean_registry, monkeypatch, tmp_path
):
    """Backslashes, quotes and non-ASCII characters in the path stay intact."""
    folder = tmp_path / "it's ümlaut"
    folder.mkdir()
    jsx = folder / "script.jsx"
    jsx.write_text("1;", encoding="utf-8")
    fake = FakePhotoshopApp("1")

    _call(monkeypatch, lambda: fake, jsx)

    assert f"new File({json.dumps(str(jsx.resolve()))})" in fake.scripts[0]
