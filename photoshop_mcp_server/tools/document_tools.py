"""Document-related MCP tools."""

import traceback

import photoshop.api as ps

from photoshop_mcp_server.logging_config import get_logger
from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.ps_adapter.utils import UNCONVERTIBLE, try_float
from photoshop_mcp_server.registry import register_tool

logger = get_logger(__name__)


def register(mcp):
    """Register document-related tools.

    Args:
        mcp: The MCP server instance.

    Returns:
        list: List of registered tool names.

    """
    registered_tools = []

    def create_document(
        width: int = 1000, height: int = 1000, name: str = "Untitled", mode: str = "rgb"
    ) -> dict:
        """Create a new document in Photoshop.

        Args:
            width: Document width in pixels.
            height: Document height in pixels.
            name: Document name.
            mode: Color mode (rgb, cmyk, etc.). Defaults to "rgb".

        Returns:
            dict: Result of the operation.

        """
        logger.debug(
            "Creating document: width=%s, height=%s, name=%s, mode=%s",
            width,
            height,
            name,
            mode,
        )
        ps_app = PhotoshopApp()
        try:
            # Validate mode parameter
            valid_modes = ["rgb", "cmyk", "grayscale", "gray", "bitmap", "lab"]
            if mode.lower() not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid mode: {mode}. Valid modes are: {', '.join(valid_modes)}",
                    "detailed_error": (
                        f"Invalid color mode: {mode}\n\n"
                        f"Valid modes are: {', '.join(valid_modes)}\n\n"
                        f"The mode parameter specifies the color mode of the new document. "
                        f"It must be one of the valid modes listed above."
                    ),
                }

            # Create document
            logger.debug(
                "Calling ps_app.create_document with width=%s, height=%s, name=%s, mode=%s",
                width,
                height,
                name,
                mode,
            )
            doc = ps_app.create_document(
                width=width, height=height, name=name, mode=mode
            )

            if not doc:
                return {
                    "success": False,
                    "error": "Failed to create document - returned None",
                }

            # Get document properties safely
            try:
                logger.debug("Document created, getting properties")
                doc_name = doc.name
                logger.debug("Document name: %s", doc_name)

                # `doc.width` / `doc.height` are either a UnitValue (with `.value`)
                # or a plain float depending on the Photoshop build. When either
                # cannot be read we fall back to the requested size but flag the
                # payload as `dimensions_unavailable`, so a client can tell a
                # confirmed measurement apart from the size it merely asked for.
                doc_width = try_float(getattr(doc, "width", None))
                doc_height = try_float(getattr(doc, "height", None))
                dimensions_unavailable = (
                    doc_width is UNCONVERTIBLE or doc_height is UNCONVERTIBLE
                )
                logger.debug(
                    "Document dimensions: width=%s, height=%s (unavailable=%s)",
                    doc_width,
                    doc_height,
                    dimensions_unavailable,
                )

                result = {
                    "success": True,
                    "document_name": doc_name,
                    "width": float(width) if doc_width is UNCONVERTIBLE else doc_width,
                    "height": (
                        float(height) if doc_height is UNCONVERTIBLE else doc_height
                    ),
                }
                if dimensions_unavailable:
                    result["dimensions_unavailable"] = True

                return result
            except Exception as prop_error:
                logger.warning("Error getting document properties: %s", prop_error)
                logger.debug(traceback.format_exc())
                # Document was created but we couldn't get properties, so the
                # reported size is only what was requested - never confirmed.
                return {
                    "success": True,
                    "document_name": name,
                    "width": width,
                    "height": height,
                    "dimensions_unavailable": True,
                    "warning": f"Created document but couldn't get properties: {prop_error!s}",
                }
        except Exception as e:
            logger.error("Error creating document: %s", e)

            tb_text = traceback.format_exc()
            logger.debug(tb_text)

            # Create a detailed error message
            detailed_error = (
                f"Error creating document with parameters:\n"
                f"  width: {width}\n"
                f"  height: {height}\n"
                f"  name: {name}\n"
                f"  mode: {mode}\n\n"
                f"Error: {e!s}\n\n"
                f"Traceback:\n{tb_text}"
            )

            return {
                "success": False,
                "error": str(e),
                "detailed_error": detailed_error,
                "parameters": {
                    "width": width,
                    "height": height,
                    "name": name,
                    "mode": mode,
                },
            }

    # Register the create_document function with a specific name
    tool_name = register_tool(mcp, create_document, "create_document")
    registered_tools.append(tool_name)

    def open_document(file_path: str) -> dict:
        """Open an existing document.

        Args:
            file_path: Path to the document file.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        try:
            doc = ps_app.open_document(file_path)
            # `doc.width` / `doc.height` are either a UnitValue (with `.value`)
            # or a plain float depending on the Photoshop build. When neither can
            # be read the dimensions are reported as 0.0 and flagged as
            # unavailable, so a client can tell a genuine zero apart from an
            # unreadable measurement.
            width = try_float(getattr(doc, "width", None))
            height = try_float(getattr(doc, "height", None))

            result = {
                "success": True,
                "document_name": doc.name,
                "width": 0.0 if width is UNCONVERTIBLE else width,
                "height": 0.0 if height is UNCONVERTIBLE else height,
            }
            if width is UNCONVERTIBLE or height is UNCONVERTIBLE:
                result["dimensions_unavailable"] = True

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Register the open_document function with a specific name
    tool_name = register_tool(mcp, open_document, "open_document")
    registered_tools.append(tool_name)

    def save_document(file_path: str, format: str = "psd") -> dict:
        """Save the active document.

        Args:
            file_path: Path where to save the document.
            format: File format (psd, jpg, png).

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            if format.lower() == "jpg" or format.lower() == "jpeg":
                options = ps.JPEGSaveOptions(quality=10)
                doc.saveAs(file_path, options, asCopy=True)
            elif format.lower() == "png":
                options = ps.PNGSaveOptions()
                doc.saveAs(file_path, options, asCopy=True)
            else:  # Default to PSD
                options = ps.PhotoshopSaveOptions()
                doc.saveAs(file_path, options, asCopy=True)

            return {"success": True, "file_path": file_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Register the save_document function with a specific name
    tool_name = register_tool(mcp, save_document, "save_document")
    registered_tools.append(tool_name)

    # Return the list of registered tools
    return registered_tools
