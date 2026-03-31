# 🏗️ Piranha Agent Architecture

## 🎯 System Overview

Piranha Agent is a **next-generation autonomous agent framework** built with a hybrid Rust + Python architecture.

**Version:** 0.4.2  
**Status:** Production Ready

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENTS & INTERFACES                        │
├─────────────────────────────────────────────────────────────────┤
│  CLI  │  Piranha Studio  │  No-Code Builder  │  VS Code Ext   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  PYTHON SDK (Orchestration)                     │
├─────────────────────────────────────────────────────────────────┤
│  Agent  │  AsyncAgent  │  Task  │  Collaboration  │  Memory   │
│  Skills │  Planning    │  Security │  Observability │  LLM    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    RUST CORE (Performance)                      │
├─────────────────────────────────────────────────────────────────┤
│  EventStore  │  SkillRegistry  │  GuardrailEngine  │  Wasm    │
│  SemanticCache │  PostgresStore  │  AgentOrchestrator         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│         SQLite (Default)        │       PostgreSQL (Prod)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏆 5 World-Class Pillars

### 1. Autonomous Swarms

Multi-agent collaboration with shared state and message bus.

```python
from piranha_agent.orchestration import create_orchestrated_team

team = create_orchestrated_team("research-team")
# Coordinator delegates to sub-agents
# Shared message bus for communication
# Shared state (whiteboard) for collaboration
```

**Components:**
- `orchestration.py` - Team coordination
- `collaboration.py` - Message bus, shared state
- `AgentOrchestrator` (Rust) - High-performance orchestration

---

### 2. Safety & Spending Brakes

Human-in-the-Loop checkpoints and budget controls.

```python
from piranha_agent import Agent

agent = Agent(
    name="safe-agent",
    plan_first=True,  # Requires HITL approval
    permissions=["read_only"],
    allowed_hosts=["trusted.com"]
)
```

**Components:**
- `skills/planning.py` - `draft_plan` (HITL required)
- `security.py` - Secret masking, egress control
- `GuardrailEngine` (Rust) - Token budget, rate limits
- `WasmRunner` (Rust) - Isolated code execution

---

### 3. Durable State

Event-sourced state with SQLite/PostgreSQL backend.

```python
from piranha_core import EventStore, PostgresEventStore

# SQLite (default)
event_store = EventStore()

# PostgreSQL (production)
event_store = PostgresEventStore("postgresql://...")
```

**Components:**
- `EventStore` (Rust) - 51K+ events/sec
- `PostgresEventStore` (Rust) - Production backend
- `session.py` - Session management

---

### 4. Live Visibility

Real-time monitoring with Piranha Studio.

```python
from piranha_agent.realtime import start_monitoring

monitor = start_monitoring(port=8080)
# Dashboard shows tokens, cost, agent state
```

**Components:**
- `realtime.py` - Real-time monitoring
- `observability.py` - Metrics, alerts
- `studio_dashboard.html` - Web UI

---

### 5. Infinite Context

Semantic cache and context management.

```python
from piranha_agent.memory import MemoryManager
from piranha_core import SemanticCache

memory = MemoryManager()
cache = SemanticCache(ttl_hours=24)  # 1.4M ops/sec
```

**Components:**
- `memory.py` - Memory hierarchy
- `SemanticCache` (Rust) - Fuzzy matching
- `embeddings.py` - Embedding models

---

## 🚀 Unique Features

### Claude Code Explorer (UNIQUE!)

Explore 512K+ lines of Claude Code source.

```python
from piranha_agent import ClaudeCodeExplorer

explorer = ClaudeCodeExplorer()
tools = await explorer.list_tools()  # 8 MCP tools
```

**Components:**
- `claude_code_explorer.py` - Python wrapper
- MCP Server - `/tmp/claude-code/mcp-server/`
- 8 exploration tools

---

### Plan Mode (Architecture-First)

Enforce planning before execution.

```python
agent.run_autonomous(
    task="Build feature",
    plan_first=True  # Drafts PLAN.md first
)
```

