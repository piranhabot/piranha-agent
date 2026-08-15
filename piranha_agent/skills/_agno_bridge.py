#!/usr/bin/env python3
"""Shared plumbing for converting Agno toolkits into real Piranha Skills.

Agno's own JSON-schema generation for a Function is lazy - it's deferred to
Agno's own agent loop and comes back empty at Toolkit-construction time - so
this builds schemas directly from each function's type hints and docstring
instead. Not exported as a public API; used internally by github_tools.py,
slack_tools.py, etc.
"""

from __future__ import annotations

import inspect
import logging
import re
from collections.abc import Callable
from typing import Any, get_type_hints

from piranha_agent.skill import Skill

logger = logging.getLogger(__name__)

_JSON_TYPE_MAP: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def parse_docstring(doc: str | None) -> tuple[str, dict[str, str]]:
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


def json_schema_for(func: Callable[..., Any]) -> dict[str, Any] | None:
    """Build a JSON schema for a function from its type hints + docstring.

    Returns None if a required parameter's type can't be confidently mapped
    to a JSON type (e.g. framework-injected objects like Agno's RunContext) -
    callers should skip exposing that function as a skill in that case,
    rather than silently generate a broken schema.
    """
    sig = inspect.signature(func)
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}
    _, descriptions = parse_docstring(func.__doc__)

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

        is_required = param.default is inspect.Parameter.empty
        if base_type not in _JSON_TYPE_MAP and is_required:
            return None

        prop: dict[str, Any] = {"type": _JSON_TYPE_MAP.get(base_type, "string")}
        if name in descriptions:
            prop["description"] = descriptions[name]
        properties[name] = prop

        if is_required:
            required.append(name)

    return {"type": "object", "properties": properties, "required": required}


def skills_from_agno_toolkit(
    toolkit: Any,
    *,
    name_prefix: str,
    permission: str,
    write_operations: set[str],
) -> list[Skill]:
    """Convert every function on an Agno toolkit into a Piranha Skill.

    Functions whose required parameters can't be represented in a JSON
    schema (e.g. Agno's own framework-injected RunContext) are skipped
    with a debug log rather than exposed as broken skills.
    """
    skills: list[Skill] = []
    for name, tool_function in toolkit.get_functions().items():
        entrypoint = tool_function.entrypoint
        schema = json_schema_for(entrypoint)
        if schema is None:
            logger.debug(
                "Skipping %s%s: has a required parameter that isn't representable "
                "in a JSON schema (likely a framework-injected argument)",
                name_prefix,
                name,
            )
            continue

        summary, _ = parse_docstring(entrypoint.__doc__)
        skills.append(
            Skill(
                name=f"{name_prefix}{name}",
                description=summary or f"{name_prefix}{name}",
                function=entrypoint,
                parameters_schema=schema,
                required_permissions=[permission],
                requires_confirmation=name in write_operations,
            )
        )
    return skills
