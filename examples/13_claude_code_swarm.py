#!/usr/bin/env python3
"""Claude Code Explorer + Multi-Agent Swarm example.

This example demonstrates:
- Creating a team of agents with Claude Code Explorer skills
- Using swarm coordination to explore Claude Code collaboratively
- Sharing discoveries via message bus and shared state
- Parallel exploration with multiple agents

Usage:
    python examples/13_claude_code_swarm.py
"""

from piranha_agent import Agent, Task
from piranha_agent.claude_code_explorer import create_claude_explorer_skill
from piranha_agent.orchestration import create_orchestrated_team, Team
from piranha_agent.collaboration import MessageBus, SharedState


def example_1_sequential_exploration():
    """Example 1: Sequential exploration with multiple specialized agents."""
    print("=" * 70)
    print("EXAMPLE 1: SEQUENTIAL EXPLORATION")
    print("=" * 70)
    print()
    
    # Create specialized agents with Claude Code Explorer skills
    tool_researcher = Agent(
        name="tool-researcher",
        model="ollama/llama3:latest",
        description="Discovers and analyzes Claude Code tools",
        skills=create_claude_explorer_skill(),
        system_prompt="You specialize in discovering and analyzing Claude Code tools. Use claude_code.list_tools and claude_code.get_tool_source to explore.",
    )
    
    command_researcher = Agent(
        name="command-researcher",
        model="ollama/llama3:latest",
        description="Discovers and analyzes Claude Code commands",
        skills=create_claude_explorer_skill(),
        system_prompt="You specialize in discovering and analyzing Claude Code commands. Use claude_code.list_commands to explore.",
    )
    
    architecture_analyst = Agent(
        name="architecture-analyst",
        model="ollama/llama3:latest",
        description="Analyzes Claude Code architecture",
        skills=create_claude_explorer_skill(),
        system_prompt="You specialize in analyzing Claude Code architecture. Use claude_code.get_architecture to understand the system design.",
    )
    
    print("Created 3 specialized agents:")
    print(f"  - {tool_researcher.name}: {tool_researcher.description}")
    print(f"  - {command_researcher.name}: {command_researcher.description}")
    print(f"  - {architecture_analyst.name}: {architecture_analyst.description}")
    print()
    
    # Step 1: Discover tools
    print("Step 1: Discovering Claude Code tools...")
    tools_task = Task(
        description="List all Claude Code tools and identify the 5 most important ones for file operations",
        agent=tool_researcher,
    )
    tools_result = tools_task.run()
    print(f"  ✓ Found tools")
    print()
    
    # Step 2: Discover commands
    print("Step 2: Discovering Claude Code commands...")
    commands_task = Task(
        description="List all Claude Code commands and identify the 5 most useful for development workflow",
        agent=command_researcher,
    )
    commands_result = commands_task.run()
    print(f"  ✓ Found commands")
    print()
    
    # Step 3: Analyze architecture
    print("Step 3: Analyzing Claude Code architecture...")
    arch_task = Task(
        description="Get Claude Code architecture overview and explain the tech stack",
        agent=architecture_analyst,
    )
    arch_result = arch_task.run()
    print(f"  ✓ Analyzed architecture")
    print()
    
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"\n🔧 Tools discovered: {len(tools_result.result) if tools_result.result else 'N/A'}")
    print(f"⌨️  Commands discovered: {len(commands_result.result) if commands_result.result else 'N/A'}")
    print(f"🏗️  Architecture analyzed: {'Yes' if arch_result.result else 'No'}")
    print()


def example_2_swarm_collaboration():
    """Example 2: Swarm collaboration with shared state."""
    print()
    print("=" * 70)
    print("EXAMPLE 2: SWARM COLLABORATION WITH SHARED STATE")
    print("=" * 70)
    print()
    
    # Create team with shared environment
    team = Team(
        name="claude-code-explorers",
        coordinator=Agent(
            name="coordinator",
            model="ollama/llama3:latest",
            system_prompt="You coordinate a team exploring Claude Code. Delegate tasks to specialists.",
        ),
        message_bus=MessageBus(),
        shared_state=SharedState(),
    )
    
    # Add specialists with Claude Code Explorer skills
    searcher = Agent(
        name="searcher",
        model="ollama/llama3:latest",
        description="Searches Claude Code source for patterns",
        skills=create_claude_explorer_skill(),
    )
    
    analyzer = Agent(
        name="analyzer",
        model="ollama/llama3:latest",
        description="Analyzes source code found by searcher",
        skills=create_claude_explorer_skill(),
    )
    
    team.add_member(searcher, "searcher")
    team.add_member(analyzer, "analyzer")
    
    print(f"Created team '{team.name}':")
    print(f"  - Coordinator (leads exploration)")
    print(f"  - {searcher.name}: {searcher.description}")
    print(f"  - {analyzer.name}: {analyzer.description}")
    print()
    
    # Shared state for discoveries
    team.shared_state.set("exploration_topic", "permission checking implementation")
    team.shared_state.set("findings", [])
    
    # Step 1: Search for permission checks
    print("Step 1: Searching for permission check implementations...")
    search_task = Task(
        description="Search Claude Code source for 'permission' patterns. Save findings to shared state.",
        agent=searcher,
    )
    search_task.run()  # Result saved to shared state
    print(f"  ✓ Search complete")
    print()
    
    # Step 2: Analyze findings
    print("Step 2: Analyzing permission check patterns...")
    analyze_task = Task(
        description="Analyze the permission check patterns found. Explain how Claude Code implements security.",
        agent=analyzer,
        context=str(team.shared_state.get_all()),
    )
    analyze_task.run()  # Result used via shared state
    print(f"  ✓ Analysis complete")
    print()
    
    print("=" * 70)
    print("SWARM RESULTS")
    print("=" * 70)
    print(f"\n📊 Shared State:")
    for key, value in team.shared_state.get_all().items():
        print(f"  {key}: {str(value)[:100]}...")
    print()


