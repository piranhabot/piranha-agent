from piranha_agent.skills.slack_tools import get_slack_skills


def test_returns_real_skill_objects():
    skills = get_slack_skills(token="xoxb-dummy")
    assert len(skills) >= 9
    names = [s.name for s in skills]
    assert "slack_send_message" in names
    assert "slack_list_channels" in names


def test_message_operations_require_confirmation():
    skills = {s.name: s for s in get_slack_skills(token="xoxb-dummy")}
    assert skills["slack_send_message"].requires_confirmation is True
    assert skills["slack_upload_file"].requires_confirmation is True
    assert skills["slack_list_channels"].requires_confirmation is False
    assert skills["slack_get_channel_history"].requires_confirmation is False


def test_all_skills_require_slack_permission():
    skills = get_slack_skills(token="xoxb-dummy")
    assert all(s.required_permissions == ["slack"] for s in skills)


def test_run_context_tool_is_skipped_not_broken():
    # search_workspace takes a framework-injected RunContext Piranha can't
    # supply - it must be excluded entirely rather than exposed with a
    # bogus schema.
    names = [s.name for s in get_slack_skills(token="xoxb-dummy")]
    assert "slack_search_workspace" not in names


def test_schema_reflects_real_function_signature():
    skills = {s.name: s for s in get_slack_skills(token="xoxb-dummy")}
    schema = skills["slack_send_message"].parameters_schema
    assert schema["properties"]["channel"]["type"] == "string"
    assert schema["properties"]["text"]["type"] == "string"
    assert set(schema["required"]) == {"channel", "text"}


def test_missing_dependency_gives_install_hint(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("agno.tools.slack"):
            raise ImportError("No module named 'agno'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        get_slack_skills(token="xoxb-dummy")
        raise AssertionError("expected ImportError")
    except ImportError as e:
        assert "piranha-agent[slack]" in str(e)
