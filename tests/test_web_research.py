from unittest.mock import MagicMock, patch

import httpx
import pytest
from piranha_agent.skill import agent_allowed_hosts
from piranha_agent.skills._web_research import fetch_url_text, web_search


def test_web_search_returns_expected_shape():
    fake_results = [
        {"title": "Result One", "href": "https://example.com/1", "body": "Snippet one"},
        {"title": "Result Two", "href": "https://example.com/2", "body": "Snippet two"},
    ]
    mock_ddgs = MagicMock()
    mock_ddgs.__enter__.return_value.text.return_value = fake_results
    mock_ddgs.__exit__.return_value = False

    with patch("ddgs.DDGS", return_value=mock_ddgs):
        results = web_search("test query", max_results=2)

    assert results == [
        {"title": "Result One", "url": "https://example.com/1", "snippet": "Snippet one"},
        {"title": "Result Two", "url": "https://example.com/2", "snippet": "Snippet two"},
    ]


def test_web_search_missing_dependency_gives_install_hint(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "ddgs":
            raise ImportError("No module named 'ddgs'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ImportError, match="pip install ddgs"):
        web_search("test query")


def test_fetch_url_text_extracts_title_and_visible_text():
    html = """
    <html><head><title>My Page</title><style>.x{color:red}</style></head>
    <body><nav>Skip me</nav><h1>Hello</h1><p>World content here.</p>
    <script>console.log('skip me too')</script></body></html>
    """
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status.return_value = None

    with patch("httpx.get", return_value=mock_response) as mock_get:
        page = fetch_url_text("https://example.com/page")

    assert page["title"] == "My Page"
    assert "Hello" in page["text"]
    assert "World content here." in page["text"]
    assert "Skip me" not in page["text"]
    assert "console.log" not in page["text"]
    assert mock_get.call_args.kwargs["timeout"] == 10.0


def test_fetch_url_text_truncates_long_text():
    long_text = "word " * 5000
    html = f"<html><body><p>{long_text}</p></body></html>"
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status.return_value = None

    with patch("httpx.get", return_value=mock_response):
        page = fetch_url_text("https://example.com/long", max_chars=100)

    assert len(page["text"]) == 100
    assert page["truncated"] is True


def test_fetch_url_text_respects_allowed_hosts_policy():
    token = agent_allowed_hosts.set(["allowed.example.com"])
    try:
        with pytest.raises(PermissionError, match="Egress blocked"):
            fetch_url_text("https://not-allowed.example.com/page")
    finally:
        agent_allowed_hosts.reset(token)


def test_fetch_url_text_propagates_http_errors():
    with patch("httpx.get", side_effect=httpx.ConnectError("connection failed")):
        with pytest.raises(httpx.ConnectError):
            fetch_url_text("https://unreachable.example.com")
