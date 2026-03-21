#!/usr/bin/env python3
"""Piranha CLI.

Usage:
    piranha debug    - Launch Time-Travel Debugger
    piranha agent    - Create an agent
    piranha version  - Show version
"""

import click


@click.group()
@click.version_option(version="0.2.0")
def main() -> None:
    """Piranha Agent CLI."""
    pass


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=7860, help="Port to bind to")
def debug(host: str, port: int) -> None:
    """Launch the Time-Travel Debugger UI."""
    from piranha.debugger import create_ui
    
    click.echo(f"🚀 Launching Piranha Time-Travel Debugger at http://{host}:{port}")
    ui = create_ui()
    ui.launch(server_name=host, server_port=port, inbrowser=True)


@main.command()
@click.option("--name", default="assistant", help="Agent name")
@click.option("--model", default="ollama/llama3:latest", help="LLM model")
@click.option("--ollama", is_flag=True, help="Use local Ollama")
def agent(name: str, model: str, ollama: bool) -> None:
    """Create and test an agent."""
    from piranha import Agent
    
    if ollama:
        model = "ollama/llama3:latest"
        click.echo("🦙 Using Ollama (make sure it's running!)")
    
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
    click.echo(f"  Python SDK: v0.2.0")
    click.echo(f"  Rust Core: v{piranha_core.__version__}")
    click.echo(f"  Features: LiteLLM, Async, Memory, Wasm, Time-Travel Debug")


if __name__ == "__main__":
    main()
