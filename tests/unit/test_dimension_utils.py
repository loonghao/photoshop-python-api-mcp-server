"""Tests for UnitValue/float compatibility when reading document dimensions.

Photoshop's COM interface is late-bound, so ``Document.width`` returns a
``UnitValue`` object on some Photoshop builds and a plain ``float`` on others.
Reading ``.value`` unconditionally breaks the builds that return a float.
"""

from unittest.mock import MagicMock, patch

import pytest

from photoshop_mcp_server.ps_adapter.utils import to_float


class FakeUnitValue:
    """Stand-in for photoshop's ``UnitValue`` object."""

    def __init__(self, value):
        self.value = value


class FakeDocument:
    """Minimal document stub exposing only what the call sites read."""

    def __init__(self, name="test.psd", width=1920, height=1080, as_unit_value=False):
        self.name = name
        if as_unit_value:
            self.width = FakeUnitValue(width)
            self.height = FakeUnitValue(height)
        else:
            self.width = width
            self.height = height
        self.resolution = 72
        self.artLayers = []


class RecordingMCP:
    """Fake MCP server that records registered tools and resources by name."""

    def __init__(self):
        self.tools = {}
        self.resources = {}

    def tool(self, name=None, **kwargs):
        """Return a decorator that records the tool function under ``name``."""

        def decorator(func):
            self.tools[name or func.__name__] = func
            return func

        return decorator

    def resource(self, path, **kwargs):
        """Return a decorator that records the resource function under ``path``."""

        def decorator(func):
            self.resources[path] = func
            return func

        return decorator


class TestToFloat:
    """Test suite for the ``to_float`` helper."""

    def test_plain_float(self):
        """A plain float is returned unchanged."""
        assert to_float(1920.5) == 1920.5

    def test_plain_int(self):
        """An int is converted to float."""
        assert to_float(1080) == 1080.0
        assert isinstance(to_float(1080), float)

    def test_unit_value_object(self):
        """A UnitValue-like object is unwrapped via ``.value``."""
        assert to_float(FakeUnitValue(1920.5)) == 1920.5

    def test_numeric_string(self):
        """A numeric string is converted to float."""
        assert to_float("1920.5") == 1920.5

    def test_none_returns_default(self):
        """``None`` (e.g. a missing attribute) falls back to the default."""
        assert to_float(None) == 0.0
        assert to_float(None, default=800.0) == 800.0

    def test_unconvertible_returns_default(self):
        """A non-numeric value falls back to the default instead of raising."""
        assert to_float(object(), default=600.0) == 600.0

    def test_unit_value_with_unconvertible_value_returns_default(self):
        """A UnitValue whose ``.value`` is not numeric also falls back safely."""
        assert to_float(FakeUnitValue("not-a-number"), default=300.0) == 300.0


class TestOpenDocument:
    """Test suite for the ``open_document`` tool."""

    @pytest.fixture
    def open_document_tool(self):
        """Register the document tools against a fake MCP and return the tool."""
        from photoshop_mcp_server.tools import document_tools

        mcp = RecordingMCP()
        document_tools.register(mcp)
        return mcp.tools["photoshop_open_document"]

    @pytest.mark.parametrize(
        ("as_unit_value",),
        [
            (False,),
            (True,),
        ],
        ids=["float", "unit_value"],
    )
    def test_returns_real_dimensions(self, open_document_tool, as_unit_value):
        """Width/height are reported for both float and UnitValue builds."""
        doc = FakeDocument(width=1920, height=1080, as_unit_value=as_unit_value)

        with patch(
            "photoshop_mcp_server.tools.document_tools.PhotoshopApp"
        ) as mock_app_cls:
            mock_app_cls.return_value.open_document.return_value = doc
            result = open_document_tool("C:/tmp/test.psd")

        assert result["success"] is True
        assert result["document_name"] == "test.psd"
        assert result["width"] == 1920.0
        assert result["height"] == 1080.0

    def test_missing_dimensions_do_not_raise(self, open_document_tool):
        """A document without width/height still returns a successful result."""
        doc = MagicMock(spec=["name"])
        doc.name = "test.psd"

        with patch(
            "photoshop_mcp_server.tools.document_tools.PhotoshopApp"
        ) as mock_app_cls:
            mock_app_cls.return_value.open_document.return_value = doc
            result = open_document_tool("C:/tmp/test.psd")

        assert result["success"] is True
        assert result["width"] == 0.0
        assert result["height"] == 0.0


