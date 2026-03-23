# Contributing to Piranha Agent 🐟

Thank you for your interest in contributing to Piranha! We welcome all contributions, from bug reports and feature requests to documentation improvements and code changes.

## 🛠️ Development Environment Setup

Piranha is a hybrid Rust and Python project. You'll need both toolchains installed.

### Prerequisites
- **Python 3.10+**
- **Rust (stable)**
- **Maturin** (installed via pip)

### Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/piranha-agent/piranha-agent.git
   cd piranha-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the project in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Build the Rust core:
   ```bash
   maturin develop
   ```

## 🧪 Testing

We use `pytest` for testing. Always ensure tests pass before submitting a PR.

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=piranha

# Run only Rust tests
cargo test --manifest-path rust_core/Cargo.toml
```

## 🎨 Coding Standards

### Python
- We use **Ruff** for linting and formatting.
- We use **Mypy** for type checking.
- Follow PEP 8 guidelines.

```bash
# Check linting and formatting
ruff check .
ruff format .

# Run type checking
mypy .
```

### Rust
- Use `cargo fmt` for formatting.
- Use `cargo clippy` for linting.

```bash
cargo fmt --all
cargo clippy --workspace -- -D warnings
```

## 🌿 Branching Policy

- Create a feature branch for your changes: `git checkout -b feature/your-feature-name` or `bugfix/issue-description`.
- Keep your changes focused. Small, modular PRs are easier to review.

## 📝 Pull Request Process

1. **Update Documentation**: If your change adds a feature or changes behavior, update the relevant docs.
2. **Add Tests**: New features must include tests. Bug fixes should include a regression test.
3. **Verify**: Ensure all tests, linting, and type checking pass locally.
4. **Submit**: Create a Pull Request against the `main` branch.
5. **Review**: Maintainers will review your PR. Be prepared to make adjustments based on feedback.

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the project's **MIT OR Apache-2.0** license.
