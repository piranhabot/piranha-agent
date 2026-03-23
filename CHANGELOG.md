# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-23

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
