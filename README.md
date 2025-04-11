# Photoshop MCP Server

[![PyPI Version](https://img.shields.io/pypi/v/photoshop-mcp-server.svg)](https://pypi.org/project/photoshop-mcp-server/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/photoshop-mcp-server.svg)](https://pypi.org/project/photoshop-mcp-server/)
[![Build Status](https://github.com/loonghao/photoshop-python-api-mcp-server/actions/workflows/python-publish.yml/badge.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/actions/workflows/python-publish.yml)
[![License](https://img.shields.io/github/license/loonghao/photoshop-python-api-mcp-server.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/photoshop-mcp-server.svg)](https://pypi.org/project/photoshop-mcp-server/)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server)
[![GitHub stars](https://img.shields.io/github/stars/loonghao/photoshop-python-api-mcp-server.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/loonghao/photoshop-python-api-mcp-server.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/loonghao/photoshop-python-api-mcp-server.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/commits/main)

A Model Context Protocol (MCP) server for Photoshop integration using photoshop-python-api.

English | [简体中文](README_zh.md)

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

The recommended way to configure the server is using `uvx` as the command, which is the official standard format.

### Standard Configuration (Recommended)

Add the following to your MCP host configuration (works with Claude Desktop, Windsurf, Cline, and other MCP hosts):

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

### Configuration Options

- **PS_VERSION**: Specify the Photoshop version to connect to (e.g., "2024", "2023", "2022", etc.)
- **command**: Use `uvx` for the standard approach
- **args**: Use `["ps-mcp"]` to run the Photoshop MCP server

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

Once configured in your MCP host, you can use the Photoshop MCP server in your AI assistant conversations.

![Photoshop MCP Server Demo](assets/ps-mcp.gif)

Example conversation:

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
