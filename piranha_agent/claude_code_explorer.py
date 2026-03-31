#!/usr/bin/env python3
"""Claude Code Explorer Skill for Piranha Agent.

Explore Claude Code's 512K+ lines of source code via MCP (Model Context Protocol).

Features:
- List all 40+ agent tools
- List all 50+ slash commands
- Get source code for specific tools/commands
- Search source code with regex
- Read any file from the source tree
- Get architecture overview

Requirements:
    pip install mcp

Usage:
    from piranha_agent import Agent
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer

    agent = Agent(skills=[ClaudeCodeExplorer()])
    
    # Or use the skill directly
    explorer = ClaudeCodeExplorer()
    result = await explorer.list_tools()
    result = await explorer.get_tool_source("BashTool")
    result = await explorer.search_source(r"def.*permission")
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "ExplorerConfig",
    "ClaudeCodeExplorer",
    "create_claude_explorer_skill",
    "add_claude_explorer_to_agent",
]

# Try to import MCP, but make it optional
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning(
        "MCP not installed. Install with: pip install mcp\n"
        "Claude Code Explorer will have limited functionality."
    )


@dataclass
class ExplorerConfig:
    """Configuration for Claude Code Explorer."""
    
    src_root: str = "/tmp/claude-code/src"
    mcp_server_command: str = "node"
    mcp_server_args: list[str] = None
    timeout_seconds: int = 30
    cwd: str = None  # Working directory for MCP server
    
    def __post_init__(self):
        if self.mcp_server_args is None:
            # Use absolute path to the built MCP server
            import os
            mcp_path = "/tmp/claude-code/mcp-server/dist/src/index.js"
            if os.path.exists(mcp_path):
                self.mcp_server_args = [mcp_path]
                # Set working directory to MCP server folder so it can find src/
                self.cwd = "/tmp/claude-code/mcp-server"
            else:
                self.mcp_server_args = ["dist/src/index.js"]


class ClaudeCodeExplorer:
    """
    Claude Code Source Code Explorer.
    
    Provides MCP-based tools to explore Claude Code's internals:
    - 40+ agent tools (FileReadTool, BashTool, AgentTool, etc.)
    - 50+ slash commands (/commit, /review, /mcp, etc.)
    - Full source code search and navigation
    - Architecture documentation
    
    Example:
        explorer = ClaudeCodeExplorer()
        
        # List all tools
        tools = await explorer.list_tools()
        
        # Get BashTool source
        source = await explorer.get_tool_source("BashTool")
        
        # Search for permission checks
        results = await explorer.search_source(r"permission.*check")
        
        # Get architecture overview
        arch = await explorer.get_architecture()
    """
    
    def __init__(self, config: ExplorerConfig = None):
        """Initialize Claude Code Explorer.
        
        Args:
            config: Explorer configuration (uses defaults if None)
        """
        self.config = config or ExplorerConfig()
        self._session = None
        self._tools_cache = None
    
    async def _get_session(self):
        """Get or create MCP session."""
        if not MCP_AVAILABLE:
            raise RuntimeError(
                "MCP not installed. Install with: pip install mcp"
            )

        if self._session is None:
            # Set environment variable for MCP server
            import os
            env = os.environ.copy()
            env["CLAUDE_CODE_SRC_ROOT"] = self.config.src_root
            
            server_params = StdioServerParameters(
                command=self.config.mcp_server_command,
                args=self.config.mcp_server_args,
                cwd=self.config.cwd,
                env=env,
            )

            client_context = stdio_client(server_params)
            read, write = await client_context.__aenter__()

            self._session = ClientSession(read, write)
            await self._session.initialize()
            
            logger.info(f"Connected to Claude Code Explorer MCP server (src: {self.config.src_root})")

        return self._session
    
    async def close(self):
        """Close the MCP session."""
        if self._session:
            await self._session.__aexit__(None, None, None)
            self._session = None
            logger.info("Disconnected from Claude Code Explorer MCP server")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._get_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    # =========================================================================
    # Tool Discovery
    # =========================================================================
    
    async def list_tools(self) -> dict[str, Any]:
        """
        List all available Claude Code agent tools.
        
        Returns:
            Dictionary with tool names, descriptions, and schemas.
            
        Example:
            tools = await explorer.list_tools()
            print(f"Found {len(tools['tools'])} tools")
            for tool in tools['tools']:
                print(f"  - {tool['name']}: {tool['description']}")
        """
        session = await self._get_session()
        
        result = await session.call_tool("list_tools", {})
        
        # Parse and cache results
        tools_data = json.loads(result.content[0].text) if hasattr(result, 'content') else result
        self._tools_cache = tools_data
        
        return tools_data
    
    async def list_commands(self) -> dict[str, Any]:
        """
        List all available Claude Code slash commands.
        
        Returns:
            Dictionary with command names and descriptions.
            
        Example:
            commands = await explorer.list_commands()
            print(f"Found {len(commands['commands'])} commands")
        """
        session = await self._get_session()
        
        result = await session.call_tool("list_commands", {})
        
        return json.loads(result.content[0].text) if hasattr(result, 'content') else result
    
    # =========================================================================
    # Source Code Access
    # =========================================================================
    
    async def get_tool_source(self, tool_name: str) -> str:
        """
        Get source code for a specific agent tool.
        
        Args:
            tool_name: Name of the tool (e.g., "BashTool", "FileEditTool")
            
        Returns:
            Source code as string.
            
        Example:
            source = await explorer.get_tool_source("BashTool")
            print(source[:500])  # First 500 chars
        """
        session = await self._get_session()
        
        result = await session.call_tool(
            "get_tool_source",
            {"tool_name": tool_name}
        )
        
        return result.content[0].text if hasattr(result, 'content') else str(result)
    
    async def get_command_source(self, command_name: str) -> str:
        """
        Get source code for a specific slash command.
        
        Args:
            command_name: Name of the command (e.g., "/commit", "/review")
            
        Returns:
            Source code as string.
        """
        session = await self._get_session()
        
        result = await session.call_tool(
            "get_command_source",
            {"command_name": command_name}
        )
        
        return result.content[0].text if hasattr(result, 'content') else str(result)
    
    async def read_source_file(self, file_path: str, start_line: int = 1, end_line: int = None) -> str:
        """
        Read a specific source file.
        
        Args:
            file_path: Relative path from src/ (e.g., "tools/BashTool.ts")
            start_line: Starting line number (1-based)
            end_line: Ending line number (optional)
            
        Returns:
            File content as string.
            
        Example:
            content = await explorer.read_source_file("QueryEngine.ts", 1, 100)
        """
        session = await self._get_session()
        
        params = {"file_path": file_path}
        if start_line:
            params["start_line"] = start_line
        if end_line:
            params["end_line"] = end_line
        
        result = await session.call_tool("read_source_file", params)
        
        return result.content[0].text if hasattr(result, 'content') else str(result)
    
    # =========================================================================
    # Source Code Search
    # =========================================================================
    
    async def search_source(self, pattern: str, file_glob: str = None, limit: int = 50) -> dict[str, Any]:
        """
        Search source code with regex pattern.
        
        Args:
            pattern: Regular expression pattern
            file_glob: Optional glob pattern to filter files (e.g., "*.ts", "tools/*")
            limit: Maximum results to return
            
        Returns:
            Dictionary with search results.
            
        Example:
            # Find all permission checks
            results = await explorer.search_source(r"permission.*check")
            
            # Find tool definitions
            results = await explorer.search_source(r"class.*Tool extends", file_glob="tools/*.ts")
        """
        session = await self._get_session()
        
        params = {"pattern": pattern, "limit": limit}
        if file_glob:
            params["file_glob"] = file_glob
        
        result = await session.call_tool("search_source", params)
        
        return json.loads(result.content[0].text) if hasattr(result, 'content') else result
    
    async def list_directory(self, dir_path: str) -> dict[str, Any]:
        """
        List contents of a source directory.
        
        Args:
            dir_path: Relative directory path (e.g., "tools/", "commands/")
            
        Returns:
            Dictionary with directory contents.
        """
        session = await self._get_session()
        
        result = await session.call_tool(
            "list_directory",
            {"dir_path": dir_path}
        )
        
        return json.loads(result.content[0].text) if hasattr(result, 'content') else result
    
    # =========================================================================
    # Architecture & Documentation
    # =========================================================================
    
    async def get_architecture(self) -> dict[str, Any]:
        """
        Get full architecture overview of Claude Code.
        
        Returns:
            Dictionary with architecture documentation.
            
        Example:
            arch = await explorer.get_architecture()
            print(arch['overview'])
            print(f"Tech stack: {arch['tech_stack']}")
        """
        session = await self._get_session()
        
        result = await session.call_tool("get_architecture", {})
        
        return json.loads(result.content[0].text) if hasattr(result, 'content') else result
    
    # =========================================================================
    # High-Level Convenience Methods
    # =========================================================================
    
    async def explain_tool(self, tool_name: str) -> str:
        """
        Get detailed explanation of how a tool works.
        
        Args:
            tool_name: Name of the tool to explain
            
        Returns:
            Formatted explanation string.
        """
        source = await self.get_tool_source(tool_name)
        
        explanation = f"""