**Components:**
- `skills/planning.py` - `draft_plan`, `get_plan`
- `agent.py` - `run_autonomous()` with `plan_first`

---

### Wasm Sandbox (Enterprise Security)

Isolated code execution with Wasmtime.

**Performance:** 7M+ validations/sec

**Components:**
- `WasmRunner` (Rust) - Wasmtime integration
- `security.py` - Permission enforcement

---

## 📦 Complete Component List

### Python SDK (`piranha_agent/`)

| Module | Purpose | Lines |
|--------|---------|-------|
| `agent.py` | Core agent implementation | ~350 |
| `async_agent.py` | Async agent support | ~250 |
| `task.py` | Task management | ~150 |
| `skill.py` | Skill decorator & registry | ~200 |
| `claude_code_explorer.py` | Claude Code integration | ~630 |
| `claude_skills.py` | 46+ Claude skills | ~850 |
| `complete_claude_skills.py` | Additional skills | ~1070 |
| `official_claude_skills.py` | Official Anthropic skills | ~850 |
| `planning.py` | Plan Mode skills | ~60 |
| `orchestration.py` | Multi-agent orchestration | ~200 |
| `collaboration.py` | Message bus, shared state | ~560 |
| `memory.py` | Memory management | ~450 |
| `security.py` | Security utilities | ~250 |
| `observability.py` | Metrics & alerts | ~500 |
| `realtime.py` | Real-time monitoring | ~1200 |
| `llm_provider.py` | LiteLLM integration | ~290 |
| `embeddings.py` | Embedding models | ~270 |
| `session.py` | Session management | ~100 |
| `debugger.py` | Time-travel debugger | ~350 |
| `cli.py` | CLI commands | ~190 |
| `version.py` | Version info | ~5 |

**Total Python:** ~8,500+ lines

---

### Rust Core (`rust_core/`)

| Module | Purpose | Performance |
|--------|---------|-------------|
| `event_store.rs` | Append-only event log | 51K+ events/sec |
| `postgres_store.rs` | PostgreSQL backend | Production-ready |
| `semantic_cache.rs` | Fuzzy matching cache | 1.4M ops/sec |
| `skill_registry.rs` | Skill registration | Sub-millisecond |
| `guardrail_engine.rs` | Token/rate limits | Sub-millisecond |
| `wasm_runner.rs` | Wasmtime integration | 7M+ validations/sec |
| `python_bindings.rs` | PyO3 bindings | - |

**Total Rust:** ~5,000+ lines

---

## 🎯 Skill Registration System

### ALL 53+ Skills Registered

The framework automatically registers all skills when you use the helper functions:

```python
from piranha_agent import (
    Agent,
    register_claude_skills,  # 46+ skills
    register_complete_claude_skills,  # All Claude skills
    create_claude_explorer_skill,  # 5 explorer skills
)

# Method 1: Auto-registration
agent = Agent(name="assistant")
register_complete_claude_skills(agent)  # Registers ALL 53+ skills

# Method 2: Manual skill list
from piranha_agent import create_claude_explorer_skill
agent = Agent(
    name="explorer",
    skills=create_claude_explorer_skill()  # 5 skills
)
```

### Skill Categories

| Category | Count | Registration Function |
|----------|-------|----------------------|
| **Planning** | 2 | `draft_plan`, `get_plan` |
| **Claude Code Explorer** | 5 | `create_claude_explorer_skill()` |
| **Official Claude Skills** | 4 | `register_official_claude_skills()` |
| **Additional Claude Skills** | 42 | `register_additional_claude_skills()` |
| **Core Claude Skills** | ~46 | `register_claude_skills()` |
| **TOTAL** | **53+** | `register_complete_claude_skills()` |

### Skill Files

```
piranha_agent/
├── skills/
│   └── planning.py          # 2 skills (draft_plan, get_plan)
├── claude_skills.py         # ~46 skills
├── official_claude_skills.py # 4 official skills
├── complete_claude_skills.py # 42 additional skills
└── claude_code_explorer.py  # 5 explorer skills
```

