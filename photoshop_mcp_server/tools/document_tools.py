# -*- coding: utf-8 -*-
"""Document-related MCP tools."""

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
import photoshop.api as ps


def register(mcp):
    """Register document-related tools.
    
    Args:
        mcp: The MCP server instance.
    """
    
    @mcp.tool()
    def create_document(width: int = 1000, height: int = 1000, name: str = "Untitled") -> dict:
        """Create a new document in Photoshop.
        
        Args:
            width: Document width in pixels.
            height: Document height in pixels.
            name: Document name.
            
        Returns:
            dict: Result of the operation.
        """
        ps_app = PhotoshopApp()
        try:
            doc = ps_app.create_document(width=width, height=height, name=name)
            return {
                "success": True,
                "document_name": doc.name,
                "width": doc.width.value,
                "height": doc.height.value
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
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
                "height": doc.height.value
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
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
