"""Document-related MCP tools."""

import photoshop.api as ps

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.registry import register_tool


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
        print(f"Creating document: width={width}, height={height}, name={name}, mode={mode}")
        ps_app = PhotoshopApp()
        try:
            # Validate mode parameter
            valid_modes = ["rgb", "cmyk", "grayscale", "gray", "bitmap", "lab"]
            if mode.lower() not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid mode: {mode}. Valid modes are: {', '.join(valid_modes)}",
                    "detailed_error": f"Invalid color mode: {mode}\n\nValid modes are: {', '.join(valid_modes)}\n\nThe mode parameter specifies the color mode of the new document. It must be one of the valid modes listed above."
                }

            # Create document
            print(f"Calling ps_app.create_document with width={width}, height={height}, name={name}, mode={mode}")
            doc = ps_app.create_document(width=width, height=height, name=name, mode=mode)

            if not doc:
                return {"success": False, "error": "Failed to create document - returned None"}

            # Get document properties safely
            try:
                print(f"Document created, getting properties")
                doc_name = doc.name
                print(f"Document name: {doc_name}")

                # Get width safely
                doc_width = width  # Default fallback
                if hasattr(doc, "width"):
                    width_obj = doc.width
                    print(f"Width object type: {type(width_obj)}")
                    if hasattr(width_obj, "value"):
                        doc_width = width_obj.value
                    else:
                        try:
                            doc_width = float(width_obj)
                        except (TypeError, ValueError):
                            print(f"Could not convert width to float: {width_obj}")
                print(f"Document width: {doc_width}")

                # Get height safely
                doc_height = height  # Default fallback
                if hasattr(doc, "height"):
                    height_obj = doc.height
                    print(f"Height object type: {type(height_obj)}")
                    if hasattr(height_obj, "value"):
                        doc_height = height_obj.value
                    else:
                        try:
                            doc_height = float(height_obj)
                        except (TypeError, ValueError):
                            print(f"Could not convert height to float: {height_obj}")
                print(f"Document height: {doc_height}")

                return {
                    "success": True,
                    "document_name": doc_name,
                    "width": doc_width,
                    "height": doc_height,
                }
            except Exception as prop_error:
                print(f"Error getting document properties: {prop_error}")
                import traceback
                traceback.print_exc()
                # Document was created but we couldn't get properties
                return {
                    "success": True,
                    "document_name": name,
                    "width": width,
                    "height": height,
                    "warning": f"Created document but couldn't get properties: {str(prop_error)}"
                }
        except Exception as e:
            print(f"Error creating document: {e}")
            import traceback
            tb_text = traceback.format_exc()
            traceback.print_exc()

            # Create a detailed error message
            detailed_error = (
                f"Error creating document with parameters:\n"
                f"  width: {width}\n"
                f"  height: {height}\n"
                f"  name: {name}\n"
                f"  mode: {mode}\n\n"
                f"Error: {str(e)}\n\n"
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
                    "mode": mode
                }
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
            return {
                "success": True,
                "document_name": doc.name,
                "width": doc.width.value,
                "height": doc.height.value,
            }
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