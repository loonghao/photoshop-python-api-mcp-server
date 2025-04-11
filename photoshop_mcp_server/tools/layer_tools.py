"""Layer-related MCP tools."""

import photoshop.api as ps

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.registry import register_tool


def register(mcp):
    """Register layer-related tools.

    Args:
        mcp: The MCP server instance.

    Returns:
        list: List of registered tool names.
    """
    registered_tools = []

    def create_text_layer(
        text: str,
        x: int = 100,
        y: int = 100,
        size: int = 24,
        color_r: int = 0,
        color_g: int = 0,
        color_b: int = 0,
    ) -> dict:
        """Create a text layer.

        Args:
            text: Text content.
            x: X position.
            y: Y position.
            size: Font size.
            color_r: Red component (0-255).
            color_g: Green component (0-255).
            color_b: Blue component (0-255).

        Returns:
            dict: Result of the operation.

        """
        # Sanitize text input to ensure it's valid UTF-8
        try:
            # Ensure text is properly encoded/decoded
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            else:
                # Force encode and decode to catch any encoding issues
                text = text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            print(f"Sanitized text: '{text}'")
        except Exception as e:
            print(f"Error sanitizing text: {e}")
            return {
                "success": False,
                "error": f"Invalid text encoding: {str(e)}",
                "detailed_error": f"The text provided contains invalid characters that cannot be properly encoded in UTF-8. Please check the text and try again with valid characters."
            }

        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(f"Creating text layer: text='{text}', position=({x}, {y}), size={size}, color=({color_r}, {color_g}, {color_b})")

            # Create text layer
            print("Adding art layer")
            text_layer = doc.artLayers.add()
            print(f"Setting layer kind to TextLayer")
            text_layer.kind = ps.LayerKind.TextLayer

            # Configure text
            print("Configuring text item")
            text_item = text_layer.textItem
            text_item.contents = text
            text_item.position = [x, y]
            text_item.size = size

            # Configure color
            print("Setting text color")
            text_color = ps.SolidColor()
            text_color.rgb.red = color_r
            text_color.rgb.green = color_g
            text_color.rgb.blue = color_b
            text_item.color = text_color

            print(f"Text layer created successfully: {text_layer.name}")
            return {"success": True, "layer_name": text_layer.name}
        except Exception as e:
            print(f"Error creating text layer: {e}")
            import traceback
            tb_text = traceback.format_exc()
            traceback.print_exc()

            # Create a detailed error message
            detailed_error = (
                f"Error creating text layer with parameters:\n"
                f"  text: {text}\n"
                f"  position: ({x}, {y})\n"
                f"  size: {size}\n"
                f"  color: ({color_r}, {color_g}, {color_b})\n\n"
                f"Error: {str(e)}\n\n"
                f"Traceback:\n{tb_text}"
            )

            return {
                "success": False,
                "error": str(e),
                "detailed_error": detailed_error,
                "parameters": {
                    "text": text,
                    "x": x,
                    "y": y,
                    "size": size,
                    "color": [color_r, color_g, color_b]
                }
            }

    # Register the create_text_layer function with a specific name
    tool_name = register_tool(mcp, create_text_layer, "create_text_layer")
    registered_tools.append(tool_name)

    def create_solid_color_layer(
        color_r: int = 255, color_g: int = 0, color_b: int = 0, name: str = "Color Fill"
    ) -> dict:
        """Create a solid color fill layer.

        Args:
            color_r: Red component (0-255).
            color_g: Green component (0-255).
            color_b: Blue component (0-255).
            name: Layer name.

        Returns:
            dict: Result of the operation.

        """
        # Sanitize name input to ensure it's valid UTF-8
        try:
            # Ensure name is properly encoded/decoded
            if isinstance(name, bytes):
                name = name.decode('utf-8', errors='replace')
            else:
                # Force encode and decode to catch any encoding issues
                name = name.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            print(f"Sanitized layer name: '{name}'")
        except Exception as e:
            print(f"Error sanitizing layer name: {e}")
            return {
                "success": False,
                "error": f"Invalid name encoding: {str(e)}",
                "detailed_error": f"The layer name provided contains invalid characters that cannot be properly encoded in UTF-8. Please check the name and try again with valid characters."
            }

        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(f"Creating solid color layer: name='{name}', color=({color_r}, {color_g}, {color_b})")

            # Escape special characters in the name for JavaScript
            escaped_name = name.replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')

            # Create a solid color fill layer using JavaScript
            js_script = f"""
            try {{
                var doc = app.activeDocument;
                var newLayer = doc.artLayers.add();
                newLayer.name = "{escaped_name}";

                // Create a solid color fill
                var solidColor = new SolidColor();
                solidColor.rgb.red = {color_r};
                solidColor.rgb.green = {color_g};
                solidColor.rgb.blue = {color_b};

                // Fill the layer with the color
                doc.selection.selectAll();
                doc.selection.fill(solidColor);
                doc.selection.deselect();
                'success';
            }} catch(e) {{
                'Error: ' + e.toString();
            }}
            """

            print("Executing JavaScript to create solid color layer")
            result = ps_app.execute_javascript(js_script)
            print(f"JavaScript execution result: {result}")

            # Check if JavaScript returned an error
            if result and isinstance(result, str) and result.startswith('Error:'):
                return {
                    "success": False,
                    "error": result,
                    "detailed_error": f"JavaScript error while creating solid color layer: {result}"
                }

            print(f"Solid color layer created successfully: {name}")
            return {"success": True, "layer_name": name}
        except Exception as e:
            print(f"Error creating solid color layer: {e}")
            import traceback
            tb_text = traceback.format_exc()
            traceback.print_exc()

            # Create a detailed error message
            detailed_error = (
                f"Error creating solid color layer with parameters:\n"
                f"  name: {name}\n"
                f"  color: ({color_r}, {color_g}, {color_b})\n\n"
                f"Error: {str(e)}\n\n"
                f"Traceback:\n{tb_text}"
            )

            return {
                "success": False,
                "error": str(e),
                "detailed_error": detailed_error,
                "parameters": {
                    "name": name,
                    "color": [color_r, color_g, color_b]
                }
            }

    # Register the create_solid_color_layer function with a specific name
    tool_name = register_tool(mcp, create_solid_color_layer, "create_solid_color_layer")
    registered_tools.append(tool_name)

    # Return the list of registered tools
    return registered_tools