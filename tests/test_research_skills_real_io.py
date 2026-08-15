"""Regression tests for article_extractor/deep_research/lead_research_assistant.

Before this fix these three skills returned canned markdown templates
with the caller's input echoed back and no actual search/fetch behind
them - same pattern as the old git_workflows skill. These tests mock
the underlying web_search/fetch_url_text calls (network isn't mocked at
the httpx/ddgs layer here, that's covered in test_web_research.py) and
assert the skills actually use the results, not just format a template.
"""

from unittest.mock import patch

import pytest
from piranha_agent.complete_claude_skills import deep_research, lead_research_assistant
from piranha_agent.official_claude_skills import article_extractor
from piranha_agent.skill import agent_permissions


@pytest.fixture(autouse=True)
def _network_read_permission():
    token = agent_permissions.set(["network_read"])
    yield
    agent_permissions.reset(token)


def test_article_extractor_requires_network_read_permission():
    token = agent_permissions.set([])
    try:
        with pytest.raises(PermissionError):
            article_extractor("https://example.com")
    finally:
        agent_permissions.reset(token)


def test_article_extractor_uses_real_fetched_content():
    with patch(
        "piranha_agent.skills._web_research.fetch_url_text",
        return_value={"url": "https://example.com", "title": "Real Title", "text": "Real body text.", "truncated": False},
    ) as mock_fetch:
        result = article_extractor("https://example.com")

    mock_fetch.assert_called_once_with("https://example.com")
    assert "Real Title" in result
    assert "Real body text." in result
    assert "[Article title would be extracted here]" not in result


def test_article_extractor_reports_fetch_errors():
    with patch(
        "piranha_agent.skills._web_research.fetch_url_text",
        side_effect=RuntimeError("connection refused"),
    ):
        result = article_extractor("https://unreachable.example.com")

    assert "❌" in result
    assert "connection refused" in result


def test_deep_research_uses_real_search_results():
    fake_results = [
        {"title": "Paper A", "url": "https://a.example.com", "snippet": "Snippet A"},
        {"title": "Paper B", "url": "https://b.example.com", "snippet": "Snippet B"},
    ]
    with patch(
        "piranha_agent.skills._web_research.web_search", return_value=fake_results
    ) as mock_search:
        result = deep_research("quantum computing", depth="shallow")

    mock_search.assert_called_once_with("quantum computing", max_results=3)
    assert "Paper A" in result
    assert "https://a.example.com" in result
    assert "[Research findings would be presented here]" not in result


def test_deep_research_depth_controls_result_count():
    with patch(
        "piranha_agent.skills._web_research.web_search", return_value=[]
    ) as mock_search:
        deep_research("topic", depth="deep")
    mock_search.assert_called_once_with("topic", max_results=10)


def test_deep_research_handles_no_results():
    with patch("piranha_agent.skills._web_research.web_search", return_value=[]):
        result = deep_research("an extremely obscure topic")
    assert "No search results found" in result


def test_lead_research_assistant_uses_real_search_results_not_fabricated_contacts():
    fake_results = [
        {"title": "Acme Corp", "url": "https://acme.example.com", "snippet": "..."},
    ]
    with patch(
        "piranha_agent.skills._web_research.web_search", return_value=fake_results
    ) as mock_search:
        result = lead_research_assistant("robotics", location="Japan")

    assert mock_search.call_args.args[0] == "robotics companies in Japan"
    assert "Acme Corp" in result
    assert "https://acme.example.com" in result
    # Must not present fabricated contact names/emails as if real
    assert "[Name]" not in result
    assert "[Email]" not in result
