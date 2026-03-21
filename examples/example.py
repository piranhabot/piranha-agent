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
        Agent,
        Task,
        Skill,
    )
except ImportError:
    console.print(
        "[red]piranha not found.[/red]\n"
        "Run: pip install -e python_sdk"
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
    skill_id="demo:knowledge_search",
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
    skill_id="demo:calculator",
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

    agent = PiranhaAgent(
        name="ResearchAssistant",
        model=os.getenv("PIRANHA_MODEL", "ollama/llama3"),
        skills=[knowledge_search, calculator],
        guardrails=Guardrail(
            token_budget=5_000,
            warn_at_pct=80,
            rate_limit=30,
        ),
        system_prompt=(
            "You are a research assistant. Use your tools to gather "
            "information and perform calculations. Always use the "
            "calculator tool for math instead of computing in your head."
        ),
    )

    console.print(f"\n[dim]Agent: {agent}[/dim]\n")

    task = Task(
        description=(
            "Search for what Ollama is, then calculate: "
            "if running a model locally saves $0.002 per call "
            "and you make 500 calls per day, how much do you "
            "save per month (30 days)?"
        ),
        expected_output=(
            "Brief explanation of Ollama and the calculated savings."
        ),
        max_iterations=10,
    )

    console.print("[yellow]Running agent...[/yellow]")
    result = await agent.run(task)

    if result.success:
        console.print(Panel(
            result.output,
            title="[green]✓ Agent Output[/green]",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]Error: {result.error}[/red]",
            title="[red]✗ Agent Failed[/red]",
            border_style="red",
        ))

    _print_cost_report(result, agent.name)
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

    agent = PiranhaAgent(
        name="BudgetedAgent",
        model=os.getenv("PIRANHA_MODEL", "ollama/llama3"),
        skills=[knowledge_search],
        guardrails=Guardrail(
            token_budget=200,
            warn_at_pct=50,
        ),
    )

    console.print("[dim]Running agent with 200-token budget...[/dim]\n")

    result = await agent.run(
        "Search for Python, then Rust, then Ollama, "
        "then write a detailed essay comparing all three."
    )

    if not result.success and result.error:
        console.print(Panel(
            f"[yellow]Guardrail stopped the agent:[/yellow]\n"
            f"{result.error}\n\n"
            f"[dim]Tokens used: {result.total_tokens} / 200[/dim]",
            title="[yellow]⚠ Guardrail Triggered[/yellow]",
            border_style="yellow",
        ))
    else:
        console.print(
            f"[green]Completed within budget![/green]\n"
            f"{result.output[:200]}"
        )


# ---------------------------------------------------------------------------
# Demo 3: Time-Travel Trace Export
# ---------------------------------------------------------------------------

async def demo_time_travel():
    console.print(Panel.fit(
        "[bold magenta]Demo 3: Time-Travel Trace Export[/bold magenta]\n"
        "Every action is recorded. Export the full trace as JSON.",
        border_style="magenta",
    ))

    agent = PiranhaAgent(
        name="TracedAgent",
        model=os.getenv("PIRANHA_MODEL", "ollama/llama3"),
        skills=[knowledge_search, calculator],
        guardrails=Guardrail.development(),
    )

    result = await agent.run(
        "Search for Rust then calculate 42 * 7."
    )

    trace_json = agent.export_trace()
    trace = json.loads(trace_json)

    console.print(
        f"\n[magenta]Session ID:[/magenta] {result.session_id}"
    )
    console.print(
        f"[magenta]Events recorded:[/magenta] "
        f"{trace.get('event_count', 0)}"
    )

    trace_path = f"/tmp/piranha_trace_{result.session_id[:8]}.json"
    with open(trace_path, "w") as f:
        f.write(trace_json)

    console.print(Panel(
        f"[green]Trace saved to:[/green] {trace_path}\n\n"
        "[dim]Load this in the Piranha Debugger UI to:\n"
        "  • Visualize the agent decision tree\n"
        "  • See token costs per step\n"
        "  • Click Rewind to roll back to any point[/dim]",
        title="[magenta]Time-Travel Trace[/magenta]",
        border_style="magenta",
    ))

    return trace_path


# ---------------------------------------------------------------------------
# Demo 4: Sub-Agent Spawning
# ---------------------------------------------------------------------------

async def demo_sub_agents():
    console.print(Panel.fit(
        "[bold blue]Demo 4: Sub-Agent Spawning[/bold blue]\n"
        "Parent spawns a child with ONLY the skills it needs.\n"
        "Child cannot access parent's full capability set.",
        border_style="blue",
    ))

    parent = PiranhaAgent(
        name="ParentAgent",
        model=os.getenv("PIRANHA_MODEL", "ollama/llama3"),
        skills=[knowledge_search, calculator],
        guardrails=Guardrail(token_budget=10_000),
    )

    console.print(
        "[dim]Parent has: knowledge_search, calculator[/dim]"
    )
    console.print(
        "[dim]Child will receive: calculator ONLY[/dim]\n"
    )

    child_result = await parent.spawn_sub_agent(
        name="CalculatorChild",
        task="Calculate 15% of 2500, then 8% of that result.",
        skills_to_delegate=["demo:calculator"],
        token_budget=1_000,
    )

    console.print(Panel(
        child_result.output,
        title="[blue]Child Agent Result[/blue]",
        border_style="blue",
    ))
    console.print(
        f"[dim]Child tokens: {child_result.total_tokens}[/dim]"
    )


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