#!/usr/bin/env python3
"""Piranha CLI.

Usage:
    piranha-agent debug    - Launch Time-Travel Debugger
    piranha-agent agent    - Create an agent
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


if __name__ == "__main__":
    main()
