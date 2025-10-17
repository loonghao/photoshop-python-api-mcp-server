"""Tests for the server module."""

import pytest
from unittest.mock import patch, MagicMock, call

from photoshop_mcp_server.server import create_server
from mcp.server.fastmcp import FastMCP


@pytest.fixture
def mock_photoshop():
    """Mock the photoshop-python-api."""
    with patch("photoshop_mcp_server.ps_adapter.application.ps") as mock_ps:
        # Mock Application
        mock_app = MagicMock()
        mock_ps.Application.return_value = mock_app

        # Mock version
        mock_app.version = "2023"

        yield mock_ps


class TestCreateServer:
    """Test suite for create_server function."""

    def test_create_server_default_parameters(self):
        """Test creating an MCP server with default parameters."""
        server = create_server()
        assert server is not None
        assert isinstance(server, FastMCP)
        assert server.name == "Photoshop"

    def test_create_server_with_custom_name(self):
        """Test creating an MCP server with a custom name."""
        server = create_server(name="Custom Photoshop")
        assert server is not None
        assert isinstance(server, FastMCP)
        assert server.name == "Custom Photoshop"

    def test_create_server_with_custom_version(self):
        """Test creating an MCP server with a custom version.

        Note: FastMCP doesn't expose version as a public attribute in the latest SDK,
        but we verify the server is created successfully without errors.
        """
        server = create_server(version="1.2.3")
        assert server is not None
        assert isinstance(server, FastMCP)

    def test_create_server_fastmcp_initialization(self):
        """Test that FastMCP is initialized with correct parameters.

        This test ensures that FastMCP is called with only the 'name' parameter,
        avoiding the 'unexpected keyword argument' error that occurred with
        older versions that tried to pass 'description' and 'version'.
        """
        with patch("photoshop_mcp_server.server.FastMCP") as mock_fastmcp:
            mock_instance = MagicMock()
            mock_fastmcp.return_value = mock_instance

            # Call create_server with various parameters
            create_server(name="TestServer", description="Test Description", version="0.1.0")

            # Verify FastMCP was called with only the name parameter
            mock_fastmcp.assert_called_once_with(name="TestServer")

    def test_create_server_with_config(self):
        """Test creating an MCP server with additional configuration."""
        config = {"env_vars": {"TEST_VAR": "test_value"}}

        with patch.dict("os.environ", {}, clear=False):
            server = create_server(config=config)
            assert server is not None
            assert isinstance(server, FastMCP)
            # Verify environment variable was set
            import os

            assert os.environ.get("TEST_VAR") == "test_value"

    def test_create_server_registers_resources(self):
        """Test that create_server registers resources."""
        with patch("photoshop_mcp_server.server.register_all_resources") as mock_register_resources:
            mock_register_resources.return_value = {"test_module": ["resource1"]}

            server = create_server()

            assert server is not None
            mock_register_resources.assert_called_once()

    def test_create_server_registers_tools(self):
        """Test that create_server registers tools."""
        with patch("photoshop_mcp_server.server.register_all_tools") as mock_register_tools:
            mock_register_tools.return_value = {"test_module": ["tool1"]}

            server = create_server()

            assert server is not None
            mock_register_tools.assert_called_once()
