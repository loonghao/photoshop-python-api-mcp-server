"""Session-related MCP tools for Photoshop."""

from typing import Any

from photoshop_mcp_server.ps_adapter.action_manager import ActionManager
from photoshop_mcp_server.registry import register_tool


def register(mcp):
    """Register session-related tools.

    Args:
        mcp: The MCP server instance.

    Returns:
        list: List of registered tool names.

    """
    registered_tools = []

    def get_session_info() -> dict[str, Any]:
        """Get information about the current Photoshop session.

        Returns:
            dict: Information about the current Photoshop session.

        """
        try:
            print("Getting Photoshop session information using Action Manager")

            # Use Action Manager to get session info
            session_info = ActionManager.get_session_info()
            print(
                f"Session info retrieved successfully: {session_info.get('success', False)}"
            )

            return session_info

        except Exception as e:
            print(f"Error getting Photoshop session info: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            # Create a detailed error message
            detailed_error = f"Error getting Photoshop session information:\nError: {e!s}\n\nTraceback:\n{tb_text}"

            return {
                "success": False,
                "is_running": False,
                "error": str(e),
                "detailed_error": detailed_error,
            }

    # Register the get_session_info function with a specific name
    tool_name = register_tool(mcp, get_session_info, "get_session_info")
    registered_tools.append(tool_name)

    def get_active_document_info() -> dict[str, Any]:
        """Get detailed information about the active document.

        Returns:
            dict: Detailed information about the active document or an error message.

        """
        try:
            print("Getting active document information using Action Manager")

            # Use Action Manager to get document info
            doc_info = ActionManager.get_active_document_info()
            print(
                f"Document info retrieved successfully: {doc_info.get('success', False)}"
            )

            return doc_info

        except Exception as e:
            print(f"Error getting active document info: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            # Create a detailed error message
            detailed_error = f"Error getting active document information:\nError: {e!s}\n\nTraceback:\n{tb_text}"

            return {"success": False, "error": str(e), "detailed_error": detailed_error}

    # Register the get_active_document_info function with a specific name
    tool_name = register_tool(mcp, get_active_document_info, "get_active_document_info")
    registered_tools.append(tool_name)

    def get_selection_info() -> dict[str, Any]:
        """Get information about the current selection in the active document.

        Returns:
            dict: Information about the current selection or an error message.

        """
        try:
            print("Getting selection information using Action Manager")

            # Use Action Manager to get selection info
            selection_info = ActionManager.get_selection_info()
            print(
                f"Selection info retrieved successfully: {selection_info.get('success', False)}"
            )

            return selection_info

        except Exception as e:
            print(f"Error getting selection info: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            # Create a detailed error message
            detailed_error = f"Error getting selection information:\nError: {e!s}\n\nTraceback:\n{tb_text}"

            return {
                "success": False,
                "has_selection": False,
                "error": str(e),
                "detailed_error": detailed_error,
            }

    # Register the get_selection_info function with a specific name
    tool_name = register_tool(mcp, get_selection_info, "get_selection_info")
    registered_tools.append(tool_name)

    return registered_tools
