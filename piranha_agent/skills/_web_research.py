"""Shared web research helpers for skills that need to do real work.

Used by article_extractor, deep_research, and lead_research_assistant -
all three previously returned canned markdown templates with the caller's
input echoed back and no actual search or fetch behind them.
"""

from html.parser import HTMLParser

import httpx
from piranha_agent.skill import validate_url

_USER_AGENT = "Mozilla/5.0 (compatible; PiranhaAgent/1.0; +https://github.com/piranhabot/piranha-agent)"


class _TextExtractor(HTMLParser):
    """Minimal, dependency-free HTML-to-text extractor.

    This strips tags and script/style/nav/footer content and keeps visible
    text - it is not a readability-quality extractor (no ad/boilerplate
    detection), just enough to turn a fetched page into skimmable text
    without adding a heavy new dependency.
    """

    _SKIP_TAGS = frozenset({"script", "style", "nav", "footer", "header"})

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._in_title = False
        self.title = ""
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # noqa: ARG002
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title = text
        elif self._skip_depth == 0:
            self.chunks.append(text)


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Run a real DuckDuckGo web search. No API key required.

    Raises ImportError with an install hint if the `ddgs` package isn't
    installed. Returns an empty list if the search runs but finds nothing -
    callers should treat that as "no results," not "search failed."
    """
    try:
        from ddgs import DDGS
    except ImportError as e:
        raise ImportError(
            "Web search requires the 'ddgs' package. Install with: pip install ddgs"
        ) from e

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    return [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "snippet": r.get("body", ""),
        }
        for r in results
    ]


def fetch_url_text(url: str, max_chars: int = 6000, timeout: float = 10.0) -> dict:
    """Fetch a URL over real HTTP and extract basic title/text.

    Respects the calling agent's `allowed_hosts` egress policy via
    validate_url() - same guard used elsewhere in the framework.
    """
    validate_url(url)

    response = httpx.get(
        url,
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": _USER_AGENT},
    )
    response.raise_for_status()

    parser = _TextExtractor()
    parser.feed(response.text)
    text = " ".join(" ".join(parser.chunks).split())

    return {
        "url": url,
        "title": parser.title,
        "text": text[:max_chars],
        "truncated": len(text) > max_chars,
    }
