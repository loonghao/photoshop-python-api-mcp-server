# Photoshop MCP Server

A Model Context Protocol (MCP) server for Photoshop integration using photoshop-python-api.

## Overview

This project provides a bridge between the Model Context Protocol (MCP) and Adobe Photoshop, allowing AI assistants and other MCP clients to control Photoshop programmatically.

## Requirements

- **Windows OS only**: This server uses COM interface which is only available on Windows
- **Adobe Photoshop**: Must be installed locally (tested with versions CC2017 through 2024)
- **Python**: Version 3.10 or higher

## Installation

```bash
# Install using pip
pip install photoshop-mcp-server

# Or using uv
uv install photoshop-mcp-server
```

## MCP Host Configuration

This server is designed to work with various MCP hosts. The `PS_VERSION` environment variable is used to specify which Photoshop version to connect to (e.g., "2024", "2023", "2022", etc.).

### Claude Desktop

To use with Claude Desktop, add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "photoshop": {
      "command": "ps-mcp",
      "env": {
        "PS_VERSION": "2024"
      }
    }
  }
}
```

### Windsurf

To use with Windsurf, add the server to your Windsurf configuration:

```json
{
  "mcpServers": {
    "photoshop": {
      "command": "ps-mcp",
      "env": {
        "PS_VERSION": "2024"
      }
    }
  }
}
```

### Cline

To use with Cline, add the server to your Cline configuration:

```json
{
  "mcpServers": {
    "photoshop": {
      "command": "ps-mcp",
      "env": {
        "PS_VERSION": "2024"
      }
    }
  }
}
```

### Using with uvx (Alternative)

If you installed the package with uv and want to use uvx to run the server:

```json
{
  "mcpServers": {
    "photoshop": {
      "command": "uvx",
      "args": ["ps-mcp"],
      "env": {
        "PS_VERSION": "2024"
      }
    }
  }
}
```

## Key Features

### Available Resources

- `photoshop://info` - Get Photoshop application information
- `photoshop://document/info` - Get active document information
- `photoshop://document/layers` - Get layers in the active document

### Available Tools

The server provides various tools for controlling Photoshop:

- **Document Tools**: Create, open, and save documents
- **Layer Tools**: Create text layers, solid color layers, etc.
- **Session Tools**: Get information about Photoshop session, active document, selection

## Basic Usage Example

Once configured in your MCP host, you can use the Photoshop MCP server in your AI assistant conversations. For example:

```text
User: Can you create a new Photoshop document and add a text layer with "Hello World"?

AI Assistant: I'll create a new document and add the text layer for you.

[The AI uses the Photoshop MCP server to:
1. Create a new document using the `create_document` tool
2. Add a text layer using the `create_text_layer` tool with the text "Hello World"]

I've created a new Photoshop document and added a text layer with "Hello World".
```

## License

MIT

## Acknowledgements

- [photoshop-python-api](https://github.com/loonghao/photoshop-python-api) - Python API for Photoshop
- [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) - MCP Python SDK
