# -*- coding: utf-8 -*-
"""
Hello World example for Photoshop MCP Server.

This example demonstrates how to use the MCP client to:
1. Create a new document
2. Add a text layer with "Hello, World!" text
3. Save the document as a JPEG file
"""

import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Run the Hello World example."""
    # Path to save the output image
    output_path = os.path.join(os.path.dirname(__file__), "hello_world.jpg")
    
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python",  # Executable
        args=["-m", "photoshop_mcp_server.server"],  # Module to run
    )
    
    print("Starting Photoshop MCP client...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("Connected to Photoshop MCP Server")
            
            # Create a new document
            print("Creating a new document...")
            result = await session.call_tool(
                "create_document",
                arguments={
                    "width": 800,
                    "height": 600,
                    "name": "Hello World Document"
                }
            )
            print(f"Document created: {result}")
            
            # Create a text layer
            print("Adding 'Hello, World!' text layer...")
            result = await session.call_tool(
                "create_text_layer",
                arguments={
                    "text": "Hello, World!",
                    "x": 250,
                    "y": 300,
                    "size": 72,
                    "color_r": 0,
                    "color_g": 255,
                    "color_b": 0
                }
            )
            print(f"Text layer created: {result}")
            
            # Save the document
            print(f"Saving document to {output_path}...")
            result = await session.call_tool(
                "save_document",
                arguments={
                    "file_path": output_path,
                    "format": "jpg"
                }
            )
            print(f"Document saved: {result}")
            
            print("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
