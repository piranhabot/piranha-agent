from typing import Any

from piranha_agent.skill import agent_permissions
from piranha_agent.skills._agno_bridge import (
    json_schema_for,
    parse_docstring,
    skills_from_agno_toolkit,
)


class _FakeContext:
    """Stand-in for a framework-injected type like Agno's RunContext."""


def test_json_schema_for_basic_types():
    def fn(name: str, count: int, ratio: float, active: bool) -> str:
        """Do a thing.

        Args:
            name: The name.
            count: How many.
            ratio: A ratio.
            active: Whether active.
        """
        return "ok"

    schema = json_schema_for(fn)
    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["count"]["type"] == "integer"
    assert schema["properties"]["ratio"]["type"] == "number"
    assert schema["properties"]["active"]["type"] == "boolean"
    assert schema["properties"]["name"]["description"] == "The name."
    assert set(schema["required"]) == {"name", "count", "ratio", "active"}


def test_json_schema_for_optional_param_not_required():
    def fn(required_arg: str, optional_arg: str | None = None) -> str:
        """Do a thing.

        Args:
            required_arg: Required.
            optional_arg: Optional.
        """
        return "ok"

    schema = json_schema_for(fn)
    assert schema["required"] == ["required_arg"]
    assert schema["properties"]["optional_arg"]["type"] == "string"


def test_json_schema_for_nested_generic_list_resolves_to_array():
    """Regression test: List[List[Any]] (and similar nested generics) used
    to fall through to the "unsupported type" path since the old code only
    compared against bare `list`/`dict`, not generic origins - silently
    dropping any tool with a parameter shaped like this (e.g. Google
    Sheets' update_sheet(data: List[List[Any]]))."""

    def fn(data: list[list[Any]]) -> str:
        """Do a thing.

        Args:
            data: A 2D grid.
        """
        return "ok"

    schema = json_schema_for(fn)
    assert schema is not None
    assert schema["properties"]["data"]["type"] == "array"
    assert "data" in schema["required"]


def test_json_schema_for_optional_nested_generic_resolves_to_array():
    def fn(data: list[list[Any]] | None = None) -> str:
        """Do a thing.

        Args:
            data: Optional 2D grid.
        """
        return "ok"

    schema = json_schema_for(fn)
    assert schema is not None
    assert schema["properties"]["data"]["type"] == "array"
    assert schema["required"] == []


def test_json_schema_for_returns_none_for_unsupported_required_type():
    def fn(ctx: _FakeContext, name: str) -> str:
        """Do a thing needing a framework-injected context.

        Args:
            ctx: Injected by the framework, not user-suppliable.
            name: The name.
        """
        return "ok"

    assert json_schema_for(fn) is None


def test_json_schema_for_ignores_self():
    class Thing:
        def method(self, name: str) -> str:
            """Do a thing.

            Args:
                name: The name.
            """
            return "ok"

    schema = json_schema_for(Thing().method)
    assert "self" not in schema["properties"]


def test_parse_docstring_summary_and_args():
    summary, descriptions = parse_docstring(
        """Create an issue.

        Args:
            repo_name: The repo.
            title: The title.

        Returns:
            A string.
        """
    )
    assert summary == "Create an issue."
    assert descriptions == {"repo_name": "The repo.", "title": "The title."}


def test_parse_docstring_handles_none():
    assert parse_docstring(None) == ("", {})


class _FakeToolFunction:
    def __init__(self, entrypoint):
        self.entrypoint = entrypoint


class _FakeToolkit:
    def __init__(self, functions):
        self._functions = functions

    def get_functions(self):
        return self._functions


def test_skills_from_agno_toolkit_skips_unsupported_and_flags_writes():
    def do_write(name: str) -> str:
        """Write something.

        Args:
            name: The name.
        """
        return "written"

    def do_read(name: str) -> str:
        """Read something.

        Args:
            name: The name.
        """
        return "read"

    def unsupported(ctx: _FakeContext) -> str:
        """Needs an injected context."""
        return "n/a"

    toolkit = _FakeToolkit({
        "do_write": _FakeToolFunction(do_write),
        "do_read": _FakeToolFunction(do_read),
        "unsupported": _FakeToolFunction(unsupported),
    })

    skills = skills_from_agno_toolkit(
        toolkit,
        name_prefix="test_",
        permission="test_perm",
        write_operations={"do_write"},
    )

    names = {s.name for s in skills}
    assert names == {"test_do_write", "test_do_read"}

    by_name = {s.name: s for s in skills}
    assert by_name["test_do_write"].requires_confirmation is True
    assert by_name["test_do_read"].requires_confirmation is False
    assert all(s.required_permissions == ["test_perm"] for s in skills)

    token = agent_permissions.set(["test_perm"])
    try:
        assert by_name["test_do_read"](name="x") == "read"
    finally:
        agent_permissions.reset(token)
