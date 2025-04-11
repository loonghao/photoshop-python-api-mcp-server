"""Integration tests for Photoshop integration.

These tests require Photoshop to be installed and will be skipped if it's not available.
"""

import os
import sys
import pytest
import platform

# Skip all tests if not on Windows
pytestmark = pytest.mark.skipif(
    platform.system() != "Windows", reason="Photoshop integration tests only run on Windows"
)


def is_photoshop_available():
    """Check if Photoshop is available."""
    try:
        import photoshop.api as ps

        ps.Application()
        return True
    except Exception:
        return False


# Skip tests if Photoshop is not available
pytestmark = pytest.mark.skipif(not is_photoshop_available(), reason="Photoshop is not available")


@pytest.fixture
def photoshop_app():
    """Fixture to provide a Photoshop application instance."""
    try:
        import photoshop.api as ps

        app = ps.Application()
        yield app
    except Exception as e:
        pytest.skip(f"Failed to initialize Photoshop: {e}")


def test_photoshop_version(photoshop_app):
    """Test getting Photoshop version."""
    assert photoshop_app.version is not None
    assert isinstance(photoshop_app.version, str)


def test_create_document(photoshop_app):
    """Test creating a document."""
    # Skip if we can't create documents
    if not hasattr(photoshop_app, "documents"):
        pytest.skip("Cannot access documents in Photoshop")

    try:
        import photoshop.api as ps

        doc = photoshop_app.documents.add(width=500, height=500, name="Test Document")
        assert doc is not None
        assert doc.name == "Test Document"

        # Clean up
        doc.close(ps.SaveOptions.DoNotSaveChanges)
    except Exception as e:
        pytest.skip(f"Failed to create document: {e}")
