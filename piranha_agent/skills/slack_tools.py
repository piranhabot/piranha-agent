#!/usr/bin/env python3
"""Real Slack API skills for Piranha agents, powered by Agno's SlackTools.

Requires the `slack` extra: pip install "piranha-agent[slack]"
"""

from __future__ import annotations

from piranha_agent.skill import Skill
from piranha_agent.skills._agno_bridge import skills_from_agno_toolkit

_INSTALL_HINT = (
    "Slack skills require the 'slack' extra. Install with: "
    "pip install \"piranha-agent[slack]\""
)

# Operations that post/mutate Slack state - require human confirmation before running.
_WRITE_OPERATIONS = {
    "send_message",
    "send_message_thread",
    "upload_file",
}


def get_slack_skills(token: str | None = None) -> list[Skill]:
    """Build real Piranha Skills from Agno's SlackTools toolkit.

    Args:
        token: Slack bot token (xoxb-...). Falls back to Agno's own default
            resolution (e.g. SLACK_TOKEN env var) if omitted.

    Returns:
        List of Skill objects (send_message, list_channels,
        get_channel_history, upload_file, etc.). Message-sending/upload
        operations are marked requires_confirmation=True. Tools whose
        parameters can't be represented in a JSON schema (e.g. Agno's
        framework-injected RunContext, used by search_workspace) are
        skipped rather than exposed broken.
    """
    try:
        from agno.tools.slack import SlackTools
    except ImportError as e:
        raise ImportError(_INSTALL_HINT) from e

    toolkit = SlackTools(token=token, all=True)
    return skills_from_agno_toolkit(
        toolkit,
        name_prefix="slack_",
        permission="slack",
        write_operations=_WRITE_OPERATIONS,
    )
