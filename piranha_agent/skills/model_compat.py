#!/usr/bin/env python3
"""Model Compatibility Skill for Piranha Agent.

Wraps the `llm-checker` CLI (https://github.com/signerless/llm-checker) so an
agent can check, before pulling anything, whether a given LLM will actually
run on the current machine's hardware.
"""

import json
import shutil
import subprocess

from piranha_agent.skill import skill

_BINARY = "llm-checker"
_INSTALL_HINT = "llm-checker is not installed. Install it with: npm install -g llm-checker"


@skill(
    name="check_model_compatibility",
    description=(
        "Check whether an LLM (by name, e.g. 'qwen3' or 'kimi-k2') can run on this "
        "machine's hardware before pulling/downloading it. Reports detected RAM/GPU, "
        "the best-fitting model variant, its exact download size, and whether it's "
        "cloud-only (too large to run locally)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Model name to search for, e.g. 'qwen3' or 'kimi'."},
            "use_case": {
                "type": "string",
                "description": "Optimize for: general, coding, chat, reasoning, creative (default general).",
            },
        },
        "required": ["query"],
    },
)
def check_model_compatibility(query: str, use_case: str = "general") -> str:
    """Skill to check LLM/hardware compatibility via the llm-checker CLI."""
    if not shutil.which(_BINARY):
        return _INSTALL_HINT

    try:
        proc = subprocess.run(
            [_BINARY, "search", query, "--json", "--limit", "5", "--use-case", use_case],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return f"llm-checker timed out while checking '{query}'."
    except Exception as e:
        return f"Error running llm-checker: {e}"

    if proc.returncode != 0:
        return f"llm-checker failed: {proc.stderr.strip() or proc.stdout.strip()}"

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return f"Could not parse llm-checker output for '{query}'."

    return _format_report(query, data)


def _format_report(query: str, data: dict) -> str:
    hardware = data.get("hardware", {})
    insights = data.get("insights", [])
    top_picks = data.get("topPicks", {})

    lines = [
        f"Hardware: {hardware.get('description', 'unknown')} "
        f"(tier: {hardware.get('tier', '?')}, max comfortable model size: {hardware.get('maxSize', '?')}GB)",
        "",
    ]

    best = top_picks.get("best") if isinstance(top_picks, dict) else None
    if best:
        variant = best.get("variant", {})
        score = best.get("score", {}).get("final")
        size_gb = variant.get("size_gb")
        params_b = variant.get("params_b")
        if size_gb is None:
            detail = "cloud-only, no local download (too large to run on this machine)"
        else:
            params_str = f"{params_b}B params, " if params_b is not None else ""
            detail = f"{params_str}{size_gb}GB"
        lines.append(f"Best match for '{query}': {variant.get('tag', '?')} ({detail}, score: {score})")
    else:
        lines.append(f"No locally runnable variant of '{query}' found for this hardware.")

    for insight in insights:
        prefix = {"warning": "Warning", "success": "OK", "info": "Info"}.get(insight.get("type"), "Note")
        lines.append(f"{prefix}: {insight.get('message', '')}")

    return "\n".join(lines)
