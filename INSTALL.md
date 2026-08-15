# Installation Guide

This document describes how to install and set up the Piranha Agent.

## Prerequisites

- **Python**: 3.10 or higher.
- **Rust**: Latest stable version (required for building the core).
- **Other Dependencies**: `pip`, `maturin`.

## Standard Installation

To install the latest stable version of Piranha Agent, run:

```bash
pip install piranha-agent
```

## Claude Code Explorer (Optional)

To use the Claude Code Explorer features:

```bash
pip install "piranha-agent[claude-explorer]"
```

This installs the `mcp` package required for Model Context Protocol support.

## Skill Integrations (Optional)

Real GitHub, Slack, and Google Sheets skills (see [skills.md](skills.md)):

```bash
pip install "piranha-agent[github]"        # GitHub issues/PRs/branches/files
pip install "piranha-agent[slack]"         # Slack messaging/channels
pip install "piranha-agent[google-sheets]" # Google Sheets read/write
```

Or install everything (dev tools + all optional extras) with:

```bash
pip install "piranha-agent[all]"
```

## Development Installation

If you want to contribute or build from source:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/piranhabot/piranha-agent.git
    cd piranha-agent
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install in Editable Mode**:
    ```bash
    pip install -e ".[dev]"
    ```

4.  **Build the Rust Core**:
    ```bash
    maturin develop
    ```

## Troubleshooting

- **Rust Compilation Issues**: Ensure `rustc` and `cargo` are in your `PATH`.
- **Python Version**: Verify you are using Python 3.10+.
