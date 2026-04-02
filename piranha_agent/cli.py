#!/usr/bin/env python3
"""Piranha CLI.

Usage:
    piranha-agent debug    - Launch Time-Travel Debugger
    piranha-agent agent    - Create an agent
    piranha-agent explore  - Explore Claude Code source
    piranha-agent version  - Show version
"""

import click

from piranha_agent import __version__


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Piranha Agent CLI."""
    pass


@main.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to (default: localhost)")
@click.option("--port", default=7860, help="Port to bind to")
@click.option(
    "--browser/--no-browser",
    default=True,
    help="Automatically open the debugger UI in a web browser",
)
def debug(host: str, port: int, browser: bool) -> None:
    """Launch the Time-Travel Debugger UI."""
    from piranha_agent.debugger import create_ui
    
    click.echo(f"🚀 Launching Piranha Time-Travel Debugger at http://{host}:{port}")
    ui = create_ui()
    ui.launch(server_name=host, server_port=port, inbrowser=browser)


@main.command()
@click.option("--name", default="assistant", help="Agent name")
@click.option(
    "--model",
    default=None,
    help="LLM model (defaults to ollama/llama3:latest if not specified)",
)
@click.option("--ollama", is_flag=True, help="Use local Ollama with default model")
def agent(name: str, model: str | None, ollama: bool) -> None:
    """Create and test an agent."""
    from piranha_agent import Agent
    
    # Determine final model based on flags and user input.
    if ollama and model is None:
        model = "ollama/llama3:latest"
        click.echo("🦙 Using Ollama (make sure it's running!)")
    elif model is None:
        # Preserve previous behavior where, in the absence of any flags,
        # the default model is ollama/llama3:latest.
        model = "ollama/llama3:latest"
    
    agent = Agent(name=name, model=model)
    click.echo(f"✓ Created agent '{name}'")
    click.echo(f"  ID: {agent.id}")
    click.echo(f"  Model: {model}")
    
    # Interactive chat
    click.echo("\n💬 Chat with the agent (type 'quit' to exit):")
    while True:
        user_input = click.prompt("You", prompt_suffix="> ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        
        response = agent.chat(user_input)
        click.echo(f"\n🤖 {agent.name}: {response}\n")
    
    # Show cost report
    cost = agent.get_cost_report()
    if cost:
        click.echo(f"\n💰 Session cost: ${cost.get('total_cost_usd', 0):.4f}")


@main.command()
def version() -> None:
    """Show version information."""
    import piranha_core

    click.echo("🐍 Piranha Agent")
    click.echo(f"  Python SDK: v{__version__}")
    click.echo(f"  Rust Core: v{piranha_core.__version__}")
    click.echo("  Features: LiteLLM, Async, Memory, Wasm, Time-Travel Debug")


@main.command()
@click.option("--tool", "-t", default=None, help="Get source code for a specific tool")
@click.option("--command", "-c", default=None, help="Get source code for a specific command")
@click.option("--search", "-s", default=None, help="Search source with regex pattern")
@click.option("--architecture", "-a", is_flag=True, help="Get architecture overview")
@click.option("--list-tools", is_flag=True, help="List all Claude Code tools")
@click.option("--list-commands", is_flag=True, help="List all Claude Code commands")
def explore(tool, command, search, architecture, list_tools, list_commands):
    """Explore Claude Code source code."""
    import asyncio

    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer
    
    if not any([tool, command, search, architecture, list_tools, list_commands]):
        click.echo("❌ No action specified. Use one of:")
        click.echo("  --tool <name>       Get tool source code")
        click.echo("  --command <name>    Get command source code")
        click.echo("  --search <pattern>  Search source code")
        click.echo("  --architecture      Get architecture overview")
        click.echo("  --list-tools        List all tools")
        click.echo("  --list-commands     List all commands")
        return
    
    async def run_exploration():
        explorer = ClaudeCodeExplorer()
        try:
            if list_tools:
                click.echo("📦 Listing Claude Code tools...")
                tools = await explorer.list_tools()
                tool_list = tools.get('tools', [])
                click.echo(f"✓ Found {len(tool_list)} tools\n")
                for i, t in enumerate(tool_list[:10], 1):
                    name = t.get('name', 'Unknown')
                    desc = t.get('description', 'N/A')[:60]
                    click.echo(f"  {i}. {name}: {desc}...")
                if len(tool_list) > 10:
                    click.echo(f"  ... and {len(tool_list) - 10} more")
            
            elif list_commands:
                click.echo("⌨️  Listing Claude Code commands...")
                commands = await explorer.list_commands()
                cmd_list = commands.get('commands', [])
                click.echo(f"✓ Found {len(cmd_list)} commands\n")
                for i, c in enumerate(cmd_list[:10], 1):
                    name = c.get('name', 'Unknown')
                    desc = c.get('description', 'N/A')[:60]
                    click.echo(f"  {i}. {name}: {desc}...")
                if len(cmd_list) > 10:
                    click.echo(f"  ... and {len(cmd_list) - 10} more")
            
            elif architecture:
                click.echo("🏗️  Getting architecture overview...")
                arch = await explorer.get_architecture()
                click.echo("✓ Architecture retrieved\n")
                if 'overview' in arch:
                    click.echo(arch['overview'][:500])
            
            elif tool:
                click.echo(f"📄 Getting source for tool: {tool}...")
                source = await explorer.get_tool_source(tool)
                lines = source.split('\n')
                click.echo(f"✓ Got {len(lines)} lines\n")
                click.echo("First 10 lines:")
                for i, line in enumerate(lines[:10], 1):
                    click.echo(f"  {i:3}. {line[:80]}")
            
            elif command:
                click.echo(f"📄 Getting source for command: {command}...")
                source = await explorer.get_command_source(command)
                lines = source.split('\n')
                click.echo(f"✓ Got {len(lines)} lines\n")
                click.echo("First 10 lines:")
                for i, line in enumerate(lines[:10], 1):
                    click.echo(f"  {i:3}. {line[:80]}")
            
            elif search:
                click.echo(f"🔍 Searching for: {search}...")
                results = await explorer.search_source(search, limit=20)
                matches = results.get('matches', [])
                click.echo(f"✓ Found {len(matches)} matches\n")
                for i, match in enumerate(matches[:10], 1):
                    path = match.get('path', 'Unknown')
                    line = match.get('line', '?')
                    text = match.get('text', '')[:60]
                    click.echo(f"  {i}. {path}:{line}")
                    click.echo(f"     {text}...")
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            import traceback
            traceback.print_exc()
        finally:
            await explorer.close()
    
    asyncio.run(run_exploration())


if __name__ == "__main__":
    main()
