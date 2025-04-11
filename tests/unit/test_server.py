# -*- coding: utf-8 -*-
"""Tests for the server module."""

import pytest
from unittest.mock import patch, MagicMock

from photoshop_mcp_server.server import create_server


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


def test_create_server():
    """Test creating an MCP server."""
    server = create_server()
    assert server is not None
    assert server.name == "Photoshop"
    

def test_create_server_with_custom_name():
    """Test creating an MCP server with a custom name."""
    server = create_server(name="Custom Photoshop")
    assert server is not None
    assert server.name == "Custom Photoshop"


def test_create_server_with_custom_version():
    """Test creating an MCP server with a custom version."""
    server = create_server(version="1.2.3")
    assert server is not None
    assert server.version == "1.2.3"
