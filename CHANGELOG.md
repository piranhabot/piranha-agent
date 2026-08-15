# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

A pass through the codebase and docs found a recurring pattern: several
features looked finished (real API, real tests passing, real docs) but
were actually no-op stubs or fake implementations underneath. Each one
below was replaced with a genuinely working implementation, not just a
passing test.

### Fixed

- **`DynamicSkillCompiler.compile_and_execute()`** decoded base64 input and
  reported a hardcoded `success=True` with the byte count as "output" -
  it never executed anything. Now genuinely runs the decoded Wasm module.
- **`PostgresEventStore`** never connected to a database: `new()` silently
  discarded the connection string and always used hardcoded defaults,
  `connected` was permanently `false`, and it had no append/query methods
  at all. Replaced with a real `deadpool-postgres`-backed implementation
  of the same `EventStore` trait `SqliteEventStore` uses, verified
  end-to-end against a live PostgreSQL instance.
- **`AgentOrchestrator.register_worker()` / `get_cluster_status()`** were
  no-ops/hardcoded strings in the Python bindings even though the
  underlying Rust methods were real and tested - the binding just never
  called them. `submit_task()` had no backend at all. Added a real task
  queue (`submit_task`, `assign_task_to_worker`, `auto_assign`,
  `complete_task`) with priority ordering and capacity limits.
- **`SemanticCache.compute_embedding()` (Rust)** used SHA-256 hashing as a
  placeholder "embedding" with no actual semantic meaning, so fuzzy
  matching could never work for related-but-differently-worded prompts.
  Now uses real embeddings via a local Ollama instance
  (`nomic-embed-text`), with a hash-based fallback if Ollama isn't
  reachable.
- **`MemoryManager`'s embedding model (Python)** had the identical bug -
  defaulted to the same fake hash-based provider, so every agent's memory
  search was non-semantic. Also fixed a related correctness bug: the
  Ollama provider returned `None` on any failure and that `None` was
  stored directly as a memory's embedding with no downstream check.
- **No-code builder's "Run" button** just showed a toast
  ("Workflow execution started!") and never executed anything. Now
  genuinely runs the generated workflow as a subprocess and shows real
  output. Fixed two more bugs this surfaced in the generated code itself:
  it called a nonexistent `Task.run_async()` (the real method is sync,
  `Task.run()`) and read a nonexistent `TaskResult.content` (the real
  field is `.result`).
- `create_provider()` passed `api_key`/`api_base` both explicitly and via
  `**kwargs`, causing a `TypeError` that broke Anthropic/OpenAI/Gemini/
  Ollama provider construction.
- `WasmRunner.execute()` / `execute_with_io()` passed the caller's `input`
  string as the Wasm function name instead of `function_name`, so
  execution always failed with "Function '<input>' not found".
- `Agent`/`AsyncAgent` silently ignored any `max_tokens` setting - always
  stuck at the hardcoded default of 2048 with no way to override it.
- A permanently-leaked `unittest.mock` patch in one test
  (`Agent.run = mock_run` inside a `with MagicMock()` block, which never
  restores it) was silently corrupting other tests that ran afterward in
  the same process - root cause of two "flaky" test failures.
- The Rust test suite (`cargo test`) had apparently never compiled
  successfully before: `event_store.rs`'s own test module was missing an
  import.
- **`register_complete_claude_skills()`** claimed (in its docstring and
  every doc referencing it) to register "ALL Claude skills," but only
  combined the official (16) + additional (16) sets - the 14 skills in
  `claude_skills.py` (`analyze_data`, `generate_code`, `debug_code`,
  etc.) were silently dropped. Found while auditing the skills docs for
  stale counts. Now returns the full 46.

### Added

- `check_model_compatibility` skill - checks whether an LLM will run on
  the current machine's hardware before pulling it (wraps the
  `llm-checker` CLI).
- 39 real GitHub skills (create/list issues and PRs, branches, file ops)
  via Agno's `GithubTools`, replacing a `git_workflows` skill that only
  ever returned a canned markdown template.
- 10 real Slack skills (send messages, read channels, upload files) via
  Agno's `SlackTools`.
- 4 real Google Sheets skills (read/create/update sheets, duplicate
  sheets) via Agno's `GoogleSheetsTools`.

### Removed

- `piranha_agent/embeddings.py` - a second, unused, near-duplicate
  implementation of the same embedding provider classes `memory.py` had
  its own separate copy of. Consolidated on `memory.py`'s version.
- `nocode_builder.py`'s own `create_builder_ui()` - a completely unused
  duplicate Gradio UI with the identical fake "Run" button bug.
  `nocode_builder_app.py`'s version (which imports the shared data/logic
  functions from `nocode_builder.py`) is the one actually exported.

### Security

- Closed all 17 open Dependabot alerts across `studio/` and
  `debugger_ui/` (Next.js, PostCSS, sharp, nanoid, brace-expansion,
  js-yaml).
- **Piranha Studio's HTTP REST API had zero authentication** despite a
  fully-built JWT/API-key auth system already covering WebSocket
  connections - all 35 `/api/*` routes in `piranha_agent/realtime.py`
  accepted unauthenticated requests. Applied `authenticate_http_request`
  as a dependency to every route except `/api/health`, with a dev-mode
  bypass for credential-free local requests (wrong credentials are still
  always rejected). See `docs/SECURITY_HARDENING.md`.

### Documentation

- README badges and benchmark numbers were stale/inconsistent (test
  count, a "Security: A+" badge with no real scan behind it, a
  `SemanticCache Put` throughput number that was measuring the fake hash
  embedding). Corrected to match verified, current state.
- The framework comparison table was fact-checked against current docs
  for DeepAgents, Microsoft Agent Framework, AutoGen, Semantic Kernel,
  LangGraph, CrewAI, LlamaIndex, Haystack, Agno, AgentScope, and Agency
  Swarm. Removed "AgentGen," a framework that could not be found to
  exist anywhere. `docs/FRAMEWORK_COMPARISON.md`,
  `docs/MICROSOFT_FRAMEWORK_COMPARISON.md`, and
  `docs/COMPARISON_SCORES.md` had extensive fabricated numbers (specific
  throughput/memory/3-year-TCO figures for every competitor, a claimed
  "Tested on M2 MacBook Pro, 32GB RAM" methodology that never happened) -
  removed rather than "corrected," since there was no real measurement
  behind them to correct to.
- Audited every `.md` file in the repo against current code.
  `docs/SECURITY_HARDENING.md` claimed a "10/10 Enterprise Ready" score
  that was false at the time of writing (see the HTTP auth gap above).
  `GETTING_STARTED.md`, `RULES.md`, and `skills/SKILLS.md` each
  contained a code example that would raise on the first line
  (`Agent.run()` used as if async, a nonexistent `Agent(parent=...)`
  kwarg, an import from the wrong module). The repo's GitHub org was
  wrong in nine files including `pyproject.toml`/`Cargo.toml`/
  `mkdocs.yml`'s own metadata. `cookbook/README.md` and `studio/README.md`
  referenced nonexistent methods and the old `piranha` package name.
  Several docs linked to `docs/OBSERVABILITY.md`/`docs/MEMORY.md`, which
  don't exist. Full list of files touched in the commit history around
  August 2026.

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
