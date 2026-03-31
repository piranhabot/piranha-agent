# Piranha Skills Documentation

## Overview

Skills are the capabilities that agents can use to interact with the world. They are divided into two categories:

1. **Static Skills** - Pre-defined, built-in capabilities
2. **Dynamic Skills** - User-defined, runtime-registered capabilities

---

## 🆕 NEW: Planning Skills (v0.4.2)

Architecture-First Workflow skills for Plan Mode:

| Skill | Description | Confirmation Required |
|-------|-------------|----------------------|
| `draft_plan` | Write architectural strategy to PLAN.md | ✅ Yes (HITL) |
| `get_plan` | Retrieve and review current plan | ❌ No |

**Usage:**
```python
from piranha_agent import Agent

agent = Agent(name="architect")

# Plan Mode forces agent to draft plan first
result = agent.run_autonomous(
    task="Build REST API",
    plan_first=True
)
```

**Full Documentation:** [docs/PLAN_MODE.md](docs/PLAN_MODE.md)

---

## 🆕 Claude Code Explorer Skills (v0.4.1)

Explore Claude Code's 512K+ lines of source code directly from your agents!

| Skill | Description |
|-------|-------------|
| `claude_code.list_tools` | List all 40+ Claude Code agent tools |
| `claude_code.list_commands` | List all 50+ Claude Code slash commands |
| `claude_code.get_tool_source` | Get source code for a specific tool |
| `claude_code.search_source` | Search source with regex patterns |
| `claude_code.get_architecture` | Get full architecture overview |

**Requirements:** `pip install mcp`

**Quick Start:**
```python
from piranha_agent import Agent
from piranha_agent.claude_code_explorer import create_claude_explorer_skill

# Create agent with explorer skills
agent = Agent(
    name="code-explorer",
    skills=create_claude_explorer_skill(),
)

# Explore Claude Code internals
result = agent.run("List all Claude Code tools and explain BashTool")
```

**Full Documentation:** [docs/CLAUDE_CODE_EXPLORER.md](docs/CLAUDE_CODE_EXPLORER.md)

---

## 🛡️ Orchestration Skills (Autonomous Swarms)

These skills allow a **Coordinator** agent to manage a team of sub-agents autonomously, similar to Claude Code's agent swarms.

| Skill | Description | Parameters |
|-------|-------------|------------|
| `delegate_task` | Delegates a sub-task to a specialized sub-agent (created on-the-fly if needed). | `agent_name`, `task_description`, `role`, `model` |
| `get_team_status` | Returns a summary of all active team members and shared memory keys. | None |
| `broadcast_message` | Sends a message to all team members via the shared message bus. | `message` |

---

## Static Skills

Static skills are built into the Piranha framework and available to all agents by default.

### Core Static Skills

| Skill | Description | Permissions |
|-------|-------------|-------------|
| `memory_store` | Store information in agent memory | `cache_access` |
| `memory_retrieve` | Retrieve information from memory | `cache_access` |
| `reason` | Perform logical reasoning | None |
| `summarize` | Summarize text content | None |
| `classify` | Classify content into categories | None |

### Usage Example

```python
from piranha_agent import Agent, Skill

# Static skills are automatically available
agent = Agent(name="assistant")

# Use built-in reasoning
response = agent.run("Reason about the pros and cons of remote work")
```

---

## Dynamic Skills

Dynamic skills are registered at runtime by users. They can be:

- Python functions decorated with `@skill`
- Tools loaded from external sources
- Skills delegated from parent agents

### Creating Dynamic Skills

```python
from piranha_agent import Skill
from piranha_agent.skill import skill

# Using the decorator
@skill(
    name="web_search",
    description="Search the web for information",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"]
    },
    permissions=["network_read"],
    inheritable=True
)
def search_web(query: str) -> str:
    """Search and return results."""
    # Implementation here
    return f"Results for: {query}"

# Add to agent
agent = Agent(name="researcher", skills=[search_web])
```

### Registering Skills Programmatically

```python
from piranha_core import SkillRegistry

registry = SkillRegistry()

registry.register_skill(
    skill_id="calculator",
    name="Calculator",
    description="Perform mathematical calculations",
    parameters_schema={
        "type": "object",
        "properties": {
            "expression": {"type": "string"}
        },
        "required": ["expression"]
    },
    permissions=["code_execution"],
    inheritable=True
)

# Grant to agent
registry.grant_skills(agent_id, ["calculator"])
```

---

## Skill Permissions

Skills require permissions to execute. Available permissions:

| Permission | Description |
|------------|-------------|
| `network_read` | Read from network/HTTP |
| `network_write` | Write to network/HTTP |
| `file_read` | Read files from disk |
| `file_write` | Write files to disk |
| `code_execution` | Execute arbitrary code |
| `spawn_sub_agent` | Create sub-agents |
| `external_api` | Call external APIs |
| `cache_access` | Access semantic cache |

---

## Agent Rules

### What Agents SHOULD Do

1. **Respect Permissions** - Only use skills they have been granted
2. **Log All Actions** - Every skill invocation is recorded in the event store
3. **Follow Guardrails** - Adhere to token budgets and rate limits
4. **Use Caching** - Leverage semantic cache to reduce costs
5. **Delegate Appropriately** - Spawn sub-agents for complex sub-tasks
6. **Report Errors** - Return clear error messages on failure
7. **Maintain Context** - Preserve conversation history in sessions

### What Agents MUST NOT Do

1. **No Unauthorized Access** - Never invoke skills without permission
2. **No Permission Escalation** - Cannot grant themselves new permissions
3. **No Budget Bypass** - Cannot exceed token/cost limits set by guardrails
4. **No Silent Failures** - Must report errors, not hide them
5. **No Data Leakage** - Cannot share session data across sessions
6. **No Infinite Loops** - Must terminate within reasonable steps
7. **No Privilege Inheritance** - Sub-agents only inherit explicitly granted skills

---

## Skill Inheritance

Skills can be inherited by sub-agents:

```python
# Parent agent with inheritable skills
parent = Agent(
    name="parent",
    skills=[search_web, calculator]  # Both inheritable=True
)

# Spawn sub-agent - inherits parent's skills
child = Agent(name="child", parent=parent)
# child can use search_web and calculator
```

### Non-Inheritable Skills

Some skills should not be inherited:

```python
@skill(name="admin_access", inheritable=False)
def admin_operation():
    """Sensitive operation - not for sub-agents"""
    pass
```

---

## Best Practices

1. **Minimal Permissions** - Grant only necessary permissions
2. **Descriptive Names** - Use clear skill names and descriptions
3. **Validate Inputs** - Always validate skill parameters
4. **Error Handling** - Return structured errors
5. **Documentation** - Document what each skill does
6. **Testing** - Test skills in isolation before agent use

---

## Security Considerations

1. **Audit Trail** - All skill invocations are logged
2. **Permission Checks** - Verified before every invocation
3. **Sandboxing** - Code execution should be sandboxed
4. **Rate Limiting** - Guardrails prevent abuse
5. **Session Isolation** - Skills cannot cross session boundaries
