#!/usr/bin/env python3
"""Real GitHub API skills for Piranha agents, powered by Agno's GithubTools.

Piranha's own `git_workflows` skill only ever returned a canned markdown
template - it never actually called GitHub's API despite claiming to manage
"PRs and collaboration". This module wraps Agno's real GithubTools toolkit
(create/list/comment on issues and PRs, branches, files, etc.) as genuine
Piranha Skill objects.

Requires the `github` extra: pip install "piranha-agent[github]"
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable
from typing import Any, get_type_hints

from piranha_agent.skill import Skill

_INSTALL_HINT = (
    "GitHub skills require the 'github' extra. Install with: "
    "pip install \"piranha-agent[github]\""
)

_JSON_TYPE_MAP: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}

# Operations that mutate GitHub state - require human confirmation before running.
_WRITE_OPERATIONS = {
    "create_issue",
    "create_repository",
    "delete_repository",
    "create_pull_request",
    "create_file",
    "update_file",
    "delete_file",
    "create_branch",
    "set_default_branch",
    "close_issue",
    "reopen_issue",
    "assign_issue",
    "label_issue",
    "edit_issue",
    "comment_on_issue",
    "create_pull_request_comment",
    "edit_pull_request_comment",
    "create_review_request",
}


def _parse_docstring(doc: str | None) -> tuple[str, dict[str, str]]:
    """Split a Google-style docstring into (summary, {param: description})."""
    if not doc:
        return "", {}

    lines = doc.strip().splitlines()
    summary = lines[0].strip() if lines else ""

    descriptions: dict[str, str] = {}
    in_args = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Args:"):
            in_args = True
            continue
        if stripped.startswith(("Returns:", "Raises:", "Yields:", "Examples:")):
            in_args = False
            continue
        if in_args and stripped:
            match = re.match(r"(\w+)\s*(?:\([^)]*\))?\s*:\s*(.*)", stripped)
            if match:
                descriptions[match.group(1)] = match.group(2)
    return summary, descriptions


def _json_schema_for(func: Callable[..., Any]) -> dict[str, Any]:
    """Build a JSON schema for a function from its type hints + docstring."""
    sig = inspect.signature(func)
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}
    _, descriptions = _parse_docstring(func.__doc__)

    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue

        py_type = hints.get(name, str)
        base_type = py_type
        args = getattr(py_type, "__args__", None)
        if args:
            non_none = [a for a in args if a is not type(None)]
            if non_none:
                base_type = non_none[0]

        prop: dict[str, Any] = {"type": _JSON_TYPE_MAP.get(base_type, "string")}
        if name in descriptions:
            prop["description"] = descriptions[name]
        properties[name] = prop

        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {"type": "object", "properties": properties, "required": required}


def get_github_skills(access_token: str | None = None) -> list[Skill]:
    """Build real Piranha Skills from Agno's GithubTools toolkit.

    Args:
        access_token: GitHub personal access token. Falls back to Agno's own
            default resolution (e.g. GITHUB_ACCESS_TOKEN env var) if omitted.

    Returns:
        List of Skill objects, one per GitHub operation (create_issue,
        list_pull_requests, create_branch, etc.). Write operations are
        marked requires_confirmation=True.
    """
    try:
        from agno.tools.github import GithubTools
    except ImportError as e:
        raise ImportError(_INSTALL_HINT) from e

    toolkit = GithubTools(access_token=access_token)

    skills = []
    for name, tool_function in toolkit.get_functions().items():
        entrypoint = tool_function.entrypoint
        summary, _ = _parse_docstring(entrypoint.__doc__)
        skills.append(
            Skill(
                name=f"github_{name}",
                description=summary or f"GitHub: {name}",
                function=entrypoint,
                parameters_schema=_json_schema_for(entrypoint),
                required_permissions=["github"],
                requires_confirmation=name in _WRITE_OPERATIONS,
            )
        )
    return skills
