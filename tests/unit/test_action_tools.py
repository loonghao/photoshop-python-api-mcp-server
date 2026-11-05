"""Tests for the Actions panel tools."""

import asyncio
import json

import pytest

import photoshop_mcp_server.tools.action_tools as action_tools
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


def _call(monkeypatch, app_factory, tool, arguments=None):
    monkeypatch.setattr(action_tools, "PhotoshopApp", app_factory)
    server = create_server()
    content = asyncio.run(server.call_tool(tool, arguments or {}))
    return json.loads(content[0].text)


def test_action_tools_are_registered(clean_registry):
    """Both tools are exposed under the ``photoshop`` namespace."""
    names = {tool.name for tool in asyncio.run(create_server().list_tools())}

    assert {"photoshop_list_actions", "photoshop_play_action"} <= names


def test_list_actions_returns_action_sets(clean_registry, monkeypatch):
    """The JSON list built in Photoshop is returned as structured data."""
    sets = [{"name": "Default Actions", "count": 2, "actions": ["Vignette", "Frame"]}]

    result = _call(
        monkeypatch,
        lambda: FakePhotoshopApp(json.dumps(sets)),
        "photoshop_list_actions",
    )

    assert result == {"success": True, "action_sets": sets}


def test_list_actions_reports_unexpected_output(clean_registry, monkeypatch):
    """Output that is not a list of action sets is a failure."""
    result = _call(
        monkeypatch, lambda: FakePhotoshopApp("undefined"), "photoshop_list_actions"
    )

    assert result["success"] is False
    assert "Unexpected" in result["error"]


def test_list_actions_reports_unreachable_photoshop(clean_registry, monkeypatch):
    """A PhotoshopApp that cannot be constructed is reported, not raised."""

    def _explode():
        raise OSError("Photoshop is not available")

    result = _call(monkeypatch, _explode, "photoshop_list_actions")

    assert result == {"success": False, "error": "Photoshop is not available"}


def test_play_action_reports_success(clean_registry, monkeypatch):
    """A played action returns its names with ``success: true``."""
    fake = FakePhotoshopApp('{"played":true}')

    result = _call(
        monkeypatch,
        lambda: fake,
        "photoshop_play_action",
        {"action_name": "Vignette (selection)", "action_set": "Default Actions"},
    )

    assert result == {
        "success": True,
        "action_name": "Vignette (selection)",
        "action_set": "Default Actions",
    }
    assert 'app.doAction("Vignette (selection)", "Default Actions")' in fake.scripts[0]


def test_play_action_reports_photoshop_error(clean_registry, monkeypatch):
    """A multi-line Photoshop error payload is surfaced as a failure."""
    message = 'General Photoshop error.\n- The command "Play" is not available.'

    result = _call(
        monkeypatch,
        lambda: FakePhotoshopApp(json.dumps({"error": message, "success": False})),
        "photoshop_play_action",
        {"action_name": "missing", "action_set": "Default Actions"},
    )

    assert result == {
        "success": False,
        "action_name": "missing",
        "action_set": "Default Actions",
        "error": message,
    }


def test_play_action_escapes_names(clean_registry, monkeypatch):
    """Quotes and backslashes in names cannot break out of the string literal."""
    fake = FakePhotoshopApp('{"played":true}')
    name = 'say "hi" \\ bye'

    _call(
        monkeypatch,
        lambda: fake,
        "photoshop_play_action",
        {"action_name": name, "action_set": "Set"},
    )

    assert f"app.doAction({json.dumps(name)}, " in fake.scripts[0]
