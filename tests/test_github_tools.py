from piranha_agent.skills.github_tools import get_github_skills


def test_returns_real_skill_objects():
    skills = get_github_skills(access_token="dummy")
    assert len(skills) > 30
    names = [s.name for s in skills]
    assert "github_create_issue" in names
    assert "github_get_repository" in names


def test_write_operations_require_confirmation():
    skills = {s.name: s for s in get_github_skills(access_token="dummy")}
    assert skills["github_create_issue"].requires_confirmation is True
    assert skills["github_delete_repository"].requires_confirmation is True
    assert skills["github_get_repository"].requires_confirmation is False
    assert skills["github_list_repositories"].requires_confirmation is False


def test_all_skills_require_github_permission():
    skills = get_github_skills(access_token="dummy")
    assert all(s.required_permissions == ["github"] for s in skills)


def test_schema_reflects_real_function_signature():
    skills = {s.name: s for s in get_github_skills(access_token="dummy")}
    schema = skills["github_create_issue"].parameters_schema
    assert schema["type"] == "object"
    assert "repo_name" in schema["properties"]
    assert "title" in schema["properties"]
    assert "body" in schema["properties"]
    assert schema["properties"]["repo_name"]["type"] == "string"
    assert "repo_name" in schema["required"]
    assert "title" in schema["required"]
    assert "body" not in schema["required"]  # has a default value


def test_pull_request_number_typed_as_integer():
    skills = {s.name: s for s in get_github_skills(access_token="dummy")}
    schema = skills["github_get_pull_request"].parameters_schema
    assert schema["properties"]["pr_number"]["type"] == "integer"


def test_descriptions_are_populated():
    skills = get_github_skills(access_token="dummy")
    for skill in skills:
        assert skill.description, f"{skill.name} has an empty description"


def test_missing_dependency_gives_install_hint(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "agno.tools.github" or name.startswith("agno.tools.github"):
            raise ImportError("No module named 'agno'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        get_github_skills(access_token="dummy")
        raise AssertionError("expected ImportError")
    except ImportError as e:
        assert "piranha-agent[github]" in str(e)
