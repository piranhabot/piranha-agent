#!/usr/bin/env python3
"""Real Google Sheets skills for Piranha agents, powered by Agno's GoogleSheetsTools.

Requires the `google-sheets` extra: pip install "piranha-agent[google-sheets]"

Google's OAuth flow needs more setup than a single token (unlike GitHub/
Slack): either a service account JSON key (service_account_path) or an
OAuth client's credentials.json + a token.json produced by an interactive
consent flow (credentials_path/token_path). See Agno's GoogleSheetsTools
docs for how to obtain these.
"""

from __future__ import annotations

from piranha_agent.skill import Skill
from piranha_agent.skills._agno_bridge import skills_from_agno_toolkit

_INSTALL_HINT = (
    "Google Sheets skills require the 'google-sheets' extra. Install with: "
    "pip install \"piranha-agent[google-sheets]\""
)

# Operations that mutate spreadsheet state - require human confirmation before running.
_WRITE_OPERATIONS = {
    "create_sheet",
    "update_sheet",
    "create_duplicate_sheet",
}


def get_google_sheets_skills(
    spreadsheet_id: str | None = None,
    service_account_path: str | None = None,
    credentials_path: str | None = None,
    token_path: str | None = None,
) -> list[Skill]:
    """Build real Piranha Skills from Agno's GoogleSheetsTools toolkit.

    Args:
        spreadsheet_id: Default spreadsheet to operate on. Individual
            skill calls can still pass their own spreadsheet_id.
        service_account_path: Path to a Google service account JSON key
            (recommended for unattended/agent use - no interactive login).
        credentials_path: Path to an OAuth client credentials.json, for
            interactive user-consent auth instead of a service account.
        token_path: Path to store/reuse the OAuth token when using
            credentials_path.

    Returns:
        List of Skill objects (read_sheet, create_sheet, update_sheet,
        create_duplicate_sheet). Write operations are marked
        requires_confirmation=True.
    """
    try:
        from agno.tools.google.sheets import GoogleSheetsTools
    except ImportError as e:
        raise ImportError(_INSTALL_HINT) from e

    toolkit = GoogleSheetsTools(
        spreadsheet_id=spreadsheet_id,
        service_account_path=service_account_path,
        credentials_path=credentials_path,
        token_path=token_path,
        all=True,
    )
    return skills_from_agno_toolkit(
        toolkit,
        name_prefix="google_sheets_",
        permission="google_sheets",
        write_operations=_WRITE_OPERATIONS,
    )
