# 📚 Complete Skills Registration Guide

## 🎯 Overview

Piranha Agent v0.4.2 includes **51 built-in `@skill`-decorated Python
skills**, plus 5 Claude Code Explorer skills built programmatically -
56 total, spread across several independent registration functions (no
single call registers literally everything - see Method 1 vs 2 below).

- Claude Skills (`register_complete_claude_skills`): 46 skills (14 + 16 + 16)
- Claude Code Explorer (`create_claude_explorer_skill`): 5 skills
- Planning (`piranha_agent.skills.planning`): 2 skills
- git workflow (`piranha_agent.skills.git`): 2 skills
- Model compatibility (`piranha_agent.skills.model_compat`): 1 skill

---

## 🚀 Quick Start: Register ALL Claude Skills

### Method 1: Auto-Register All Claude Skills (Recommended)

```python
from piranha_agent import Agent, register_complete_claude_skills

# Create agent
agent = Agent(name="assistant")

# Register all 46 Claude skills (core + official + additional)
register_complete_claude_skills(agent)
```

This registers the 46 Claude skills only - it does **not** add Planning,
Explorer, git, or Model Compatibility skills; those need to be added
separately (see below), and GitHub/Slack/Google Sheets integrations are
a different mechanism entirely (see [../skills.md](../skills.md)).

*Fixed August 2026: this function previously combined only the official
(16) + additional (16) sets, silently dropping the 14 skills in
`claude_skills.py` - it now returns the full 46 as originally intended.*

### Method 2: Selective Registration

```python
from piranha_agent import Agent
from piranha_agent import (
    register_claude_skills,           # 14 skills (claude_skills.py)
    create_claude_explorer_skill,     # 5 skills
)

agent = Agent(name="assistant")

# Register specific skill sets
register_claude_skills(agent)  # Core Claude skills only (not official/additional)

# Add explorer skills separately
for skill in create_claude_explorer_skill():
    agent.add_skill(skill)
```

### Method 3: Manual Skill List

```python
from piranha_agent import Agent, create_claude_explorer_skill

# Create agent with specific skills
agent = Agent(
    name="explorer",
    skills=create_claude_explorer_skill()  # 5 explorer skills
)
```

---

## 📋 Complete Skill Registration Functions

### Planning Skills (2 skills)

**File:** `piranha_agent/skills/planning.py`

```python
from piranha_agent.skills.planning import draft_plan, get_plan

# These are automatically included in register_complete_claude_skills()
# Or use Plan Mode:
agent.run_autonomous(task="Build API", plan_first=True)
```

**Skills:**
| Skill | Description | Confirmation |
|-------|-------------|--------------|
| `draft_plan` | Write PLAN.md | ✅ Required (HITL) |
| `get_plan` | Read PLAN.md | ❌ No |

---

### Claude Code Explorer Skills (5 skills)

**File:** `piranha_agent/claude_code_explorer.py`

```python
from piranha_agent import create_claude_explorer_skill

skills = create_claude_explorer_skill()
# Returns list of 5 skills
```

**Skills:**
| Skill | Description |
|-------|-------------|
| `claude_code.list_tools` | List 40+ Claude Code tools |
| `claude_code.list_commands` | List 50+ slash commands |
| `claude_code.get_tool_source` | Get tool source code |
| `claude_code.search_source` | Search source with regex |
| `claude_code.get_architecture` | Get architecture overview |

---

### Claude Skills (46 skills)

**Files:**
- `piranha_agent/claude_skills.py` - 14 core Claude skills
- `piranha_agent/official_claude_skills.py` - 16 official-style skills (incl. `docx`/`pdf`/`pptx`/`xlsx`)
- `piranha_agent/complete_claude_skills.py` - 16 additional skills

```python
from piranha_agent import (
    register_claude_skills,           # 14 skills
    register_official_claude_skills,  # 16 skills
    register_additional_claude_skills, # 16 skills
    register_complete_claude_skills,  # all 46 (14 + 16 + 16)
)
```

**Categories:**
- Document Processing (4 skills): `docx`, `pdf`, `pptx`, `xlsx`
- Development & Code (5 skills): `frontend-design`, `mcp-builder`, etc.
- Research & Analysis (5 skills): `deep-research`, `root-cause-tracing`, etc.
- Creative & Design (5 skills): `canvas-design`, `brand-guidelines`, etc.
- Communication (5 skills): `internal-comms`, `article-extractor`, etc.
- Data & Analytics (4 skills): `csv-data-summarizer`, `postgres`, etc.
- Productivity (6 skills): `file-organizer`, `git-workflows`, etc.
- Social Media (3 skills): `reddit-fetch`, `youtube-transcript`, etc.
- Business (4 skills): `competitive-ads-extractor`, etc.
- Reasoning (5 skills): `analyze_data`, `solve_math_problem`, etc.

---

## 🎯 Registration by Use Case

### Use Case 1: General Assistant

```python
from piranha_agent import Agent, register_complete_claude_skills

agent = Agent(name="assistant")
register_complete_claude_skills(agent)  # All 46 Claude skills
```

### Use Case 2: Code Explorer

```python
from piranha_agent import Agent, create_claude_explorer_skill

agent = Agent(
    name="code-explorer",
    skills=create_claude_explorer_skill(),  # 5 explorer skills
)
```

### Use Case 3: Architect (Plan Mode)

```python
from piranha_agent import Agent

agent = Agent(name="architect")

# Plan Mode enabled
result = agent.run_autonomous(
    task="Build REST API",
    plan_first=True  # Uses draft_plan skill automatically
)
```

### Use Case 4: Multi-Agent Swarm

```python
from piranha_agent.orchestration import create_orchestrated_team
from piranha_agent import create_claude_explorer_skill

team = create_orchestrated_team("research-team")

# Add explorer skills to coordinator
for skill in create_claude_explorer_skill():
    team.coordinator.add_skill(skill)
```

