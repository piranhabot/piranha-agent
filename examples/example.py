"""
examples/example.py — Piranha Agent Hello World

Run:
    python examples/example.py
"""

import asyncio
import json
import os

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


# ---------------------------------------------------------------------------
# Install check
# ---------------------------------------------------------------------------

try:
    from piranha import (
        AsyncAgent as Agent,
        Task,
        skill,
    )
except ImportError:
    console.print(
        "[red]piranha not found.[/red]\n"
        "Run: pip install -e ."
    )
    exit(1)


# ---------------------------------------------------------------------------
# Define Skills
# ---------------------------------------------------------------------------

@skill(
    description=(
        "Search a knowledge base for information. "
        "Use for factual questions and research."
    ),
    permissions=["network_read"],
    inheritable=True,
)
async def knowledge_search(query: str, max_results: int = 3) -> str:
    """
    query: The search query (natural language)
    max_results: How many results to return (1-10)
    """
    mock_results = {
        "rust": {
            "title": "The Rust Programming Language",
            "summary": (
                "Rust is a systems programming language focused on "
                "safety, speed, and concurrency. It achieves memory "
                "safety without a garbage collector."
            ),
        },
        "python": {
            "title": "Python Overview",
            "summary": (
                "Python is a high-level language known for its "
                "readability. The Python/Rust combo via PyO3 gives "
                "you both developer experience and raw performance."
            ),
        },
        "ollama": {
            "title": "Ollama — Local LLMs",
            "summary": (
                "Ollama lets you run large language models locally. "
                "No API costs, no data leaving your machine. "
                "Supports llama3, mistral, codellama and more."
            ),
        },
    }

    query_lower = query.lower()
    for key, result in mock_results.items():
        if key in query_lower:
            return json.dumps({
                "query": query,
                "results": [result],
                "source": "demo_knowledge_base",
            }, indent=2)

    return json.dumps({
        "query": query,
        "results": [{
            "title": f"Search results for: {query}",
            "summary": (
                f"Found relevant information about '{query}'."
            ),
        }],
        "source": "demo_knowledge_base",
    }, indent=2)