def example_3_orchestrated_swarm():
    """Example 3: Autonomous orchestrated swarm."""
    print()
    print("=" * 70)
    print("EXAMPLE 3: AUTONOMOUS ORCHESTRATED SWARM")
    print("=" * 70)
    print()
    
    # Create orchestrated team
    team = create_orchestrated_team(
        name="claude-code-analysis-team",
        coordinator_model="ollama/llama3:latest",
    )
    
    # Add Claude Code Explorer skills to coordinator
    explorer_skills = create_claude_explorer_skill()
    for skill in explorer_skills:
        team.coordinator.add_skill(skill)
    
    print(f"Created autonomous team '{team.name}'")
    print(f"  Coordinator: {team.coordinator.name}")
    print(f"  Skills: {len(explorer_skills)} Claude Code Explorer skills")
    print()
    
    # Give autonomous task
    print("Task: 'Explore Claude Code and find all file-related tools'")
    print("(Coordinator will autonomously delegate sub-tasks)")
    print()
    
    # Note: This requires the coordinator to have reasoning capabilities
    # For demo purposes, we'll simulate the orchestration
    print("🤖 Autonomous coordination simulation:")
    print("  1. Coordinator receives high-level task")
    print("  2. Uses 'delegate_task' skill to create sub-agents")
    print("  3. Sub-agents explore different aspects")
    print("  4. Results aggregated via message bus")
    print()
    
    # Manual delegation for demo
    print("Manual delegation (for demo):")
    
    # Create sub-agent for tool discovery
    tool_agent = Agent(
        name="tool-discoverer",
        model="ollama/llama3:latest",
        skills=create_claude_explorer_skill(),
    )
    team.add_member(tool_agent, "tool-discoverer")
    
    tool_task = Task(
        description="List all Claude Code tools and filter for file-related ones (File*, file*, etc.)",
        agent=tool_agent,
    )
    tool_task.run()  # Result displayed in output
    print(f"  ✓ Tool discovery complete")
    print()
    
    print("=" * 70)
    print("ORCHESTRATION COMPLETE")
    print("=" * 70)
    print()


def example_4_parallel_exploration():
    """Example 4: Parallel exploration with async agents."""
    print()
    print("=" * 70)
    print("EXAMPLE 4: PARALLEL EXPLORATION (SIMULATED)")
    print("=" * 70)
    print()
    
    import asyncio
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer
    
    async def explore_tools():
        """Async tool exploration."""
        explorer = ClaudeCodeExplorer()
        try:
            tools = await explorer.list_tools()
            return len(tools.get('tools', []))
        finally:
            await explorer.close()
    
    async def explore_commands():
        """Async command exploration."""
        explorer = ClaudeCodeExplorer()
        try:
            commands = await explorer.list_commands()
            return len(commands.get('commands', []))
        finally:
            await explorer.close()
    
    async def explore_architecture():
        """Async architecture exploration."""
        explorer = ClaudeCodeExplorer()
        try:
            arch = await explorer.get_architecture()
            return 'overview' in arch
        finally:
            await explorer.close()
    
    print("Running parallel exploration tasks...")
    print()
    
    # Run all explorations in parallel
    results = asyncio.gather(
        explore_tools(),
        explore_commands(),
        explore_architecture(),
    )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tools_count, commands_count, arch_ok = loop.run_until_complete(results)
    loop.close()
    
    print(f"✓ Parallel exploration complete!")
    print()
    print(f"Results:")
    print(f"  - Tools discovered: {tools_count}")
    print(f"  - Commands discovered: {commands_count}")
    print(f"  - Architecture analyzed: {'✓' if arch_ok else '✗'}")
    print()


def main():
    """Run all examples."""
    print()
    print("🦈 PIRANHA SWARM + CLAUDE CODE EXPLORER 🦈")
    print()
    print("Demonstrating multi-agent collaboration with Claude Code exploration")
    print()
    
    input("Press Enter to start Example 1 (Sequential Exploration)...")
    example_1_sequential_exploration()
    
    input("Press Enter to start Example 2 (Swarm Collaboration)...")
    example_2_swarm_collaboration()
    
    input("Press Enter to start Example 3 (Orchestrated Swarm)...")
    example_3_orchestrated_swarm()
    
    input("Press Enter to start Example 4 (Parallel Exploration)...")
    example_4_parallel_exploration()
    
    print()
    print("=" * 70)
    print("🎉 ALL EXAMPLES COMPLETE!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  1. ✅ Claude Code Explorer skills work with multi-agent teams")
    print("  2. ✅ Shared state enables collaborative discovery")
    print("  3. ✅ Message bus allows async communication")
    print("  4. ✅ Orchestrated swarms can delegate exploration tasks")
    print("  5. ✅ Parallel exploration improves efficiency")
    print()
    print("Next steps:")
    print("  - Customize agent roles for your use case")
    print("  - Add more Claude Code Explorer skills")
    print("  - Integrate with Piranha Studio for monitoring")
    print()


if __name__ == "__main__":
    main()
