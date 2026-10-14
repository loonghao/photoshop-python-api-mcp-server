"""Document-related MCP resources."""

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.ps_adapter.utils import UNCONVERTIBLE, try_float


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
            "has_active_document": ps_app.get_active_document() is not None,
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

        # `doc.width` / `doc.height` are either a UnitValue (with `.value`)
        # or a plain float depending on the Photoshop build. When neither can be
        # read the dimensions are reported as 0.0 and flagged as unavailable, so
        # a client can tell a genuine zero apart from an unreadable measurement.
        width = try_float(getattr(doc, "width", None))
        height = try_float(getattr(doc, "height", None))
        dimensions_unavailable = width is UNCONVERTIBLE or height is UNCONVERTIBLE

        info = {
            "name": doc.name,
            "width": 0.0 if width is UNCONVERTIBLE else width,
            "height": 0.0 if height is UNCONVERTIBLE else height,
            "resolution": doc.resolution,
            "layers_count": len(doc.artLayers),
        }
        if dimensions_unavailable:
            info["dimensions_unavailable"] = True

        return info

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
            layers.append(
                {
                    "index": i,
                    "name": layer.name,
                    "visible": layer.visible,
                    "kind": str(layer.kind),
                }
            )

        return {"layers": layers}
