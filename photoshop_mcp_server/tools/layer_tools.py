# -*- coding: utf-8 -*-
"""Layer-related MCP tools."""

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
import photoshop.api as ps


def register(mcp):
    """Register layer-related tools.
    
    Args:
        mcp: The MCP server instance.
    """
    
    @mcp.tool()
    def create_text_layer(text: str, x: int = 100, y: int = 100, size: int = 24, 
                         color_r: int = 0, color_g: int = 0, color_b: int = 0) -> dict:
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
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}
        
        try:
            # Create text layer
            text_layer = doc.artLayers.add()
            text_layer.kind = ps.LayerKind.TextLayer
            
            # Configure text
            text_item = text_layer.textItem
            text_item.contents = text
            text_item.position = [x, y]
            text_item.size = size
            
            # Configure color
            text_color = ps.SolidColor()
            text_color.rgb.red = color_r
            text_color.rgb.green = color_g
            text_color.rgb.blue = color_b
            text_item.color = text_color
            
            return {
                "success": True,
                "layer_name": text_layer.name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def create_solid_color_layer(color_r: int = 255, color_g: int = 0, color_b: int = 0, 
                               name: str = "Color Fill") -> dict:
        """Create a solid color fill layer.
        
        Args:
            color_r: Red component (0-255).
            color_g: Green component (0-255).
            color_b: Blue component (0-255).
            name: Layer name.
            
        Returns:
            dict: Result of the operation.
        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}
        
        try:
            # Create a solid color fill layer using JavaScript
            js_script = f"""
            var doc = app.activeDocument;
            var newLayer = doc.artLayers.add();
            newLayer.name = "{name}";
            
            // Create a solid color fill
            var solidColor = new SolidColor();
            solidColor.rgb.red = {color_r};
            solidColor.rgb.green = {color_g};
            solidColor.rgb.blue = {color_b};
            
            // Fill the layer with the color
            doc.selection.selectAll();
            doc.selection.fill(solidColor);
            doc.selection.deselect();
            """
            
            result = ps_app.execute_javascript(js_script)
            return {"success": True, "layer_name": name}
        except Exception as e:
            return {"success": False, "error": str(e)}