---

## 📊 Data Flow

### 1. Agent Execution Flow

```
User Request
    ↓
Agent.run(task)
    ↓
LLM Provider (LiteLLM)
    ↓
Skill Registry (check permissions)
    ↓
Guardrail Engine (check limits)
    ↓
Skill Execution (or Wasm sandbox)
    ↓
Event Store (persist action)
    ↓
Response to User
```

### 2. Plan Mode Flow

```
User Request (plan_first=True)
    ↓
Agent analyzes task
    ↓
draft_plan skill (writes PLAN.md)
    ↓
Human Review (HITL checkpoint)
    ↓
Human approves
    ↓
Agent executes according to plan
    ↓
Progress tracked against milestones
```

### 3. Multi-Agent Swarm Flow

```
Coordinator receives task
    ↓
Delegates to sub-agents via message bus
    ↓
Sub-agents work in parallel
    ↓
Results shared via shared state
    ↓
Coordinator aggregates results
    ↓
Response to User
```

---

## 🔒 Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────┐
│  Layer 1: Permission System             │
│  - Fine-grained skill permissions       │
│  - Context variable enforcement         │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Layer 2: Guardrail Engine (Rust)       │
│  - Token budget enforcement             │
│  - Rate limiting                        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Layer 3: Egress Hardening              │
│  - Host whitelist                       │
│  - URL validation                       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Layer 4: Wasm Sandbox                  │
│  - Memory isolation                     │
│  - CPU/fuel limits                      │
│  - Execution time limits                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Layer 5: Secret Masking                │
│  - Auto-redaction of credentials        │
│  - Keyword masking                      │
└─────────────────────────────────────────┘
```

---

## 📈 Performance Benchmarks

| Operation | Performance | Implementation |
|-----------|-------------|----------------|
| Event Store | 51K+ events/sec | Rust `EventStore` |
| Wasm Validation | 7M+ ops/sec | Rust `WasmRunner` |
| Semantic Cache | 1.4M ops/sec | Rust `SemanticCache` |
| Guardrail Check | Sub-millisecond | Rust `GuardrailEngine` |
| Skill Registry | Sub-millisecond | Rust `SkillRegistry` |

---

## 🎯 Configuration

### Environment Variables

```bash
# Security
SECRET_KEY=your-secret-key-min-32-characters

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Local LLM
OLLAMA_HOST=localhost:11434

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/piranha

# Claude Code Explorer
CLAUDE_CODE_SRC_ROOT=/tmp/claude-code/src
CLAUDE_CODE_MCP_TIMEOUT=30
```

### Agent Configuration

```python
from piranha_agent import Agent

agent = Agent(
    name="assistant",
    model="ollama/llama3:latest",  # or "gpt-4", "claude-3-5-sonnet"
    system_prompt="You are helpful",
    permissions=["read_only"],
    allowed_hosts=["trusted.com"],
    api_base=None,  # For Ollama: "http://localhost:11434"
    api_key=None,   # Or from env
)
```

---

## 📚 Related Documentation

- [WORLD_CLASS_FEATURES.md](WORLD_CLASS_FEATURES.md) - Feature showcase
- [docs/PLAN_MODE.md](docs/PLAN_MODE.md) - Plan Mode guide
- [docs/CLAUDE_CODE_EXPLORER.md](docs/CLAUDE_CODE_EXPLORER.md) - Explorer guide
- [skills.md](skills.md) - Skills documentation
- [skills/CATEGORIZATION.md](skills/CATEGORIZATION.md) - Complete skill catalog
- [docs/SECURITY_HARDENING.md](docs/SECURITY_HARDENING.md) - Security guide
- [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) - Monitoring guide
- [INDEX.md](INDEX.md) - Complete documentation index

---

**Version:** 0.4.2  
**Date:** April 1, 2026  
**Status:** ✅ **PRODUCTION READY**
