"""Script execution MCP tools for Photoshop."""

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.registry import register_tool


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
                  or 'error' if execution failed.

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
        ps_app = PhotoshopApp()
        try:
            result = ps_app.execute_javascript(script)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    tool_name = register_tool(mcp, execute_jsx, "execute_jsx")
    return [tool_name]
