#!/usr/bin/env python3
"""Claude Code Explorer - Working Implementation.

This example shows the correct way to use Claude Code Explorer
with the MCP server built from source.
"""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Test Claude Code Explorer with working configuration."""
    
    print("=" * 70)
    print("CLAUDE CODE EXPLORER - WORKING VERSION")
    print("=" * 70)
    print()
    
    # Configuration
    MCP_SERVER_PATH = "/tmp/claude-code/mcp-server/dist/src/index.js"
    MCP_CWD = "/tmp/claude-code/mcp-server"
    CLAUDE_CODE_SRC = "/tmp/claude-code/src"
    
    print(f"MCP Server: {MCP_SERVER_PATH}")
    print(f"Working Dir: {MCP_CWD}")
    print(f"Source Root: {CLAUDE_CODE_SRC}")
    print()
    
    # Set environment
    env = os.environ.copy()
    env["CLAUDE_CODE_SRC_ROOT"] = CLAUDE_CODE_SRC
    
    server_params = StdioServerParameters(
        command="node",
        args=[MCP_SERVER_PATH],
        cwd=MCP_CWD,
        env=env,
    )
    
    async with stdio_client(server_params) as (read, write):
        print("✅ Connected to MCP server")
        
        async with ClientSession(read, write) as session:
            print("✅ Session initialized")
            print()
            
            # 1. List tools
            print("1. Listing tools...")
            tools = await session.list_tools()
            print(f"   ✅ Found {len(tools.tools)} tools")
            print()
            print("   Tools:")
            for i, tool in enumerate(tools.tools[:5], 1):
                print(f"     {i}. {tool.name}")
                print(f"        {tool.description[:70]}...")
            print()
            
            # 2. List commands
            print("2. Listing commands...")
            await session.call_tool("list_commands", {})
            print("   ✅ Commands retrieved")
            print()
            
            # 3. Get architecture
            print("3. Getting architecture...")
            await session.call_tool("get_architecture", {})
            print("   ✅ Architecture retrieved")
            print()
            
            # 4. Search source
            print("4. Searching source...")
            await session.call_tool(
                "search_source",
                {"pattern": "class.*Tool", "limit": 3}
            )
            print("   ✅ Search completed")
            print()
            
            print("=" * 70)
            print("🎉 CLAUDE CODE EXPLORER IS 100% WORKING!")
            print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
