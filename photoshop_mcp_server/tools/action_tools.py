"""Photoshop Actions panel MCP tools."""

import json

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.registry import register_tool

_LIST_ACTIONS_JSX = """
(function () {
    var result = [];
    var setIndex = 1;
    while (true) {
        var ref = new ActionReference();
        ref.putIndex(charIDToTypeID("ASet"), setIndex);
        var desc;
        try {
            desc = executeActionGet(ref);
        } catch (e) {
            break;
        }
        var setName = desc.getString(charIDToTypeID("Nm  "));
        var count = desc.hasKey(charIDToTypeID("NmbC"))
            ? desc.getInteger(charIDToTypeID("NmbC"))
            : 0;
        var actions = [];
        for (var j = 1; j <= count; j++) {
            var aref = new ActionReference();
            aref.putIndex(charIDToTypeID("Actn"), j);
            aref.putIndex(charIDToTypeID("ASet"), setIndex);
            try {
                var adesc = executeActionGet(aref);
                actions.push(adesc.getString(charIDToTypeID("Nm  ")));
            } catch (e2) {}
        }
        result.push({name: setName, count: count, actions: actions});
        setIndex++;
    }
    return JSON.stringify(result);
})()
"""


def _parse_payload(raw):
    """Decode a JSON payload returned by ``execute_javascript``.

    Args:
        raw: The raw value returned by ``execute_javascript``.

    Returns:
        The decoded JSON value, or ``raw`` unchanged when it is not JSON.

    """
    if not isinstance(raw, str):
        return raw
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def _failure(payload):
    """Return the error message of a ``success: false`` payload, else ``None``."""
    if isinstance(payload, dict) and payload.get("success") is False:
        return str(payload.get("error") or "Script execution failed")
    return None


def register(mcp):
    """Register Photoshop action tools.

    Args:
        mcp: The MCP server instance.

    Returns:
        list: List of registered tool names.

    """
    registered_tools = []

    def list_actions() -> dict:
        """List all loaded action sets and the actions in each set.

        Use this before play_action to learn the exact action and set names.

        Returns:
            dict: 'success' flag and 'action_sets', a list of
                {name, count, actions} objects, or 'error'.

        """
        try:
            ps_app = PhotoshopApp()
            payload = _parse_payload(ps_app.execute_javascript(_LIST_ACTIONS_JSX))
        except Exception as e:
            return {"success": False, "error": str(e)}

        error_message = _failure(payload)
        if error_message is not None:
            return {"success": False, "error": error_message}
        if not isinstance(payload, list):
            return {
                "success": False,
                "error": f"Unexpected list_actions result: {payload!r}",
            }
        return {"success": True, "action_sets": payload}

    registered_tools.append(register_tool(mcp, list_actions, "list_actions"))

    def play_action(action_name: str, action_set: str) -> dict:
        """Play an action from a loaded action set.

        Dialogs are suppressed while the action runs.

        Args:
            action_name: Exact action name as shown in the Actions panel.
            action_set: Exact name of the action set that contains it.

        Returns:
            dict: 'success' flag, 'action_name' and 'action_set', or 'error'.

        """
        script = (
            "(function () {"
            "app.displayDialogs = DialogModes.NO;"
            "app.playbackDisplayDialogs = DialogModes.NO;"
            f"app.doAction({json.dumps(action_name)}, {json.dumps(action_set)});"
            "return JSON.stringify({played: true});"
            "})()"
        )
        result = {"action_name": action_name, "action_set": action_set}
        try:
            ps_app = PhotoshopApp()
            payload = _parse_payload(ps_app.execute_javascript(script))
        except Exception as e:
            return {"success": False, **result, "error": str(e)}

        error_message = _failure(payload)
        if error_message is not None:
            return {"success": False, **result, "error": error_message}
        return {"success": True, **result}

    registered_tools.append(register_tool(mcp, play_action, "play_action"))

    return registered_tools
