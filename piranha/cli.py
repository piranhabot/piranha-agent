#!/usr/bin/env python3
"""Piranha CLI.

Usage:
    piranha debug    - Launch Time-Travel Debugger
    piranha agent    - Create an agent
    piranha version  - Show version
"""

import click


@click.group()
@click.version_option(version="0.4.0")
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
@click.option(
    "--model",
    default=None,
    help="LLM model (defaults to ollama/llama3:latest if not specified)",
)
@click.option("--ollama", is_flag=True, help="Use local Ollama (sets a default model if none is specified)")
def agent(name: str, model: str | None, ollama: bool) -> None:
    """Create and test an agent."""
    from piranha import Agent
    
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
    click.echo("  Python SDK: v0.4.0")
    click.echo(f"  Rust Core: v{piranha_core.__version__}")
    click.echo("  Features: LiteLLM, Async, Memory, Wasm, Time-Travel Debug")


if __name__ == "__main__":
    main()
