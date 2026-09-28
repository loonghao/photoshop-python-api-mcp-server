"""Script execution MCP tools for Photoshop."""

import json

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.registry import register_tool


def _script_error_message(result):
    r"""Return the failure message carried by a script payload, if any.

    ``PhotoshopApp.execute_javascript`` catches every COM failure and reports it
    as a JSON string such as ``{\"error\": \"...\", \"success\": false}`` instead of
    raising. Without this check the tool would wrap a failed script in
    ``{\"success\": true, ...}`` and hand the error string to the caller as if it
    were script output, so callers could not tell failure from success.

    Args:
        result: The raw value returned by ``execute_javascript``.

    Returns:
        str or None: The error message when the payload describes a failure,
            otherwise ``None``.

    """
    if not isinstance(result, str):
        return None

    try:
        payload = json.loads(result)
    except ValueError:
        # Not JSON at all, so it is ordinary script output.
        return None

    if not isinstance(payload, dict):
        return None

    succeeded = payload.get("success")
    error = payload.get("error")
    if succeeded is False or (error is not None and succeeded is None):
        return str(error) if error else "Script execution failed"

    return None


def register(mcp):
    """Register script execution tools.

    Args:
        mcp: The MCP server instance.

    """

    def execute_jsx(script: str) -> dict:
        """Execute JavaScript (JSX) code in Photoshop.

        This is a universal tool that can run any Photoshop JavaScript code,
        giving access to the full Photoshop API including operations not covered
        by other dedicated tools.

        A JSON.stringify polyfill is automatically injected since Photoshop's
        ExtendScript engine is based on ECMAScript 3 which lacks native JSON.

        Args:
            script: JavaScript/JSX code to execute in Photoshop.
                    The script should return a value (string, number, or JSON string).
                    If no return statement is present, the last expression is returned.

        Returns:
            dict: Result containing 'success' flag and 'result' with the script output,
                  or 'error' if execution failed. A script that throws inside
                  Photoshop, and a Photoshop instance that cannot be reached at
                  all, both report ``success: false``.

        Examples:
            Get layer count:
                script: "app.activeDocument.artLayers.length;"

            Get all layer names as JSON:
                script: '''
                var doc = app.activeDocument;
                var names = [];
                for (var i = 0; i < doc.artLayers.length; i++) {
                    names.push(doc.artLayers[i].name);
                }
                JSON.stringify(names);
                '''

            Create a rectangle shape:
                script: '''
                var doc = app.activeDocument;
                var layer = doc.artLayers.add();
                layer.name = "Rectangle";
                var selection = doc.selection;
                selection.select([[100,100],[500,100],[500,400],[100,400]]);
                selection.fill(app.foregroundColor);
                selection.deselect();
                "done";
                '''

        """
        try:
            # Constructing PhotoshopApp() talks to Photoshop over COM, so it has
            # to be inside the try as well or an unreachable host escapes as an
            # unhandled exception instead of a reported failure.
            ps_app = PhotoshopApp()
            result = ps_app.execute_javascript(script)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

        # A script that throws does not raise here: execute_javascript() reports
        # it as a JSON payload, so surface that payload as a tool-level failure.
        error_message = _script_error_message(result)
        if error_message is not None:
            return {
                "success": False,
                "error": error_message,
            }

        return {
            "success": True,
            "result": result,
        }

    tool_name = register_tool(mcp, execute_jsx, "execute_jsx")
    return [tool_name]