@skill(
    description=(
        "Perform mathematical calculations. "
        "Use for arithmetic, percentages, and unit conversions. "
        "More reliable than asking the LLM to compute directly."
    ),
    permissions=[],
    inheritable=True,
)
async def calculator(expression: str) -> str:
    """
    expression: A math expression (e.g. '2 + 2', '100 * 0.15')
    """
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression):
        return json.dumps({
            "error": "Invalid characters. Only math allowed."
        })

    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa
        return json.dumps({
            "expression": expression,
            "result": result,
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Demo 1: Single Agent
# ---------------------------------------------------------------------------

async def demo_single_agent():
    console.print(Panel.fit(
        "[bold cyan]Demo 1: Single Agent with Skills[/bold cyan]\n"
        "Agent uses search + calculator to answer a question.",
        border_style="cyan",
    ))

    agent = Agent(
        name="ResearchAssistant",
        model=os.getenv("PIRANHA_MODEL", "ollama/llama3"),
        skills=[knowledge_search, calculator],
        system_prompt=(
            "You are a research assistant. Use your tools to gather "
            "information and perform calculations. Always use the "
            "calculator tool for math instead of computing in your head."
        ),
    )

    console.print(f"\n[dim]Agent: {agent}[/dim]\n")

    description = (
        "Search for what Ollama is, then calculate: "
        "if running a model locally saves $0.002 per call "
        "and you make 500 calls per day, how much do you "
        "save per month (30 days)?"
    )

    console.print("[yellow]Running agent...[/yellow]")
    result = await agent.run(description)

    console.print(Panel(
        result.content,
        title="[green]✓ Agent Output[/green]",
        border_style="green",
    ))

    return result


# ---------------------------------------------------------------------------
# Demo 2: Guardrail Enforcement
# ---------------------------------------------------------------------------

async def demo_guardrails():
    console.print(Panel.fit(
        "[bold yellow]Demo 2: Guardrail Enforcement[/bold yellow]\n"
        "A tight token budget triggers a warning then a hard stop.",
        border_style="yellow",
    ))

    agent = Agent(
        name="BudgetedAgent",
        model=os.getenv("PIRANHA_MODEL", "ollama/llama3"),
        skills=[knowledge_search],
    )

    console.print("[dim]Running agent...[/dim]\n")

    result = await agent.run(
        "Search for Python, then Rust, then Ollama, "
        "then write a detailed essay comparing all three."
    )

    console.print(
        f"[green]Completed![/green]\n"
        f"{result.content[:200]}..."
    )


# ---------------------------------------------------------------------------
# Demo 3: Time-Travel Trace Export
# ---------------------------------------------------------------------------

async def demo_time_travel():
    console.print(Panel.fit(
        "[bold magenta]Demo 3: Time-Travel Trace Export[/bold magenta]\n"
        "Every action is recorded.",
        border_style="magenta",
    ))

    agent = Agent(
        name="TracedAgent",
        model=os.getenv("PIRANHA_MODEL", "ollama/llama3"),
        skills=[knowledge_search, calculator],
    )

    result = await agent.run(
        "Search for Rust then calculate 42 * 7."
    )

    console.print(
        f"[green]Agent output:[/green] {result.content}"
    )


# ---------------------------------------------------------------------------
# Demo 4: Sub-Agent Spawning
# ---------------------------------------------------------------------------

async def demo_sub_agents():
    console.print(Panel.fit(
        "[bold blue]Demo 4: Sub-Agent Execution[/bold blue]\n"
        "Running multiple tasks through the agent.",
        border_style="blue",
    ))

    agent = Agent(
        name="ParentAgent",
        model=os.getenv("PIRANHA_MODEL", "ollama/llama3"),
        skills=[knowledge_search, calculator],
    )

    result = await agent.run("Calculate 15% of 2500, then 8% of that result.")

    console.print(Panel(
        result.content,
        title="[blue]Agent Result[/blue]",
        border_style="blue",
    ))


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _print_cost_report(result, agent_name: str):
    table = Table(
        title=f"[bold]Cost Report — {agent_name}[/bold]",
        show_header=True,
    )
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")

    table.add_row("Total Cost", f"${result.total_cost_usd:.6f}")
    table.add_row("Total Tokens", str(result.total_tokens))
    table.add_row(
        "Cache Savings", f"${result.cache_savings_usd:.6f}"
    )
    table.add_row("Iterations", str(result.iterations))
    table.add_row(
        "Skills Used",
        ", ".join(result.skills_used) or "none",
    )
    table.add_row("Success", "✓" if result.success else "✗")
    console.print(table)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    console.print(Panel.fit(
        "[bold white]Piranha Agent — Hello World[/bold white]\n"
        "[dim]Security-first • Cost-efficient • Time-travel debuggable[/dim]",
        border_style="white",
    ))

    # Check Ollama is running
    console.print(
        "[dim]Make sure Ollama is running: ollama serve[/dim]\n"
    )

    demos = [
        ("Single Agent Run", demo_single_agent),
        ("Guardrail Enforcement", demo_guardrails),
        ("Time-Travel Trace Export", demo_time_travel),
        ("Sub-Agent Least Privilege", demo_sub_agents),
    ]

    for name, demo_fn in demos:
        console.print(f"\n{'─' * 60}")
        try:
            await demo_fn()
        except Exception as e:
            console.print(f"[red]Demo '{name}' failed: {e}[/red]")
            import traceback
            traceback.print_exc()

    console.print(f"\n{'─' * 60}")
    console.print(Panel.fit(
        "[bold green]✓ All demos complete![/bold green]\n\n"
        "[dim]Next steps:\n"
        "  • maturin develop --release  → enable Rust core\n"
        "  • pytest python_sdk/tests    → run test suite\n"
        "  • cargo test                 → run Rust tests[/dim]",
        border_style="green",
    ))


if __name__ == "__main__":
    asyncio.run(main())