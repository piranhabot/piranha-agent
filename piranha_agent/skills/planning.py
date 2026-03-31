#!/usr/bin/env python3
"""Planning Skill for Piranha Agent.

Enables agents to draft and manage a PLAN.md file for complex tasks,
enforcing a 'Plan-First' architectural workflow.
"""

import os
from piranha_agent.skill import skill

@skill(
    name="draft_plan",
    description="Draft or update a PLAN.md file to outline the strategy for a task.",
    parameters={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "The Markdown content of the plan."},
            "filename": {"type": "string", "description": "The name of the plan file (defaults to PLAN.md)."}
        },
        "required": ["content"]
    },
    requires_confirmation=True # User MUST approve the plan
)
def draft_plan(content: str, filename: str = "PLAN.md") -> str:
    """Skill to draft a plan file."""
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"Plan successfully written to {filename}. Please review the file and approve execution."
    except Exception as e:
        return f"Error writing plan: {str(e)}"

@skill(
    name="get_plan",
    description="Read the current PLAN.md to check progress.",
    parameters={
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "The name of the plan file."}
        }
    }
)
def get_plan(filename: str = "PLAN.md") -> str:
    """Skill to read the plan file."""
    if not os.path.exists(filename):
        return f"No plan found at {filename}. Use 'draft_plan' first."
    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading plan: {str(e)}"
