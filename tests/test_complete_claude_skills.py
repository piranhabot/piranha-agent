from piranha_agent.claude_skills import get_all_claude_skills
from piranha_agent.complete_claude_skills import (
    get_all_additional_claude_skills,
    get_complete_claude_skills,
    register_complete_claude_skills,
)
from piranha_agent.official_claude_skills import get_all_official_claude_skills


def test_get_complete_claude_skills_includes_core_claude_skills():
    """Regression test: get_complete_claude_skills() used to only combine
    official + additional skills, silently dropping the 14 skills in
    claude_skills.py (analyze_data, generate_code, debug_code, etc.)
    despite its docstring promising "ALL Claude skills"."""
    complete = get_complete_claude_skills()
    core = get_all_claude_skills()
    complete_names = {s.name for s in complete}
    core_names = {s.name for s in core}
    assert core_names.issubset(complete_names)


def test_get_complete_claude_skills_count_matches_all_three_sources():
    complete = get_complete_claude_skills()
    core = get_all_claude_skills()
    official = get_all_official_claude_skills()
    additional = get_all_additional_claude_skills()
    assert len(complete) == len(core) + len(official) + len(additional)


def test_get_complete_claude_skills_has_no_duplicate_names():
    complete = get_complete_claude_skills()
    names = [s.name for s in complete]
    assert len(names) == len(set(names))


def test_register_complete_claude_skills_registers_core_skill():
    from piranha_agent import Agent

    agent = Agent(name="skills-test-agent")
    register_complete_claude_skills(agent)
    names = {s.name for s in agent.skills}
    assert "analyze_data" in names
    assert "docx" in names
