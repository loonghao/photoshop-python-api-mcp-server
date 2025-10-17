"""Tests for FastMCP initialization to prevent regression of parameter errors.

This test module specifically validates that FastMCP is initialized with the correct
parameters according to the latest MCP SDK API. This prevents regressions of issues
like 'FastMCP.__init__() got an unexpected keyword argument' errors.
"""

import pytest
from unittest.mock import patch, MagicMock
from mcp.server.fastmcp import FastMCP

from photoshop_mcp_server.server import create_server


class TestFastMCPInitialization:
    """Test suite for FastMCP initialization parameters."""

    def test_fastmcp_accepts_name_parameter(self):
        """Test that FastMCP can be initialized with name parameter."""
        server = FastMCP(name="TestServer")
        assert server is not None
        assert server.name == "TestServer"

    def test_fastmcp_does_not_accept_description_parameter(self):
        """Test that FastMCP rejects description parameter.

        This test ensures that the old API (which accepted description)
        is no longer supported, validating our fix.
        """
        with pytest.raises(TypeError, match="unexpected keyword argument"):
            FastMCP(name="TestServer", description="Test Description")

    def test_fastmcp_does_not_accept_version_parameter(self):
        """Test that FastMCP rejects version parameter.

        This test ensures that the old API (which accepted version)
        is no longer supported, validating our fix.
        """
        with pytest.raises(TypeError, match="unexpected keyword argument"):
            FastMCP(name="TestServer", version="1.0.0")

    def test_create_server_does_not_pass_description_to_fastmcp(self):
        """Test that create_server doesn't pass description to FastMCP.

        This is the critical test that validates our fix. Even though
        create_server accepts a description parameter, it should NOT
        pass it to FastMCP.
        """
        with patch("mcp.server.fastmcp.FastMCP") as mock_fastmcp:
            mock_instance = MagicMock()
            mock_fastmcp.return_value = mock_instance

            # Call with description parameter
            create_server(name="TestServer", description="This is a test description")

            # Verify FastMCP was called with only name, not description
            mock_fastmcp.assert_called_once_with(name="TestServer")

            # Ensure description was NOT passed
            call_kwargs = mock_fastmcp.call_args.kwargs
            assert "description" not in call_kwargs

    def test_create_server_does_not_pass_version_to_fastmcp(self):
        """Test that create_server doesn't pass version to FastMCP.

        This validates that the version parameter is handled internally
        but not passed to FastMCP.
        """
        with patch("mcp.server.fastmcp.FastMCP") as mock_fastmcp:
            mock_instance = MagicMock()
            mock_fastmcp.return_value = mock_instance

            # Call with version parameter
            create_server(name="TestServer", version="1.2.3")

            # Verify FastMCP was called with only name, not version
            mock_fastmcp.assert_called_once_with(name="TestServer")

            # Ensure version was NOT passed
            call_kwargs = mock_fastmcp.call_args.kwargs
            assert "version" not in call_kwargs

    def test_create_server_with_all_parameters(self):
        """Test create_server with all parameters doesn't break FastMCP init.

        This comprehensive test ensures that even when all parameters are
        provided to create_server, FastMCP is initialized correctly.
        """
        with patch("mcp.server.fastmcp.FastMCP") as mock_fastmcp:
            mock_instance = MagicMock()
            mock_fastmcp.return_value = mock_instance

            # Call with all parameters
            create_server(
                name="FullTestServer",
                description="Full test description",
                version="2.0.0",
                config={"env_vars": {"TEST": "value"}},
            )

            # Verify FastMCP was called correctly
            mock_fastmcp.assert_called_once_with(name="FullTestServer")

            # Verify only name was passed
            call_kwargs = mock_fastmcp.call_args.kwargs
            assert len(call_kwargs) == 1
            assert "name" in call_kwargs
            assert "description" not in call_kwargs
            assert "version" not in call_kwargs

    def test_fastmcp_initialization_signature(self):
        """Test that FastMCP.__init__ has the expected signature.

        This test documents the expected FastMCP API and will fail if
        the API changes unexpectedly.
        """
        import inspect

        sig = inspect.signature(FastMCP.__init__)
        params = list(sig.parameters.keys())

        # Should have 'self' and 'name' at minimum
        assert "self" in params
        assert "name" in params

        # Should NOT have these parameters (which caused the original error)
        assert "description" not in params or sig.parameters["description"].default is inspect.Parameter.empty
        assert "version" not in params or sig.parameters["version"].default is inspect.Parameter.empty