class TestCreateDocument:
    """Test suite for the ``create_document`` tool.

    This is the only call site passing a non-trivial ``default``, so it is
    asserted separately from ``open_document``.
    """

    @pytest.fixture
    def create_document_tool(self):
        """Register the document tools against a fake MCP and return the tool."""
        from photoshop_mcp_server.tools import document_tools

        mcp = RecordingMCP()
        document_tools.register(mcp)
        return mcp.tools["photoshop_create_document"]

    @pytest.mark.parametrize(
        ("as_unit_value",),
        [
            (False,),
            (True,),
        ],
        ids=["float", "unit_value"],
    )
    def test_returns_real_dimensions(self, create_document_tool, as_unit_value):
        """Width/height come from the document, not from the requested size.

        The requested size deliberately differs from what Photoshop reports, and
        the result must carry no ``warning``. Both assertions matter:
        ``create_document`` wraps property reads in a broad ``except`` that falls
        back to the requested size, so a test whose requested size equals the
        reported size would pass even when reading the dimensions raises.
        """
        doc = FakeDocument(
            name="created.psd", width=800, height=600, as_unit_value=as_unit_value
        )

        with patch(
            "photoshop_mcp_server.tools.document_tools.PhotoshopApp"
        ) as mock_app_cls:
            mock_app_cls.return_value.create_document.return_value = doc
            result = create_document_tool(width=1000, height=1000, name="created.psd")

        assert result["success"] is True
        assert result["document_name"] == "created.psd"
        assert result["width"] == 800.0
        assert result["height"] == 600.0
        assert "warning" not in result

    def test_missing_dimensions_fall_back_to_requested_size(
        self, create_document_tool
    ):
        """When Photoshop reports no dimensions, the requested size is kept.

        This call site is the only one that passes ``default``, so the created
        document reports the size the caller asked for instead of 0.
        """
        doc = MagicMock(spec=["name"])
        doc.name = "created.psd"

        with patch(
            "photoshop_mcp_server.tools.document_tools.PhotoshopApp"
        ) as mock_app_cls:
            mock_app_cls.return_value.create_document.return_value = doc
            result = create_document_tool(width=1024, height=768, name="created.psd")

        assert result["success"] is True
        assert result["width"] == 1024.0
        assert result["height"] == 768.0
        # Reached via the helper's default, not by raising and hitting the
        # except-branch fallback (which would also report the requested size).
        assert "warning" not in result


class TestDocumentInfoResource:
    """Test suite for the ``photoshop://document/info`` resource."""

    @pytest.fixture
    def document_info_resource(self):
        """Register the document resources against a fake MCP and return it."""
        from photoshop_mcp_server.resources import document_resources

        mcp = RecordingMCP()
        document_resources.register(mcp)
        return mcp.resources["photoshop://document/info"]

    @pytest.mark.parametrize(
        ("as_unit_value",),
        [
            (False,),
            (True,),
        ],
        ids=["float", "unit_value"],
    )
    def test_returns_real_dimensions(self, document_info_resource, as_unit_value):
        """Width/height are reported for both float and UnitValue builds."""
        doc = FakeDocument(width=1920, height=1080, as_unit_value=as_unit_value)

        with patch(
            "photoshop_mcp_server.resources.document_resources.PhotoshopApp"
        ) as mock_app_cls:
            mock_app_cls.return_value.get_active_document.return_value = doc
            result = document_info_resource()

        assert result["name"] == "test.psd"
        assert result["width"] == 1920.0
        assert result["height"] == 1080.0
        assert result["resolution"] == 72
        assert result["layers_count"] == 0

    def test_no_active_document_returns_error(self, document_info_resource):
        """The no-document path is unchanged."""
        with patch(
            "photoshop_mcp_server.resources.document_resources.PhotoshopApp"
        ) as mock_app_cls:
            mock_app_cls.return_value.get_active_document.return_value = None
            result = document_info_resource()

        assert result == {"error": "No active document"}
