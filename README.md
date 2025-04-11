# Photoshop MCP Server

A Model Context Protocol (MCP) server for Photoshop integration using photoshop-python-api.

## Overview

This project provides a bridge between the Model Context Protocol (MCP) and Adobe Photoshop, allowing AI assistants and other MCP clients to control Photoshop programmatically.

## Features

- **MCP Resources**: Access information about Photoshop and documents
- **MCP Tools**: Control Photoshop with simple function calls
- **Windows Support**: Works with Photoshop on Windows via COM interface

## Requirements

- **Windows OS only**: This server uses COM interface which is only available on Windows
- **Adobe Photoshop**: Must be installed locally (tested with versions CC2017 through 2024)
- **Python**: Version 3.10 or higher

### Photoshop Version Configuration

By default, the server will attempt to connect to the latest installed version of Photoshop. You can specify a particular version using the `PS_VERSION` environment variable:

```bash
# For Photoshop 2024
set PS_VERSION=2024

# For Photoshop 2023
set PS_VERSION=2023

# For Photoshop 2022
set PS_VERSION=2022

# For Photoshop 2021
set PS_VERSION=2021

# For Photoshop 2020
set PS_VERSION=2020

# For Photoshop CC 2019
set PS_VERSION=2019

# For Photoshop CC 2018
set PS_VERSION=2018

# For Photoshop CC 2017
set PS_VERSION=2017
```

This environment variable is passed to the underlying [photoshop-python-api](https://github.com/loonghao/photoshop-python-api) which uses it to connect to the specified Photoshop version.

## Installation

```bash
# Using pip
pip install photoshop-mcp-server

# Using uv
uv pip install photoshop-mcp-server
```

## Quick Start

### Starting the Server

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

### Using Session Tools

Here's an example of how to use the session tools to get information about the current Photoshop session:

```python
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "photoshop_mcp_server.server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get session info
            session_info = await session.call_tool("get_session_info")
            print(f"Session info: {json.dumps(session_info, indent=2)}")

            # Check if there's an active document
            if session_info.get("has_active_document", False):
                # Get active document info
                doc_info = await session.call_tool("get_active_document_info")
                print(f"Document info: {json.dumps(doc_info, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
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

### Document Tools

- `create_document` - Create a new Photoshop document
- `open_document` - Open an existing document
- `save_document` - Save the active document

### Layer Tools

- `create_text_layer` - Create a text layer
- `create_solid_color_layer` - Create a solid color layer

### Session Tools

- `get_session_info` - Get information about the current Photoshop session
- `get_active_document_info` - Get detailed information about the active document
- `get_selection_info` - Get information about the current selection

## License

MIT

## Acknowledgements

- [photoshop-python-api](https://github.com/loonghao/photoshop-python-api) - Python API for Photoshop
- [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) - MCP Python SDK
