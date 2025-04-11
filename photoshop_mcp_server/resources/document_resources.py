# -*- coding: utf-8 -*-
"""Document-related MCP resources."""

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp


def register(mcp):
    """Register document-related resources.
    
    Args:
        mcp: The MCP server instance.
    """
    
    @mcp.resource("photoshop://info")
    def get_photoshop_info() -> dict:
        """Get information about the Photoshop application.
        
        Returns:
            dict: Information about Photoshop.
        """
        ps_app = PhotoshopApp()
        return {
            "version": ps_app.get_version(),
            "has_active_document": ps_app.get_active_document() is not None
        }
    
    @mcp.resource("photoshop://document/info")
    def get_document_info() -> dict:
        """Get information about the active document.
        
        Returns:
            dict: Information about the active document or an error message.
        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"error": "No active document"}
        
        return {
            "name": doc.name,
            "width": doc.width.value,
            "height": doc.height.value,
            "resolution": doc.resolution,
            "layers_count": len(doc.artLayers)
        }
    
    @mcp.resource("photoshop://document/layers")
    def get_layers() -> dict:
        """Get information about the layers in the active document.
        
        Returns:
            dict: Information about layers or an error message.
        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"error": "No active document"}
        
        layers = []
        for i, layer in enumerate(doc.artLayers):
            layers.append({
                "index": i,
                "name": layer.name,
                "visible": layer.visible,
                "kind": str(layer.kind)
            })
        
        return {"layers": layers}
