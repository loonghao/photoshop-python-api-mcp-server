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


This environment variable is passed to the underlying [photoshop-python-api](https://github.com/loonghao/photoshop-python-api) which uses it to connect to the specified Photoshop version.

## MCP Host Integration

This server is designed to work with various MCP hosts like Claude Desktop, Windsurf, Cline, and others.

### Windsurf

To use with Windsurf, add the server to your Windsurf configuration:

```json
{
  "mcpServers":  {
    "photoshop": {
      "command": "uvx",
      "args": ["photoshop-mcp-server"],
      "env": {
        "PS_VERSION": "2024"
      }
    }
  }
}
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
