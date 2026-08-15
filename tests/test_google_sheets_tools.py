from piranha_agent.skills.google_sheets_tools import get_google_sheets_skills


def test_returns_real_skill_objects():
    skills = get_google_sheets_skills(spreadsheet_id="dummy")
    names = [s.name for s in skills]
    assert "google_sheets_read_sheet" in names
    assert "google_sheets_update_sheet" in names
    assert "google_sheets_create_sheet" in names
    assert "google_sheets_create_duplicate_sheet" in names


def test_write_operations_require_confirmation():
    skills = {s.name: s for s in get_google_sheets_skills(spreadsheet_id="dummy")}
    assert skills["google_sheets_read_sheet"].requires_confirmation is False
    assert skills["google_sheets_create_sheet"].requires_confirmation is True
    assert skills["google_sheets_update_sheet"].requires_confirmation is True
    assert skills["google_sheets_create_duplicate_sheet"].requires_confirmation is True


def test_all_skills_require_google_sheets_permission():
    skills = get_google_sheets_skills(spreadsheet_id="dummy")
    assert all(s.required_permissions == ["google_sheets"] for s in skills)


def test_update_sheet_nested_list_type_resolves_to_array():
    """Regression test: update_sheet's `data: List[List[Any]]` parameter
    used to make json_schema_for() return None (nested generics weren't
    recognized, only bare `list`/`dict`), silently dropping update_sheet -
    the toolkit's only real write operation - from the skill set."""
    skills = {s.name: s for s in get_google_sheets_skills(spreadsheet_id="dummy")}
    schema = skills["google_sheets_update_sheet"].parameters_schema
    assert schema["properties"]["data"]["type"] == "array"
    assert "data" in schema["required"]


def test_missing_dependency_gives_install_hint(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("agno.tools.google"):
            raise ImportError("No module named 'agno'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        get_google_sheets_skills(spreadsheet_id="dummy")
        raise AssertionError("expected ImportError")
    except ImportError as e:
        assert "piranha-agent[google-sheets]" in str(e)
