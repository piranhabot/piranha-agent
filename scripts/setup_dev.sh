#!/usr/bin/env bash
# scripts/setup_dev.sh — One-command development environment setup
#
# Usage: bash scripts/setup_dev.sh

set -euo pipefail

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║      Piranha Agent — Development Setup       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Check prerequisites ───────────────────────────────────────────────────
check_cmd() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ $1 is required but not installed."
        echo "   Install: $2"
        exit 1
    fi
    echo "✓ $1 found"
}

echo "→ Checking prerequisites..."
check_cmd "rustc"   "https://rustup.rs"
check_cmd "cargo"   "https://rustup.rs"
check_cmd "python3" "https://python.org"
check_cmd "pip"     "pip install pip --upgrade"
check_cmd "ollama"  "https://ollama.com"
echo ""

# ── Python virtual environment ────────────────────────────────────────────
echo "→ Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
echo "✓ Virtual env: .venv"
echo ""

# ── Python dependencies ───────────────────────────────────────────────────
echo "→ Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet maturin litellm pydantic httpx rich \
    pytest pytest-asyncio pytest-cov python-dotenv
echo "✓ Python dependencies installed"
echo ""

# ── Install Python SDK ────────────────────────────────────────────────────
echo "→ Installing Piranha Agent Python SDK..."
pip install --quiet -e python_sdk
echo "✓ Python SDK installed"
echo ""

# ── Pull Ollama model ─────────────────────────────────────────────────────
echo "→ Pulling Ollama llama3 model..."
echo "  (This may take a few minutes on first run ~4GB)"
ollama pull llama3
echo "✓ llama3 model ready"
echo ""

# ── Build Rust core ───────────────────────────────────────────────────────
echo "→ Building Rust core (first run takes ~60 seconds)..."
maturin develop --release 2>&1 | tail -5
echo "✓ Rust core compiled"
echo ""

# ── Run Rust tests ────────────────────────────────────────────────────────
echo "→ Running Rust unit tests..."
cargo test --quiet 2>&1 | tail -10
echo ""

# ── Run Python tests ──────────────────────────────────────────────────────
echo "→ Running Python unit tests..."
pytest python_sdk/tests/ -q --no-header 2>&1 | tail -15
echo ""

# ── Summary ───────────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════╗"
echo "║         Piranha Agent Ready! 🐟  ✓           ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "  1. Activate your virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Start Ollama:"
echo "     ollama serve"
echo ""
echo "  3. Run the Hello World example:"
echo "     python examples/example.py"
echo ""
echo "  4. Run all tests:"
echo "     pytest python_sdk/tests/    # Python tests"
echo "     cargo test                  # Rust tests"
echo ""
```

---

**Save with Cmd+S**

---

🎉 **ALL FILES ARE COMPLETE!**
```
✅ Cargo.toml
✅ rust_core/Cargo.toml
✅ rust_core/src/lib.rs
✅ rust_core/src/types.rs
✅ rust_core/src/event_store.rs
✅ rust_core/src/skill_registry.rs
✅ rust_core/src/guardrails.rs
✅ rust_core/src/semantic_cache.rs
✅ rust_core/src/python_bindings.rs
✅ python_sdk/piranha/__init__.py
✅ python_sdk/piranha/skill.py
✅ python_sdk/piranha/guardrail.py
✅ python_sdk/piranha/llm.py
✅ python_sdk/piranha/agent.py
✅ python_sdk/piranha/group_chat.py
✅ python_sdk/tests/conftest.py
✅ python_sdk/tests/test_agent.py
✅ examples/example.py
✅ README.md
✅ pyproject.toml
✅ scripts/setup_dev.sh