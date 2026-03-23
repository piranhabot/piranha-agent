# Piranha Agent Cookbook

A collection of recipes for common AI agent use cases and patterns.

---

## 📚 Table of Contents

### Getting Started
1. [Create Your First Agent](#1-create-your-first-agent)
2. [Run a Simple Task](#2-run-a-simple-task)
3. [Use Local LLM with Ollama](#3-use-local-llm-with-ollama)

### Skills
4. [Use Claude Skills](#4-use-claude-skills)
5. [Create Custom Skills](#5-create-custom-skills)
6. [Register Multiple Skills](#6-register-multiple-skills)

### Advanced Features
7. [Enable Semantic Cache](#7-enable-semantic-cache)
8. [Use Wasm Sandbox](#8-use-wasm-sandbox)
9. [Time-Travel Debugging](#9-time-travel-debugging)

### Multi-Agent
10. [Create Multi-Agent System](#10-create-multi-agent-system)
11. [Agent Communication](#11-agent-communication)
12. [Distributed Agents](#12-distributed-agents)

### Production
13. [PostgreSQL Event Store](#13-postgresql-event-store)
14. [Cost Tracking](#14-cost-tracking)
15. [Guardrails and Limits](#15-guardrails-and-limits)

### Integrations
16. [Use Real Embeddings](#16-use-real-embeddings)
17. [VS Code Integration](#17-vs-code-integration)
18. [Stream Responses](#18-stream-responses)

---

## Recipes

### 1. Create Your First Agent

**Problem:** You want to create a simple AI agent.

**Solution:**

```python
from piranha_agent import Agent, Task

# Create agent
agent = Agent(
    name="my-assistant",
    model="ollama/llama3:latest",  # or "anthropic/claude-3-5-sonnet"
    description="My first AI assistant"
)

# Create and run task
task = Task(
    description="Explain quantum computing in simple terms",
    agent=agent
)

result = task.run()
print(result)
```

**See also:** [`examples/01_basic_agent.py`](examples/01_basic_agent.py)

---

### 2. Run a Simple Task

**Problem:** You want to execute a specific task with an agent.

**Solution:**

```python
from piranha_agent import Agent, Task

agent = Agent(model="ollama/llama3:latest")

# Simple task
task = Task(
    description="Write a Python function to calculate fibonacci",
    expected_output="A working Python function",
    agent=agent
)

result = task.run()
print(f"Success: {result.success}")
print(f"Result: {result.result}")
```

---

### 3. Use Local LLM with Ollama

**Problem:** You want to run agents locally without API costs.

**Solution:**

```python
from piranha_agent import Agent, Task

# First, install Ollama: https://ollama.ai
# Then pull a model: ollama pull llama3:latest

agent = Agent(
    name="local-assistant",
    model="ollama/llama3:latest",
)

task = Task(description="What is 2 + 2?", agent=agent)
result = task.run()
print(result)
```

**See also:** [`examples/05_ollama_local.py`](examples/05_ollama_local.py)

---

### 4. Use Claude Skills

**Problem:** You want to use pre-built skills for common tasks.

**Solution:**

```python
from piranha_agent import Agent
from piranha_agent.complete_claude_skills import (
    register_complete_claude_skills,
    deep_research,
    frontend_design,
    code_review
)

# Create agent with all 46+ skills
agent = Agent(name="skilled-assistant", model="ollama/llama3:latest")
register_complete_claude_skills(agent)

# Use skills directly
research = deep_research(topic="AI trends", depth="deep")
design = frontend_design(type="landing-page", style="Modern")
review = code_review(code=my_code, focus_areas=["Security"])
```

**See also:** [`examples/10_official_claude_skills.py`](examples/10_official_claude_skills.py)

---

### 5. Create Custom Skills

**Problem:** You need a custom skill for your specific use case.

**Solution:**

```python
from piranha_agent import Agent, Skill
from piranha_agent.skill import skill

# Method 1: Using decorator
@skill(
    name="calculate_tax",
    description="Calculate sales tax for a purchase",
    parameters={
        "type": "object",
        "properties": {
            "amount": {"type": "number", "description": "Purchase amount"},
            "tax_rate": {"type": "number", "description": "Tax rate (0-1)"}
        },
        "required": ["amount", "tax_rate"]
    }
)
def calculate_tax(amount: float, tax_rate: float) -> float:
    return amount * tax_rate

# Method 2: Using Skill class
def my_function(x, y):
    return x + y

custom_skill = Skill(
    name="my_skill",
    description="Does something useful",
    function=my_function
)

# Add to agent
agent = Agent(name="custom-agent", skills=[calculate_tax, custom_skill])
```

**See also:** [`examples/02_skills.py`](examples/02_skills.py)

---

### 6. Register Multiple Skills

**Problem:** You want to organize and register multiple skills efficiently.

**Solution:**

```python
from piranha_agent import Agent
from piranha_agent.claude_skills import get_all_claude_skills
from piranha_agent.official_claude_skills import get_all_official_claude_skills
from piranha_agent.complete_claude_skills import get_all_additional_claude_skills

# Get all skills from different modules
all_skills = (
    get_all_claude_skills() +
    get_all_official_claude_skills() +
    get_all_additional_claude_skills()
)

# Create agent with all skills
agent = Agent(
    name="master-assistant",
    model="ollama/llama3:latest",
    skills=all_skills
)

print(f"Registered {len(agent.skills)} skills")
```

---

### 7. Enable Semantic Cache

**Problem:** You want to reduce LLM costs by caching responses.

**Solution:**

```python
from piranha_agent import SemanticCache

# Create cache
cache = SemanticCache(ttl_hours=24, max_entries=10000)

# Store with embedding
cache.put_with_embedding(
    key="python_intro",
    prompt_text="What is Python?",
    response="Python is a programming language...",
    model="llama3",
    prompt_tokens=10,
    completion_tokens=25,
    cost_usd=0.0003
)

# Fuzzy match - finds similar prompts
result = cache.get_fuzzy("Tell me about Python", "llama3")
if result:
    print(f"Cache hit! Similarity: {result['similarity']:.2f}")
    print(f"Response: {result['response']}")
else:
    print("Cache miss - call LLM")
```

**See also:** [`examples/08_semantic_cache_fuzzy.py`](examples/08_semantic_cache_fuzzy.py)

---

### 8. Use Wasm Sandbox

**Problem:** You want to execute untrusted code safely.

**Solution:**

```python
from piranha_agent import WasmRunner

# Create Wasm runner
runner = WasmRunner()

# Validate Wasm module
wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
is_valid = runner.validate(wasm_bytes)
print(f"Valid: {is_valid}")

# Execute safely in sandbox
result = runner.execute(
    wasm_bytes=wasm_bytes,
    function_name="main",
    input="test input"
)

print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
print(f"Time: {result['execution_time_ms']}ms")
```

**See also:** [`examples/07_wasm_sandbox.py`](examples/07_wasm_sandbox.py)

---

### 9. Time-Travel Debugging

**Problem:** You want to debug agent decisions step-by-step.

**Solution:**

```python
# Method 1: Launch from CLI
# Run: piranha-agent debug

# Method 2: Programmatically
from piranha_agent import create_debugger_ui

ui = create_debugger_ui()
ui.launch()

# Method 3: Export trace for analysis
from piranha_agent import Agent, Task

agent = Agent(name="debug-agent", model="ollama/llama3:latest")
task = Task(description="Test task", agent=agent)
result = task.run()

# Export trace
trace = agent.export_trace()
print(f"Trace size: {len(trace)} bytes")

# Load trace in debugger UI
```

**See also:** [`piranha/debugger.py`](piranha/debugger.py)

---

### 10. Create Multi-Agent System

**Problem:** You want multiple agents to work together.

**Solution:**

```python
from piranha_agent import Agent, Task

# Create specialized agents
researcher = Agent(
    name="researcher",
    model="ollama/llama3:latest",
    description="Researches topics"
)

writer = Agent(
    name="writer",
    model="ollama/llama3:latest",
    description="Writes content"
)

reviewer = Agent(
    name="reviewer",
    model="ollama/llama3:latest",
    description="Reviews and edits"
)

# Create tasks for each agent
research_task = Task(
    description="Research AI trends in 2026",
    agent=researcher
)
research_result = research_task.run()

write_task = Task(
    description=f"Write article based on: {research_result.result}",
    agent=writer
)
write_result = write_task.run()

review_task = Task(
    description=f"Review and improve: {write_result.result}",
    agent=reviewer
)
final_result = review_task.run()

print(final_result.result)
```

**See also:** [`examples/03_multi_agent.py`](examples/03_multi_agent.py)

---

### 11. Agent Communication

**Problem:** You want agents to communicate and share information.

**Solution:**

```python
from piranha_agent import Agent, Task
from piranha_agent.memory import MemoryManager

# Shared memory for communication
shared_memory = MemoryManager()

# Create agents with shared memory
agent1 = Agent(name="agent-1", model="ollama/llama3:latest")
agent1.memory.add("Project X requires Python 3.10+")

agent2 = Agent(name="agent-2", model="ollama/llama3:latest")

# Agent 2 can access shared memory
search_results = agent2.memory.search("Python requirements", top_k=3)
for memory, score in search_results:
    print(f"Found: {memory.content} (score: {score:.2f})")
```

---

### 12. Distributed Agents

**Problem:** You want to run agents across multiple processes/machines.

**Solution:**

```python
from piranha_agent import AgentOrchestrator, DistributedAgent

# Create orchestrator
orchestrator = AgentOrchestrator(queue_size=100)

# Create worker agents
workers = []
for i in range(3):
    worker = DistributedAgent(f"worker-{i}")
    workers.append(worker)

# Submit tasks
task_ids = []
for i in range(5):
    task_id = orchestrator.submit_task(
        f"Process data batch {i}",
        priority=5
    )
    task_ids.append(task_id)

# Get cluster status
status = orchestrator.get_cluster_status()
print(f"Active workers: {len(status)}")

# Get worker statistics
stats = orchestrator.get_worker_stats()
for worker_id, tasks_completed in stats:
    print(f"{worker_id}: {tasks_completed} tasks completed")
```

---

### 13. PostgreSQL Event Store

**Problem:** You want to use PostgreSQL for production event sourcing.

**Solution:**

```python
from piranha_agent import PostgresEventStore

# Create PostgreSQL store
store = PostgresEventStore(
    connection_string="postgresql://user:pass@localhost:5432/piranha"
)

# Get connection info
print(store.get_info())
print(store.get_connection_info())

# In production, use async methods
# await store.record_llm_call_async(...)
# await store.export_trace_async(...)
```

---

### 14. Cost Tracking

**Problem:** You want to track and optimize LLM costs.

**Solution:**

```python
from piranha_agent import Agent, Task

agent = Agent(name="cost-tracker", model="anthropic/claude-3-5-sonnet")

# Run tasks
for i in range(5):
    task = Task(description=f"Task {i}", agent=agent)
    task.run()

# Get cost report
cost_report = agent.get_cost_report()
print(f"Total cost: ${cost_report.get('total_cost_usd', 0):.4f}")
print(f"LLM calls: {cost_report.get('llm_calls', 0)}")
print(f"Total tokens: {cost_report.get('total_tokens', 0)}")

# Export trace for analysis
trace = agent.export_trace()
```

---

### 15. Guardrails and Limits

**Problem:** You want to enforce safety limits on agent actions.

**Solution:**

```python
from piranha_agent import Agent
from piranha_core import GuardrailEngine

# Create guardrail engine
guardrails = GuardrailEngine(token_budget=100000)

# Create agent with guardrails
agent = Agent(
    name="safe-agent",
    model="ollama/llama3:latest"
)

# Check before expensive operations
verdict = guardrails.check(
    agent_id=agent.id,
    session_id=agent.session.id,
    tokens_used=1000,
    token_budget=100000,
    pending_action="web_search"
)

if verdict["verdict"] == "block":
    print(f"Action blocked: {verdict.get('reason')}")
else:
    print(f"Action allowed: {verdict['verdict']}")
```

---

### 16. Use Real Embeddings

**Problem:** You want true semantic matching instead of hash-based embeddings.

**Solution:**

```python
from piranha_agent import SemanticCache, EmbeddingModel

# Option 1: sentence-transformers (local, free)
model = EmbeddingModel(
    provider="sentence-transformers",
    model="all-MiniLM-L6-v2"
)

# Option 2: Ollama embeddings (local, free)
model = EmbeddingModel(
    provider="ollama",
    model="nomic-embed-text"
)

# Option 3: OpenAI embeddings (cloud, paid)
model = EmbeddingModel(
    provider="openai",
    model="text-embedding-3-small",
    api_key="sk-..."
)

# Use with semantic cache
cache = SemanticCache(embedding_model=model)

# Now fuzzy matching uses real semantic similarity
cache.put_with_embedding(
    key="python_intro",
    prompt_text="What is Python?",
    response="Python is a programming language...",
    model="llama3",
    prompt_tokens=10,
    completion_tokens=25,
    cost_usd=0.0003
)

# This will now match semantically similar queries
result = cache.get_fuzzy("Tell me about Python programming", "llama3")
```

**See also:** [`piranha/embeddings.py`](piranha/embeddings.py)

---

### 17. VS Code Integration

**Problem:** You want to develop agents directly in VS Code.

**Solution:**

1. **Install Piranha Agent extension** from VS Code Marketplace

2. **Create Agent:**
   - Open Command Palette (`Ctrl+Shift+P`)
   - Run `Piranha: Create New Agent`
   - Enter name and select model

3. **Run Agent:**
   - Open Python file with agent code
   - Click Play icon in editor title

4. **Debug:**
   - Run `Piranha: Open Time-Travel Debugger`
   - Step through agent decisions

5. **Chat:**
   - Run `Piranha: Chat with Agent`
   - Chat panel opens in sidebar

**See also:** [`vscode-extension/`](vscode-extension/)

---

### 18. Stream Responses

**Problem:** You want to stream agent responses token-by-token.

**Solution:**

```python
from piranha_agent import Agent

agent = Agent(name="streaming-agent", model="ollama/llama3:latest")

# Stream response (when supported)
response = agent.run("Tell me a story", stream=True)

for chunk in response:
    print(chunk, end="", flush=True)
```

---

## 📖 Additional Resources

- [Full Documentation](docs/)
- [Skills Catalog](skills/CATEGORIZATION.md)
- [Framework Comparison](docs/FRAMEWORK_COMPARISON.md)
- [Improvement Roadmap](docs/IMPROVEMENT_ROADMAP.md)
- [GitHub Repository](https://github.com/piranha-agent/piranha-agent)

---

## 🤝 Contributing

Have a useful recipe? Submit it as a pull request!

1. Fork the repository
2. Create your recipe in `cookbook/`
3. Test it works
4. Submit PR

---

*Last updated: March 2026*
*Version: 0.3.0*
*Total recipes: 18*
