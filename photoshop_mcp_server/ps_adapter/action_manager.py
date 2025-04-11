"""Photoshop Action Manager utilities.

This module provides utilities for working with Photoshop's Action Manager API,
which is a lower-level API that is more stable than the JavaScript API.
"""

from typing import Any

import photoshop.api as ps

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp


class ActionManager:
    """Utility class for working with Photoshop's Action Manager API."""

    @staticmethod
    def str_id_to_char_id(string_id: str) -> int:
        """Convert a string ID to a character ID.

        Args:
            string_id: The string ID to convert.

        Returns:
            The character ID.

        """
        ps_app = PhotoshopApp()
        return ps_app.app.stringIDToTypeID(string_id)

    @staticmethod
    def char_id_to_type_id(char_id: str) -> int:
        """Convert a character ID to a type ID.

        Args:
            char_id: The character ID to convert.

        Returns:
            The type ID.

        """
        ps_app = PhotoshopApp()
        return ps_app.app.charIDToTypeID(char_id)

    @classmethod
    def get_active_document_info(cls) -> dict[str, Any]:
        """Get information about the active document using Action Manager.

        Returns:
            A dictionary containing information about the active document,
            or an error message if no document is open.

        """
        try:
            ps_app = PhotoshopApp()
            app = ps_app.app

            # Check if there's an active document
            if not hasattr(app, "documents") or not app.documents.length:
                return {
                    "success": True,
                    "error": "No active document",
                    "no_document": True,
                }

            # Create a reference to the current document
            ref = ps.ActionReference()
            ref.putEnumerated(
                cls.char_id_to_type_id("Dcmn"),  # Document
                cls.char_id_to_type_id("Ordn"),  # Ordinal
                cls.char_id_to_type_id("Trgt"),  # Target/Current
            )

            # Get the document descriptor
            desc = app.executeActionGet(ref)

            # Extract basic document info
            result = {
                "success": True,
                "name": "",
                "width": 0,
                "height": 0,
                "resolution": 0,
                "mode": "",
                "color_mode": "",
                "bit_depth": 0,
                "layers": [],
                "layer_sets": [],
                "channels": [],
                "path": "",
            }

            # Get document properties safely
            try:
                if desc.hasKey(cls.str_id_to_char_id("title")):
                    result["name"] = desc.getString(cls.str_id_to_char_id("title"))
            except Exception as e:
                print(f"Error getting document name: {e}")

            try:
                if desc.hasKey(cls.char_id_to_type_id("Wdth")):
                    result["width"] = desc.getUnitDoubleValue(
                        cls.char_id_to_type_id("Wdth")
                    )
            except Exception as e:
                print(f"Error getting document width: {e}")

            try:
                if desc.hasKey(cls.char_id_to_type_id("Hght")):
                    result["height"] = desc.getUnitDoubleValue(
                        cls.char_id_to_type_id("Hght")
                    )
            except Exception as e:
                print(f"Error getting document height: {e}")

            try:
                if desc.hasKey(cls.char_id_to_type_id("Rslt")):
                    result["resolution"] = desc.getUnitDoubleValue(
                        cls.char_id_to_type_id("Rslt")
                    )
            except Exception as e:
                print(f"Error getting document resolution: {e}")

            try:
                if desc.hasKey(cls.char_id_to_type_id("Md  ")):
                    mode_id = desc.getEnumerationValue(cls.char_id_to_type_id("Md  "))
                    mode_map = {
                        cls.char_id_to_type_id("Grys"): "Grayscale",
                        cls.char_id_to_type_id("RGBM"): "RGB",
                        cls.char_id_to_type_id("CMYM"): "CMYK",
                        cls.char_id_to_type_id("LbCM"): "Lab",
                    }
                    result["mode"] = mode_map.get(mode_id, f"Unknown ({mode_id})")
                    result["color_mode"] = result["mode"]
            except Exception as e:
                print(f"Error getting document mode: {e}")

            try:
                if desc.hasKey(cls.char_id_to_type_id("Dpth")):
                    result["bit_depth"] = desc.getInteger(
                        cls.char_id_to_type_id("Dpth")
                    )
            except Exception as e:
                print(f"Error getting document bit depth: {e}")

            try:
                if desc.hasKey(cls.str_id_to_char_id("fileReference")):
                    file_ref = desc.getPath(cls.str_id_to_char_id("fileReference"))
                    result["path"] = str(file_ref)
            except Exception as e:
                print(f"Error getting document path: {e}")

            # Get layers info would require more complex Action Manager code
            # This is a simplified implementation

            return result

        except Exception as e:
            import traceback

            tb_text = traceback.format_exc()
            print(f"Error in get_active_document_info: {e}")
            print(tb_text)
            return {"success": False, "error": str(e), "detailed_error": tb_text}

    @classmethod
    def get_selection_info(cls) -> dict[str, Any]:
        """Get information about the current selection using Action Manager.

        Returns:
            A dictionary containing information about the current selection,
            or an indication that there is no selection.

        """
        try:
            ps_app = PhotoshopApp()
            app = ps_app.app

            # Check if there's an active document
            if not hasattr(app, "documents") or not app.documents.length:
                return {
                    "success": True,
                    "has_selection": False,
                    "error": "No active document",
                }

            # Create a reference to check if there's a selection
            ref = ps.ActionReference()
            ref.putProperty(
                cls.char_id_to_type_id("Prpr"),  # Property
                cls.char_id_to_type_id("PixL"),  # Pixel Selection
            )
            ref.putEnumerated(
                cls.char_id_to_type_id("Dcmn"),  # Document
                cls.char_id_to_type_id("Ordn"),  # Ordinal
                cls.char_id_to_type_id("Trgt"),  # Target/Current
            )

            # Try to get the selection
            try:
                # If this doesn't throw an error, there's a selection
                app.executeActionGet(ref)
                # We don't need to store the result, just check if it throws an exception
            except Exception:
                # No selection
                return {"success": True, "has_selection": False}

            # If we get here, there is a selection
            # Get the bounds of the selection
            bounds_ref = ps.ActionReference()
            bounds_ref.putProperty(
                cls.char_id_to_type_id("Prpr"),  # Property
                cls.str_id_to_char_id("bounds"),  # Bounds
            )
            bounds_ref.putEnumerated(
                cls.char_id_to_type_id("csel"),  # Current Selection
                cls.char_id_to_type_id("Ordn"),  # Ordinal
                cls.char_id_to_type_id("Trgt"),  # Target/Current
            )

            try:
                bounds_desc = app.executeActionGet(bounds_ref)
                if bounds_desc.hasKey(cls.str_id_to_char_id("bounds")):
                    bounds = bounds_desc.getObjectValue(cls.str_id_to_char_id("bounds"))

                    # Extract bounds values
                    left = bounds.getUnitDoubleValue(cls.char_id_to_type_id("Left"))
                    top = bounds.getUnitDoubleValue(cls.char_id_to_type_id("Top "))
                    right = bounds.getUnitDoubleValue(cls.char_id_to_type_id("Rght"))
                    bottom = bounds.getUnitDoubleValue(cls.char_id_to_type_id("Btom"))

                    # Calculate dimensions
                    width = right - left
                    height = bottom - top

                    return {
                        "success": True,
                        "has_selection": True,
                        "bounds": {
                            "left": left,
                            "top": top,
                            "right": right,
                            "bottom": bottom,
                        },
                        "width": width,
                        "height": height,
                        "area": width * height,
                    }
            except Exception as e:
                print(f"Error getting selection bounds: {e}")
                return {
                    "success": True,
                    "has_selection": True,
                    "error": f"Selection exists but couldn't get bounds: {e!s}",
                }

            # Fallback if we couldn't get bounds
            return {"success": True, "has_selection": True}

        except Exception as e:
            import traceback

            tb_text = traceback.format_exc()
            print(f"Error in get_selection_info: {e}")
            print(tb_text)
            return {
                "success": False,
                "has_selection": False,
                "error": str(e),
                "detailed_error": tb_text,
            }

    @classmethod
    def get_session_info(cls) -> dict[str, Any]:
        """Get information about the current Photoshop session using Action Manager.

        Returns:
            A dictionary containing information about the current Photoshop session.

        """
        try:
            ps_app = PhotoshopApp()
            app = ps_app.app

            # Get basic application info
            info = {
                "success": True,
                "is_running": True,
                "version": app.version,
                "build": getattr(app, "build", ""),
                "has_active_document": False,
                "documents": [],
                "active_document": None,
                "preferences": {},
            }

            # Get document info
            doc_info = cls.get_active_document_info()
            if doc_info.get("success", False) and not doc_info.get(
                "no_document", False
            ):
                info["has_active_document"] = True
                info["active_document"] = doc_info

                # Get all documents
                docs = []
                for i in range(app.documents.length):
                    try:
                        # Create a reference to the document
                        doc_ref = ps.ActionReference()
                        doc_ref.putIndex(
                            cls.char_id_to_type_id("Dcmn"),  # Document
                            i + 1,  # 1-based index
                        )

                        # Get the document descriptor
                        doc_desc = app.executeActionGet(doc_ref)

                        # Extract basic info
                        doc_info = {
                            "name": "",
                            "width": 0,
                            "height": 0,
                            "is_active": False,
                        }

                        # Get document name
                        if doc_desc.hasKey(cls.str_id_to_char_id("title")):
                            doc_info["name"] = doc_desc.getString(
                                cls.str_id_to_char_id("title")
                            )

                        # Check if this is the active document
                        doc_info["is_active"] = (
                            doc_info["name"] == info["active_document"]["name"]
                        )

                        # Get dimensions
                        if doc_desc.hasKey(cls.char_id_to_type_id("Wdth")):
                            doc_info["width"] = doc_desc.getUnitDoubleValue(
                                cls.char_id_to_type_id("Wdth")
                            )
                        if doc_desc.hasKey(cls.char_id_to_type_id("Hght")):
                            doc_info["height"] = doc_desc.getUnitDoubleValue(
                                cls.char_id_to_type_id("Hght")
                            )

                        docs.append(doc_info)
                    except Exception as e:
                        print(f"Error getting document {i} info: {e}")

                info["documents"] = docs

            # Get preferences
            try:
                # Create a reference to the application
                app_ref = ps.ActionReference()
                app_ref.putProperty(
                    cls.char_id_to_type_id("Prpr"),  # Property
                    cls.str_id_to_char_id("generalPreferences"),  # General Preferences
                )
                app_ref.putEnumerated(
                    cls.char_id_to_type_id("capp"),  # Current Application
                    cls.char_id_to_type_id("Ordn"),  # Ordinal
                    cls.char_id_to_type_id("Trgt"),  # Target/Current
                )

                # Get the application descriptor
                app_desc = app.executeActionGet(app_ref)

                # Extract preferences
                prefs = {}

                # Get ruler units
                if app_desc.hasKey(cls.str_id_to_char_id("rulerUnits")):
                    ruler_id = app_desc.getEnumerationValue(
                        cls.str_id_to_char_id("rulerUnits")
                    )
                    ruler_map = {
                        cls.char_id_to_type_id("Pxl"): "Pixels",
                        cls.char_id_to_type_id("Inch"): "Inches",
                        cls.char_id_to_type_id("Centimeter"): "Centimeters",
                        cls.char_id_to_type_id("Millimeter"): "Millimeters",
                        cls.char_id_to_type_id("Pnt"): "Points",
                        cls.char_id_to_type_id("Pica"): "Picas",
                        cls.char_id_to_type_id("Percent"): "Percent",
                    }
                    prefs["ruler_units"] = ruler_map.get(
                        ruler_id, f"Unknown ({ruler_id})"
                    )

                # Get type units
                if app_desc.hasKey(cls.str_id_to_char_id("typeUnits")):
                    type_id = app_desc.getEnumerationValue(
                        cls.str_id_to_char_id("typeUnits")
                    )
                    type_map = {
                        cls.char_id_to_type_id("Pxl"): "Pixels",
                        cls.char_id_to_type_id("Pnt"): "Points",
                        cls.char_id_to_type_id("Millimeter"): "Millimeters",
                    }
                    prefs["type_units"] = type_map.get(type_id, f"Unknown ({type_id})")

                info["preferences"] = prefs
            except Exception as e:
                print(f"Error getting preferences: {e}")

            return info

        except Exception as e:
            import traceback

            tb_text = traceback.format_exc()
            print(f"Error in get_session_info: {e}")
            print(tb_text)
            return {
                "success": False,
                "is_running": True,
                "error": str(e),
                "detailed_error": tb_text,
            }
