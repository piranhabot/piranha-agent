# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.2] - 2026-04-01

### Added
- **Architecture-First Workflow (Plan Mode)**: New `plan_first` parameter for `run_autonomous()` method.
  - Agents must draft PLAN.md before executing code-changing skills
  - Human-in-the-Loop approval required via `draft_plan` skill
  - Enforces architectural thinking before implementation
- **Planning Skills** (`piranha_agent/skills/planning.py`):
  - `draft_plan`: Write architectural strategy to PLAN.md (requires confirmation)
  - `get_plan`: Retrieve and review current strategy
- **Adaptive System Directives**: Dynamic system prompt updates for Plan Mode
- **Resilient Initialization**: Fixed crashes when agent initialized without system prompt
- **Claude Code Explorer**: Explore Claude Code's 512K+ lines of source code via MCP.
  - 5 new skills: `list_tools`, `list_commands`, `get_tool_source`, `search_source`, `get_architecture`
  - Access to 40+ Claude Code agent tools and 50+ slash commands
  - Regex search across entire codebase
  - Architecture documentation retrieval
- **CLI Command**: `piranha-agent explore` for quick source code exploration.
- **Convenience Function**: `add_claude_explorer_to_agent()` for easy skill integration.
- **Swarm Collaboration**: Multi-agent exploration with shared state and message bus.
- **MCP Integration**: Full Model Context Protocol support for external tool servers.

### Changed
- Updated `__init__.py` to export Claude Code Explorer components.
- Added `mcp>=1.0.0` as optional dependency (`[claude-explorer]` extra).
- Enhanced `run_autonomous()` with `plan_first` parameter for strict planning workflow.

### Documentation
- Added `docs/CLAUDE_CODE_EXPLORER.md` - Complete user guide.
- Added `docs/CLAUDE_CODE_QUICKSTART.md` - Quick reference.
- Added `docs/CLAUDE_CODE_SWARM.md` - Swarm collaboration guide.
- Added `examples/12_claude_code_explorer.py` - Basic usage example.
- Added `examples/13_claude_code_swarm.py` - Multi-agent swarm examples.
- Added `examples/15_claude_code_explorer_working.py` - Working implementation.
- Updated planning and architecture documentation across all guides.

### Tests
- Added `tests/test_claude_code_explorer.py` with 12 unit tests.

## [0.4.1] - 2026-04-01

### Added
- **Piranha Studio**: A real-time monitoring dashboard for agent activity.
- **No-Code Builder**: Visual interface for building agent workflows.
- **Wasm Sandboxing**: Enhanced security using `wasmtime` for tool execution.
- **46+ Claude Skills**: Pre-built skills for common tasks.
- **Observability**: OpenTelemetry integration for tracing and monitoring.
- **PostgreSQL Backend**: Production-ready event persistence.
- **Distributed Agents**: Support for multi-process agent collaboration.
- **Semantic Cache**: Fuzzy matching for LLM response caching.

### Changed
- Improved security hardening with fail-closed API verification.
- Updated to Python 3.12+ compatibility.
- Replaced hardcoded default `SECRET_KEY` with environment-based configuration.

### Fixed
- Resolved 96 code quality findings.
- Fixed ReDoS vulnerabilities in regex patterns.
- Fixed thread-safety issues in concurrent tests.
- Fixed WebSocket authentication bugs.

## [0.1.0] - 2025-10-01
### Added
- Initial release with Python SDK and Rust core.
- Event sourcing foundations.