### Use Case 5: Minimal Skills

```python
from piranha_agent import Agent, Skill, skill

@skill(name="hello", description="Say hello")
def hello(name: str) -> str:
    return f"Hello, {name}!"

agent = Agent(
    name="minimal",
    skills=[hello]  # Only custom skills
)
```

---

## 📊 Skill Registration Matrix

| Function | Skills Registered | Use Case |
|----------|-------------------|----------|
| `register_complete_claude_skills()` | 46 | General purpose (all Claude skills) |
| `register_claude_skills()` | 14 | Core Claude skills only |
| `register_official_claude_skills()` | 16 | Official-style skills only |
| `register_additional_claude_skills()` | 16 | Additional skills only |
| `create_claude_explorer_skill()` | 5 | Source exploration |
| `draft_plan`, `get_plan` | 2 | Plan Mode |

---

## 🔧 Advanced: Custom Skill Registration

### Create Custom Skill

```python
from piranha_agent.skill import skill

@skill(
    name="calculate_tax",
    description="Calculate sales tax",
    parameters={
        "type": "object",
        "properties": {
            "amount": {"type": "number"},
            "rate": {"type": "number"}
        },
        "required": ["amount", "rate"]
    }
)
def calculate_tax(amount: float, rate: float) -> float:
    return amount * rate

# Register with agent
agent.add_skill(calculate_tax)
```

### Skill with Permissions

```python
from piranha_agent.skill import skill

@skill(
    name="secure_operation",
    description="Requires special permission",
    permissions=["secure_ops"]  # Required permission
)
def secure_operation() -> str:
    return "Done!"

# Agent must have permission
agent = Agent(
    name="secure-agent",
    permissions=["secure_ops"],
    skills=[secure_operation]
)
```

### Skill with Auto-Monitoring

```python
from piranha_agent.skill import skill

@skill(
    name="tracked_operation",
    description="Automatically tracked in Studio",
    auto_monitor=True  # Enable auto-monitoring
)
def tracked_operation() -> str:
    return "Tracked!"
```

---

## ✅ Verification

### Check Registered Skills

```python
from piranha_agent import Agent, register_complete_claude_skills

agent = Agent(name="assistant")
register_complete_claude_skills(agent)

# Check skill count
print(f"Total skills: {len(agent.skills)}")  # Should be 46

# List skill names
for skill in agent.skills:
    print(f"  - {skill.name}")
```

### Test Skill Execution

```python
from piranha_agent import Agent, Task

agent = Agent(name="test")
register_complete_claude_skills(agent)

# Test a skill
task = Task(description="List all Claude Code tools", agent=agent)
result = task.run()
print(result)
```

---

## 🎯 Skill Categories Reference

### Planning Skills (2)
- `draft_plan`
- `get_plan`

### Claude Code Explorer (5)
- `claude_code.list_tools`
- `claude_code.list_commands`
- `claude_code.get_tool_source`
- `claude_code.search_source`
- `claude_code.get_architecture`

### Official Claude Skills (4)
- `docx`
- `pdf`
- `pptx`
- `xlsx`

### Development Skills (5)
- `frontend-design`
- `mcp-builder`
- `test-driven-development`
- `code-review`
- `software-architecture`

### Research Skills (5)
- `deep-research`
- `root-cause-tracing`
- `lead-research-assistant`
- `analyze_complex_problem`
- `logical_reasoning`

### Creative Skills (5)
- `canvas-design`
- `brand-guidelines`
- `brainstorming`
- `imagen`
- `creative_writing`

### Communication Skills (5)
- `internal-comms`
- `article-extractor`
- `content-research-writer`
- `summarize_text`
- `edit_improve_text`

### Data Skills (4)
- `csv-data-summarizer`
- `postgres`
- `statistical_analysis`
- `meeting-insights-analyzer`

### Productivity Skills (6)
- `file-organizer`
- `git-workflows`
- `skill-creator`
- `kaizen`
- `extract_information`
- `step_by_step_solver`

### Social Media Skills (3)
- `reddit-fetch`
- `youtube-transcript`
- `twitter-algorithm-optimizer`

### Business Skills (4)
- `competitive-ads-extractor`
- `domain-name-brainstormer`
- `lead-research-assistant`
- `tailored-resume-generator`

### Reasoning Skills (5)
- `analyze_data`
- `solve_math_problem`
- `explain_code`
- `generate_code`
- `debug_code`

---

## 📚 Related Documentation

*Links below are relative to this file's location (`docs/`), not repo root.*

- [../skills.md](../skills.md) - Skills overview, incl. GitHub/Slack/Google Sheets/Model Compatibility skills (not covered by this page - those are separate optional integrations, not part of `register_complete_claude_skills()`)
- [../skills/CATEGORIZATION.md](../skills/CATEGORIZATION.md) - Complete catalog
- [PLAN_MODE.md](PLAN_MODE.md) - Plan Mode guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CLAUDE_CODE_EXPLORER.md](CLAUDE_CODE_EXPLORER.md) - Explorer guide
- [../INDEX.md](../INDEX.md) - Complete index

---

**Version:** 0.4.2
**Date:** April 1, 2026 (original); code-verified August 2026

*Updated August 2026: `register_complete_claude_skills()` previously
combined only the official (16) + additional (16) skill sets, silently
dropping the 14 skills in `claude_skills.py` (`analyze_data`,
`generate_code`, `debug_code`, etc.) despite its docstring and this
page both claiming it registers "ALL" Claude skills. Fixed - it now
returns the full 46 (14 + 16 + 16), matching what "Method 1" below has
always claimed. See [CHANGELOG.md](../CHANGELOG.md).*
