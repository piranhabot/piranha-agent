#!/usr/bin/env python3
"""Real GitHub API skills for Piranha agents, powered by Agno's GithubTools.

Piranha's own `git_workflows` skill only ever returned a canned markdown
template - it never actually called GitHub's API despite claiming to manage
"PRs and collaboration". This module wraps Agno's real GithubTools toolkit
(create/list/comment on issues and PRs, branches, files, etc.) as genuine
Piranha Skill objects.

Requires the `github` extra: pip install "piranha-agent[github]"
"""

from __future__ import annotations

from piranha_agent.skill import Skill
from piranha_agent.skills._agno_bridge import skills_from_agno_toolkit

_INSTALL_HINT = (
    "GitHub skills require the 'github' extra. Install with: "
    "pip install \"piranha-agent[github]\""
)

# Operations that mutate GitHub state - require human confirmation before running.
_WRITE_OPERATIONS = {
    "create_issue",
    "create_repository",
    "delete_repository",
    "create_pull_request",
    "create_file",
    "update_file",
    "delete_file",
    "create_branch",
    "set_default_branch",
    "close_issue",
    "reopen_issue",
    "assign_issue",
    "label_issue",
    "edit_issue",
    "comment_on_issue",
    "create_pull_request_comment",
    "edit_pull_request_comment",
    "create_review_request",
}


def get_github_skills(access_token: str | None = None) -> list[Skill]:
    """Build real Piranha Skills from Agno's GithubTools toolkit.

    Args:
        access_token: GitHub personal access token. Falls back to Agno's own
            default resolution (e.g. GITHUB_ACCESS_TOKEN env var) if omitted.

    Returns:
        List of Skill objects, one per GitHub operation (create_issue,
        list_pull_requests, create_branch, etc.). Write operations are
        marked requires_confirmation=True.
    """
    try:
        from agno.tools.github import GithubTools
    except ImportError as e:
        raise ImportError(_INSTALL_HINT) from e

    toolkit = GithubTools(access_token=access_token)
    return skills_from_agno_toolkit(
        toolkit,
        name_prefix="github_",
        permission="github",
        write_operations=_WRITE_OPERATIONS,
    )
