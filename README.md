# Photoshop MCP Server

A Model Context Protocol (MCP) server for Photoshop integration using photoshop-python-api.

## Overview

This project provides a bridge between the Model Context Protocol (MCP) and Adobe Photoshop, allowing AI assistants and other MCP clients to control Photoshop programmatically.

## Features

- **MCP Resources**: Access information about Photoshop and documents
- **MCP Tools**: Control Photoshop with simple function calls
- **Windows Support**: Works with Photoshop on Windows via COM interface

## Requirements

- Windows OS
- Adobe Photoshop (tested with versions CC2017 through 2024)
- Python 3.8+

## Installation

```bash
# Using pip
pip install photoshop-mcp-server

# Using uv
uv pip install photoshop-mcp-server
```

## Quick Start

```python
# Start the MCP server
from photoshop_mcp_server.server import create_server

# Create and run the server
mcp = create_server()
mcp.run()
```

Or use the command-line interface:

```bash
# Start the server
ps-mcp

# Start with custom name and debug logging
ps-mcp --name "My Photoshop" --debug
```

## MCP Host Integration

This server is designed to work with various MCP hosts like Claude Desktop, Claude Windsurf, and others.

### Claude Desktop

Install the server in Claude Desktop:

```bash
# Install in Claude Desktop
mcp install ps-mcp

# Or install with custom name
mcp install ps-mcp --name "My Photoshop"
```

### Claude Windsurf

To use with Claude Windsurf, add the server to your Windsurf configuration:

```json
{
  "servers": [
    {
      "name": "photoshop",
      "command": "ps-mcp",
      "args": ["--name", "Photoshop for Windsurf"]
    }
  ]
}
```

### Other MCP Hosts

For other MCP hosts, use the `pyproject.toml` configuration which provides metadata for automatic discovery:

```toml
[tool.mcp]
name = "Photoshop"
description = "Control Adobe Photoshop using MCP"
version = "0.1.0"
icon = "https://raw.githubusercontent.com/loonghao/photoshop-python-api-mcp-server/main/assets/photoshop-icon.png"
authors = ["Hal <hal.long@outlook.com>"]
repository = "https://github.com/loonghao/photoshop-python-api-mcp-server"
entrypoint = "photoshop_mcp_server.server:create_server"
```

This configuration allows MCP hosts to automatically discover and load the server with the correct metadata.

## Available Resources

- `photoshop://info` - Get Photoshop application information
- `photoshop://document/info` - Get active document information
- `photoshop://document/layers` - Get layers in the active document

## Available Tools

- `create_document` - Create a new Photoshop document
- `open_document` - Open an existing document
- `save_document` - Save the active document
- `create_text_layer` - Create a text layer
- `create_solid_color_layer` - Create a solid color layer

## License

MIT

## Acknowledgements

- [photoshop-python-api](https://github.com/loonghao/photoshop-python-api) - Python API for Photoshop
- [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) - MCP Python SDK
