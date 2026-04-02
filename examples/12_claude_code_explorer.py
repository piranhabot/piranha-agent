#!/usr/bin/env python3
"""Claude Code Explorer Example.

Demonstrates exploring Claude Code's 512K+ lines of source code
using the Piranha Agent framework.

Requirements:
    pip install mcp

Usage:
    python examples/12_claude_code_explorer.py
"""

import asyncio

from piranha_agent import Agent, Task
from piranha_agent.claude_code_explorer import ClaudeCodeExplorer, create_claude_explorer_skill


async def explore_directly():
    """Use Claude Code Explorer directly."""
    print("=" * 70)
    print("CLAUDE CODE EXPLORER - DIRECT USAGE")
    print("=" * 70)
    print()
    
    explorer = ClaudeCodeExplorer()
    
    try:
        # 1. List all tools
        print("1. 📦 Listing all Claude Code agent tools...")
        tools = await explorer.list_tools()
        print(f"   ✓ Found {len(tools.get('tools', []))} tools")
        
        # Show first 5 tools
        for i, tool in enumerate(tools.get('tools', [])[:5], 1):
            print(f"      {i}. {tool.get('name', 'Unknown')}: {tool.get('description', 'N/A')[:60]}...")
        print()
        
        # 2. List all commands
        print("2. ⌨️  Listing all Claude Code slash commands...")
        commands = await explorer.list_commands()
        print(f"   ✓ Found {len(commands.get('commands', []))} commands")
        
        # Show first 5 commands
        for i, cmd in enumerate(commands.get('commands', [])[:5], 1):
            print(f"      {i}. {cmd.get('name', 'Unknown')}: {cmd.get('description', 'N/A')[:60]}...")
        print()
        
        # 3. Get architecture overview
        print("3. 🏗️  Getting architecture overview...")
        arch = await explorer.get_architecture()
        print("   ✓ Got architecture documentation")
        if 'overview' in arch:
            print(f"      Overview: {arch['overview'][:100]}...")
        print()
        
        # 4. Search source code
        print("4. 🔍 Searching source for 'class.*Tool extends'...")
        results = await explorer.search_source(r"class.*Tool extends", limit=10)
        matches = results.get('matches', [])
        print(f"   ✓ Found {len(matches)} tool class definitions")
        
        for i, match in enumerate(matches[:3], 1):
            file_path = match.get('path', 'Unknown')
            line_num = match.get('line', '?')
            print(f"      {i}. {file_path}:{line_num}")
        print()
        
        # 5. Get specific tool source
        print("5. 📄 Getting BashTool source code...")
        try:
            source = await explorer.get_tool_source("BashTool")
            lines = source.split('\n')
            print(f"   ✓ Got BashTool source: {len(lines)} lines")
            print("      Preview (first 5 lines):")
            for i, line in enumerate(lines[:5], 1):
                print(f"        {i}. {line[:80]}")
        except Exception as e:
            print(f"   ⚠️  BashTool not found: {e}")
        print()
        
        print("=" * 70)
        print("✅ EXPLORATION COMPLETE!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await explorer.close()


def explore_with_agent():
    """Use Claude Code Explorer via Piranha Agent."""
    print()
    print("=" * 70)
    print("CLAUDE CODE EXPLORER - AGENT USAGE")
    print("=" * 70)
    print()
    
    # Create agent with Claude Code Explorer skills
    explorer_skills = create_claude_explorer_skill()
    
    agent = Agent(
        name="claude-explorer",
        model="ollama/llama3:latest",
        description="Explores Claude Code source code",
        skills=explorer_skills,
    )
    
    print("Created agent with Claude Code Explorer skills:")
    for skill in explorer_skills:
        print(f"  - {skill.name}: {skill.description}")
    print()
    
    # Run task to list tools
    print("Running task: 'List all available Claude Code tools'...")
    task = Task(
        description="List all available Claude Code tools and show the first 5",
        agent=agent,
    )
    
    try:
        result = task.run()
        print(f"✓ Result: {str(result)[:200]}...")
    except Exception as e:
        print(f"⚠️  Task execution: {e}")
    
    print()
    print("=" * 70)
    print("✅ AGENT EXPLORATION COMPLETE!")
    print("=" * 70)


def main():
    """Main entry point."""
    print()
    print("🦈 PIRANHA AGENT + CLAUDE CODE EXPLORER 🦈")
    print()
    print("This example demonstrates:")
    print("  1. Direct usage of ClaudeCodeExplorer class")
    print("  2. Usage via Piranha Agent with skills")
    print()
    print("Prerequisites:")
    print("  - pip install mcp")
    print("  - Access to Claude Code MCP server (auto-installed via npx)")
    print()
    
    input("Press Enter to start exploration...")
    print()
    
    # Run async exploration
    asyncio.run(explore_directly())
    
    # Run agent-based exploration
    explore_with_agent()
    
    print()
    print("🎉 All examples completed!")
    print()
    print("Next steps:")
    print("  - Try searching for specific features: explorer.search_source('pattern')")
    print("  - Get tool source: await explorer.get_tool_source('BashTool')")
    print("  - Explore architecture: await explorer.get_architecture()")
    print()


if __name__ == "__main__":
    main()
