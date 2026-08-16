"""Regression tests for the 6 remaining skills found to have zero real I/O
in the full 46-skill audit (git-workflows, file-organizer, youtube-transcript,
reddit-fetch, imagen, competitive-ads-extractor).

reddit-fetch and imagen are mocked throughout (no live Reddit app / image-gen
API key available in this environment) - unlike the other skills fixed this
session, they have NOT been live-verified against the real service, only
against the documented API shape. Say so plainly rather than implying equal
confidence.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from piranha_agent.complete_claude_skills import (
    competitive_ads_extractor,
    imagen,
    reddit_fetch,
    youtube_transcript,
)
from piranha_agent.official_claude_skills import file_organizer, git_workflows
from piranha_agent.skill import agent_permissions


@pytest.fixture(autouse=True)
def _permissions():
    token = agent_permissions.set(["file_write", "network_read", "external_api"])
    yield
    agent_permissions.reset(token)


class TestGitWorkflows:
    def test_requires_confirmation(self):
        assert git_workflows.requires_confirmation is True

    def test_status_runs_real_git_command(self):
        result = git_workflows("status", repo_path=".")
        assert "git status --short --branch" in result
        assert "[status would be checked here]" not in result.lower()

    def test_pr_redirects_to_real_github_skill(self):
        result = git_workflows("pr")
        assert "github_create_pull_request" in result

    def test_merge_without_branch_is_rejected(self):
        result = git_workflows("merge")
        assert "❌" in result
        assert "branch" in result.lower()

    def test_unknown_action_is_rejected(self):
        result = git_workflows("nonsense")
        assert "❌" in result


class TestFileOrganizer:
    @pytest.fixture
    def populated_dir(self):
        tmpdir = tempfile.mkdtemp()
        (Path(tmpdir) / "a.pdf").write_text("x")
        (Path(tmpdir) / "b.jpg").write_text("x")
        yield tmpdir

    def test_dry_run_does_not_move_files(self, populated_dir):
        file_organizer(populated_dir, strategy="by-type", dry_run=True)
        assert (Path(populated_dir) / "a.pdf").exists()
        assert not (Path(populated_dir) / "documents").exists()

    def test_execution_actually_moves_files(self, populated_dir):
        result = file_organizer(populated_dir, strategy="by-type", dry_run=False)
        assert "Files moved: 2" in result
        assert (Path(populated_dir) / "documents" / "a.pdf").exists()
        assert (Path(populated_dir) / "images" / "b.jpg").exists()
        assert not (Path(populated_dir) / "a.pdf").exists()

    def test_by_project_strategy_is_honestly_unimplemented(self, populated_dir):
        result = file_organizer(populated_dir, strategy="by-project")
        assert "❌" in result
        assert "not implemented" in result.lower()

    def test_nonexistent_directory_gives_clear_error(self):
        result = file_organizer("/tmp/definitely_not_a_real_dir_piranha")
        assert "❌" in result


class TestYoutubeTranscript:
    def test_fetches_real_segments_not_placeholder(self):
        fake_snippet = MagicMock(start=5.0, text="Hello world")
        mock_api = MagicMock()
        mock_api.fetch.return_value = [fake_snippet]
        with patch("youtube_transcript_api.YouTubeTranscriptApi", return_value=mock_api):
            result = youtube_transcript("https://www.youtube.com/watch?v=abc123")
        assert "Hello world" in result
        assert "[Transcript would be fetched here]" not in result
        assert "[Point 1]" not in result

    def test_summarize_does_not_fabricate_bullets(self):
        mock_api = MagicMock()
        mock_api.fetch.return_value = [MagicMock(start=0.0, text="content")]
        with patch("youtube_transcript_api.YouTubeTranscriptApi", return_value=mock_api):
            result = youtube_transcript("https://youtu.be/abc123", summarize=True)
        assert "no LLM access" in result

    def test_missing_dependency_gives_install_hint(self, monkeypatch):
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "youtube_transcript_api":
                raise ImportError("no module")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        result = youtube_transcript("https://youtu.be/abc123")
        assert "pip install youtube-transcript-api" in result


class TestRedditFetch:
    """Mocked only - no live Reddit app credentials available this session."""

    def test_missing_credentials_gives_clear_error(self, monkeypatch):
        monkeypatch.delenv("PIRANHA_REDDIT_CLIENT_ID", raising=False)
        monkeypatch.delenv("PIRANHA_REDDIT_CLIENT_SECRET", raising=False)
        result = reddit_fetch("python")
        assert "❌" in result
        assert "PIRANHA_REDDIT_CLIENT_ID" in result

    def test_uses_real_submission_data_not_placeholders(self, monkeypatch):
        monkeypatch.setenv("PIRANHA_REDDIT_CLIENT_ID", "fake_id")
        monkeypatch.setenv("PIRANHA_REDDIT_CLIENT_SECRET", "fake_secret")

        fake_submission = MagicMock()
        fake_submission.title = "Real Post Title"
        fake_submission.author = "real_user"
        fake_submission.score = 42
        fake_submission.num_comments = 7
        fake_submission.permalink = "/r/python/comments/abc/real_post/"

        mock_reddit = MagicMock()
        mock_reddit.subreddit.return_value.hot.return_value = [fake_submission]

        with patch("praw.Reddit", return_value=mock_reddit):
            result = reddit_fetch("python", sort="hot")

        assert "Real Post Title" in result
        assert "u/real_user" in result
        assert "[Post title]" not in result

    def test_search_used_when_query_given(self, monkeypatch):
        monkeypatch.setenv("PIRANHA_REDDIT_CLIENT_ID", "fake_id")
        monkeypatch.setenv("PIRANHA_REDDIT_CLIENT_SECRET", "fake_secret")

        mock_reddit = MagicMock()
        mock_sub = mock_reddit.subreddit.return_value
        mock_sub.search.return_value = []

        with patch("praw.Reddit", return_value=mock_reddit):
            reddit_fetch("python", query="async", sort="top")

        mock_sub.search.assert_called_once_with("async", sort="top", limit=10)


class TestImagen:
    """Mocked only - no live image-gen API key available this session."""

    def test_missing_api_key_gives_clear_error(self):
        with patch("litellm.image_generation", side_effect=Exception("auth error")):
            result = imagen("a red fox")
        assert "❌" in result

    def test_uses_real_response_not_placeholder(self):
        mock_response = MagicMock()
        mock_response.data = [{"url": "https://example.com/generated.png"}]
        with patch("litellm.image_generation", return_value=mock_response) as mock_gen:
            result = imagen("a red fox", style="watercolor")
        assert "https://example.com/generated.png" in result
        assert "[Image would be generated here" not in result
        assert "watercolor" in mock_gen.call_args.kwargs["prompt"]

    def test_model_configurable_via_env_var(self, monkeypatch):
        monkeypatch.setenv("PIRANHA_IMAGE_MODEL", "gemini/imagen-3.0-generate-002")
        mock_response = MagicMock()
        mock_response.data = [{"url": "https://example.com/x.png"}]
        with patch("litellm.image_generation", return_value=mock_response) as mock_gen:
            imagen("a cat")
        assert mock_gen.call_args.kwargs["model"] == "gemini/imagen-3.0-generate-002"


class TestCompetitiveAdsExtractor:
    def test_uses_real_search_results_and_discloses_limitation(self):
        fake_results = [{"title": "Ad Strategy Article", "url": "https://x.com/a", "snippet": "..."}]
        with patch(
            "piranha_agent.skills._web_research.web_search", return_value=fake_results
        ) as mock_search:
            result = competitive_ads_extractor(["Acme"], platform="google")

        assert mock_search.call_args.args[0] == "Acme google advertising campaign"
        assert "Ad Strategy Article" in result
        assert "not ad-library data" in result.lower()
        assert "[count]" not in result
