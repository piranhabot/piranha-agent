# Piranha Agent - Complete Implementation

## 🎉 Phase 3 Complete!

All features from the roadmap have been implemented:

### ✅ Phase 1: Rust Core
- EventStore (append-only audit log)
- SkillRegistry (tool authorization)
- GuardrailEngine (hard limits)
- SemanticCache (cost reduction)

### ✅ Phase 2: Python SDK + Features
- **LiteLLM Integration** - 100+ LLM providers
- **Async Support** - AsyncAgent, AgentGroup
- **Streaming Responses** - Token-by-token streaming
- **Memory/Context** - Vector search, context management

### ✅ Phase 3: Wasm + Time-Travel Debugger
- **Wasm Sandbox** - wasmtime integration
- **WasmRunner** - Memory/CPU limits
- **DynamicSkillCompiler** - Python → Wasm
- **Gradio Debugger** - Time-travel UI

---

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/lakshmana/Desktop/piranha-agent
source .venv/bin/activate
```

### 2. Start Ollama (for local LLM)

```bash
ollama run llama3:latest
```

### 3. Run Examples

```bash
# Basic agent
python examples/01_basic_agent.py

# Skills
python examples/02_skills.py

# Multi-agent
python examples/03_multi_agent.py

# Rust core
python examples/04_rust_core.py

# Ollama local
python examples/05_ollama_local.py

# Complete features demo
python examples/06_complete_features.py
```

### 4. Launch Time-Travel Debugger

```bash
piranha debug
# or
python -c "from piranha import create_debugger_ui; create_debugger_ui().launch()"
```

### 5. CLI Commands

```bash
piranha --help
piranha debug      # Launch debugger
piranha agent      # Interactive agent
piranha version    # Version info
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Piranha Agent                            │
├─────────────────────────────────────────────────────────────┤
│  Python SDK                                                  │
│  ├── Agent / AsyncAgent                                      │
│  ├── Task / Session                                          │
│  ├── LLMProvider (LiteLLM)                                   │
│  ├── MemoryManager / ContextManager                          │
│  └── Gradio Debugger UI                                      │
├─────────────────────────────────────────────────────────────┤
│  Rust Core (piranha_core)                                    │
│  ├── EventStore (SQLite)                                     │
│  ├── SkillRegistry                                           │
│  ├── GuardrailEngine                                         │
│  ├── SemanticCache                                           │
│  ├── WasmRunner (wasmtime)                                   │
│  └── DynamicSkillCompiler                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
piranha-agent/
├── piranha/                  # Python SDK
│   ├── __init__.py
│   ├── agent.py              # Agent with LiteLLM
│   ├── async_agent.py        # Async support
│   ├── llm_provider.py       # LiteLLM wrapper
│   ├── memory.py             # Memory/Context
│   ├── task.py               # Task execution
│   ├── session.py            # Session management
│   ├── skill.py              # Skill decorator
│   ├── debugger.py           # Gradio UI
│   └── cli.py                # CLI
├── rust_core/                # Rust core
│   ├── src/
│   │   ├── lib.rs
│   │   ├── python_bindings.rs
│   │   ├── event_store.rs
│   │   ├── guardrails.rs
│   │   ├── semantic_cache.rs
│   │   ├── skill_registry.rs
│   │   ├── types.rs
│   │   └── wasm_runner.rs    # NEW: Wasm sandbox
│   └── Cargo.toml
├── examples/
│   ├── 01_basic_agent.py
│   ├── 02_skills.py
│   ├── 03_multi_agent.py
│   ├── 04_rust_core.py
│   ├── 05_ollama_local.py
│   └── 06_complete_features.py
├── tests/
│   ├── test_python_sdk.py
│   └── test_rust_core.py
├── skills.md                 # Skills documentation
├── RULES.md                  # Agent rules
└── README.md
```

---

## Key Features

### 1. LiteLLM Integration

```python
from piranha import Agent, LLMProvider

# Use any LiteLLM provider
agent = Agent(
    name="assistant",
    model="ollama/llama3:latest",  # or gpt-4, claude-3-5-sonnet, etc.
)

# Direct LLM access
llm = LLMProvider(model="ollama/llama3:latest")
response = llm.chat([LLMMessage(role="user", content="Hello")])
```

### 2. Async Execution

```python
from piranha import AsyncAgent, AgentGroup

agent = AsyncAgent(name="assistant")
response = await agent.chat("Hello")

# Parallel execution
group = AgentGroup([agent1, agent2, agent3])
results = await group.run_parallel("Task")
```

### 3. Memory & Context

```python
agent = Agent(name="assistant")

# Add to long-term memory
agent.add_to_memory("User prefers Python")

# Search memory
results = agent.search_memory("What does user prefer?")

# Context management
context = agent.memory.get_context("programming", max_tokens=500)
```

### 4. Wasm Sandbox

```python
from piranha_core import WasmRunner, DynamicSkillCompiler

runner = WasmRunner()
valid = runner.validate(wasm_bytes)

compiler = DynamicSkillCompiler()
result = compiler.compile_and_execute(skill_code, input_data)
```

### 5. Time-Travel Debugger

```bash
piranha debug
```

Features:
- Load traces from EventStore
- Visualize event timeline
- Analyze costs per model
- Rollback to any sequence
- Inspect event payloads

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Test specific module
pytest tests/test_rust_core.py -v
pytest tests/test_python_sdk.py -v
```

---

## API Reference

### Agent

| Method | Description |
|--------|-------------|
| `run(task)` | Execute a task |
| `chat(message)` | Chat with agent |
| `add_to_memory(content)` | Add to long-term memory |
| `search_memory(query)` | Search memories |
| `get_history()` | Get conversation history |
| `clear_history()` | Clear history |
| `get_cost_report()` | Get cost report |
| `export_trace()` | Export session trace |

### AsyncAgent

| Method | Description |
|--------|-------------|
| `run(task)` | Async task execution |
| `chat(message)` | Async chat |
| `get_history()` | Get history |

### LLMProvider

| Method | Description |
|--------|-------------|
| `chat(messages)` | Sync chat |
| `chat_async(messages)` | Async chat |
| `chat(messages, stream=True)` | Streaming chat |

### MemoryManager

| Method | Description |
|--------|-------------|
| `add(content, tags)` | Add memory |
| `search(query, top_k)` | Semantic search |
| `get_context(query)` | Build context |

### WasmRunner

| Method | Description |
|--------|-------------|
| `validate(wasm_bytes)` | Validate Wasm |
| `execute(wasm, input)` | Execute Wasm |

---

## Configuration

### Environment Variables

```bash
# Ollama
OLLAMA_HOST=localhost:11434

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Logging
PIRANHA_RUST_LOG=info
```

---

## Roadmap

### Future Enhancements

- [ ] Real Python→Wasm compilation (Luna/Py2Wasm)
- [ ] Vector database integration (ChromaDB, Qdrant)
- [ ] Multi-modal agents (images, audio)
- [ ] Agent orchestration UI
- [ ] Production deployment (Docker, K8s)

---

## License

MIT OR Apache-2.0
