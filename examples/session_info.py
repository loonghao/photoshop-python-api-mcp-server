"""Session Info example for Photoshop MCP Server.

This example demonstrates how to use the MCP client to:
1. Get information about the current Photoshop session
2. Get detailed information about the active document
3. Get information about the current selection
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Run the Session Info example."""
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

            # Get session info
            print("\n1. Getting session info...")
            result = await session.call_tool("get_session_info")
            print(f"Session info:\n{json.dumps(result, indent=2)}")

            # Check if there's an active document
            if result.get("has_active_document", False):
                # Get active document info
                print("\n2. Getting active document info...")
                doc_info = await session.call_tool("get_active_document_info")
                print(f"Active document info:\n{json.dumps(doc_info, indent=2)}")

                # Get selection info
                print("\n3. Getting selection info...")
                selection_info = await session.call_tool("get_selection_info")
                print(f"Selection info:\n{json.dumps(selection_info, indent=2)}")
            else:
                print("\nNo active document. Please open a document in Photoshop and run this example again.")

            print("\nExample completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
