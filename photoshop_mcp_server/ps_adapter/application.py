# -*- coding: utf-8 -*-
"""Photoshop application adapter."""

import photoshop.api as ps


class PhotoshopApp:
    """Adapter for the Photoshop application."""
    
    def __init__(self):
        """Initialize the Photoshop application."""
        self.app = ps.Application()
    
    def get_version(self):
        """Get the Photoshop version.
        
        Returns:
            str: The Photoshop version.
        """
        return self.app.version
    
    def get_active_document(self):
        """Get the active document.
        
        Returns:
            Document or None: The active document or None if no document is open.
        """
        return self.app.activeDocument if hasattr(self.app, "activeDocument") else None
    
    def create_document(self, width=1000, height=1000, resolution=72, name="Untitled", mode="rgb"):
        """Create a new document.
        
        Args:
            width (int, optional): Document width in pixels. Defaults to 1000.
            height (int, optional): Document height in pixels. Defaults to 1000.
            resolution (int, optional): Document resolution in PPI. Defaults to 72.
            name (str, optional): Document name. Defaults to "Untitled".
            mode (str, optional): Color mode (rgb, cmyk, etc.). Defaults to "rgb".
            
        Returns:
            Document: The created document.
        """
        return self.app.documents.add(width, height, resolution, name, getattr(ps.NewDocumentMode, mode.upper()))
    
    def open_document(self, file_path):
        """Open an existing document.
        
        Args:
            file_path (str): Path to the document file.
            
        Returns:
            Document: The opened document.
        """
        return self.app.open(file_path)
    
    def execute_javascript(self, script):
        """Execute JavaScript code in Photoshop.
        
        Args:
            script (str): JavaScript code to execute.
            
        Returns:
            str: The result of the JavaScript execution.
        """
        return self.app.doJavaScript(script)