# Tool: {tool_name}

## Source Code Location
Found in Claude Code source tree.

## Source Code Preview
```typescript
{source[:2000]}{'...' if len(source) > 2000 else ''}
```

## Analysis
To get a complete explanation, use the MCP prompt:
- Prompt: `explain_tool`
- Arguments: `{{"tool_name": "{tool_name}"}}`

## Related Tools
Use `list_tools()` to discover similar tools.
"""
        return explanation.strip()
    
    async def find_implementation(self, feature: str) -> dict[str, Any]:
        """
        Find where a feature is implemented in the source.
        
        Args:
            feature: Feature description (e.g., "permission check", "file editing")
            
        Returns:
            Search results with locations.
        """
        # Convert feature description to regex patterns
        patterns = [
            feature.lower().replace(" ", ".*"),
            feature.lower().replace(" ", "_"),
            feature.lower().replace(" ", "-"),
        ]
        
        all_results = []
        for pattern in patterns:
            try:
                results = await self.search_source(pattern, limit=20)
                if results and 'matches' in results:
                    all_results.extend(results['matches'])
            except Exception as e:
                logger.debug(f"Pattern '{pattern}' failed: {e}")
        
        return {
            "feature": feature,
            "total_matches": len(all_results),
            "matches": all_results[:50]  # Limit total results
        }
    
    async def compare_tools(self, tool_names: list[str]) -> str:
        """
        Compare multiple tools side-by-side.
        
        Args:
            tool_names: List of tool names to compare
            
        Returns:
            Formatted comparison table.
        """
        tools_info = []
        for name in tool_names:
            try:
                source = await self.get_tool_source(name)
                tools_info.append({"name": name, "source": source[:500]})
            except Exception as e:
                tools_info.append({"name": name, "error": str(e)})
        
        comparison = "# Tool Comparison\n\n"
        comparison += "| Tool | Source Preview |\n"
        comparison += "|------|---------------|\n"
        
        for info in tools_info:
            preview = info.get('source', info.get('error', 'N/A'))
            preview = preview.replace('\n', ' ')[:100]
            comparison += f"| {info['name']} | {preview}... |\n"
        
        return comparison


# =============================================================================
# Piranha Agent Skill Integration
# =============================================================================

def create_claude_explorer_skill():
    """
    Create a piranha-agent skill wrapper for Claude Code Explorer.
    
    Returns:
        Skill instance ready to be added to an agent.
    """
    from piranha_agent.skill import skill
    
    _explorer = None
    
    def get_explorer():
        nonlocal _explorer
        if _explorer is None:
            _explorer = ClaudeCodeExplorer()
        return _explorer
    
    @skill(
        name="claude_code.list_tools",
        description="List all available Claude Code agent tools (40+ tools)",
        auto_monitor=True,
    )
    def list_tools() -> dict:
        """List Claude Code tools."""
        explorer = get_explorer()
        return asyncio.run(explorer.list_tools())
    
    @skill(
        name="claude_code.list_commands",
        description="List all available Claude Code slash commands (50+ commands)",
        auto_monitor=True,
    )
    def list_commands() -> dict:
        """List Claude Code commands."""
        explorer = get_explorer()
        return asyncio.run(explorer.list_commands())
    
    @skill(
        name="claude_code.get_tool_source",
        description="Get source code for a specific Claude Code tool",
        parameters={
            "type": "object",
            "properties": {
                "tool_name": {"type": "string", "description": "Tool name (e.g., 'BashTool')"}
            },
            "required": ["tool_name"],
        },
        auto_monitor=True,
    )
    def get_tool_source(tool_name: str) -> str:
        """Get tool source code."""
        explorer = get_explorer()
        return asyncio.run(explorer.get_tool_source(tool_name))
    
    @skill(
        name="claude_code.search_source",
        description="Search Claude Code source with regex pattern",
        parameters={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern to search for"},
                "file_glob": {"type": "string", "description": "Optional glob pattern (e.g., '*.ts')"},
                "limit": {"type": "integer", "description": "Max results (default: 50)"}
            },
            "required": ["pattern"],
        },
        auto_monitor=True,
    )
    def search_source(pattern: str, file_glob: str = None, limit: int = 50) -> dict:
        """Search source code."""
        explorer = get_explorer()
        return asyncio.run(explorer.search_source(pattern, file_glob, limit))
    
    @skill(
        name="claude_code.get_architecture",
        description="Get full architecture overview of Claude Code",
        auto_monitor=True,
    )
    def get_architecture() -> dict:
        """Get architecture overview."""
        explorer = get_explorer()
        return asyncio.run(explorer.get_architecture())
    
    # Return all skills as a list
    return [list_tools, list_commands, get_tool_source, search_source, get_architecture]


def add_claude_explorer_to_agent(agent):
    """
    Add Claude Code Explorer skills to an existing agent.
    
    Args:
        agent: Agent instance to add skills to
        
    Returns:
        The same agent with explorer skills added
        
    Example:
        from piranha_agent import Agent
        from piranha_agent.claude_code_explorer import add_claude_explorer_to_agent
        
        agent = Agent(name="assistant")
        add_claude_explorer_to_agent(agent)
        
        # Now agent has all 5 Claude Code Explorer skills
        result = agent.run("List all Claude Code tools")
    """
    from piranha_agent.agent import Agent
    
    if not isinstance(agent, Agent):
        raise TypeError(f"Expected Agent instance, got {type(agent)}")
    
    for skill in create_claude_explorer_skill():
        agent.add_skill(skill)
    
    return agent


# =============================================================================
# CLI for Testing
# =============================================================================

if __name__ == "__main__":
    import sys
    
    async def main():
        """Test Claude Code Explorer."""
        print("=" * 70)
        print("CLAUDE CODE EXPLORER - TEST")
        print("=" * 70)
        print()
        
        if not MCP_AVAILABLE:
            print("❌ MCP not installed. Install with: pip install mcp")
            sys.exit(1)
        
        explorer = ClaudeCodeExplorer()
        
        try:
            # Test 1: List tools
            print("1. Listing tools...")
            tools = await explorer.list_tools()
            print(f"   ✓ Found {len(tools.get('tools', []))} tools")
            
            # Test 2: List commands
            print("2. Listing commands...")
            commands = await explorer.list_commands()
            print(f"   ✓ Found {len(commands.get('commands', []))} commands")
            
            # Test 3: Get architecture
            print("3. Getting architecture overview...")
            arch = await explorer.get_architecture()
            print(f"   ✓ Got architecture info")
            
            # Test 4: Search source
            print("4. Searching source for 'class.*Tool'...")
            results = await explorer.search_source(r"class.*Tool", limit=10)
            print(f"   ✓ Found {len(results.get('matches', []))} matches")
            
            print()
            print("=" * 70)
            print("ALL TESTS PASSED!")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await explorer.close()
    
    asyncio.run(main())
