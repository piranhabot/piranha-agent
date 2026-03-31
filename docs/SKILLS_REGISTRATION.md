# 📚 Complete Skills Registration Guide

## 🎯 Overview

Piranha Agent v0.4.2 includes **53+ skills** across multiple categories.

**Total Skills:** 53+
- Planning: 2 skills
- Claude Code Explorer: 5 skills
- Claude Skills: 46+ skills

---

## 🚀 Quick Start: Register ALL Skills

### Method 1: Auto-Register All Skills (Recommended)

```python
from piranha_agent import Agent, register_complete_claude_skills

# Create agent
agent = Agent(name="assistant")

# Register ALL 53+ skills
register_complete_claude_skills(agent)

# Agent now has:
# - 2 Planning skills
# - 5 Claude Code Explorer skills
# - 46+ Claude skills
```

### Method 2: Selective Registration

```python
from piranha_agent import Agent
from piranha_agent import (
    register_claude_skills,           # ~46 skills
    create_claude_explorer_skill,     # 5 skills
)

agent = Agent(name="assistant")

# Register specific skill sets
register_claude_skills(agent)  # Core Claude skills

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

### Claude Skills (~46 skills)

**Files:**
- `piranha_agent/claude_skills.py` - Core Claude skills
- `piranha_agent/official_claude_skills.py` - 4 official Anthropic skills
- `piranha_agent/complete_claude_skills.py` - 42 additional skills

```python
from piranha_agent import (
    register_claude_skills,           # ~46 skills
    register_official_claude_skills,  # 4 official skills
    register_additional_claude_skills, # 42 additional skills
    register_complete_claude_skills,  # ALL 53+ skills
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
register_complete_claude_skills(agent)  # All 53+ skills
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
| `register_complete_claude_skills()` | 53+ | General purpose |
| `register_claude_skills()` | ~46 | Core Claude skills |
| `register_official_claude_skills()` | 4 | Official Anthropic |
| `register_additional_claude_skills()` | 42 | Extended Claude |
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
print(f"Total skills: {len(agent.skills)}")  # Should be 53+

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

- [skills.md](skills.md) - Skills overview
- [skills/CATEGORIZATION.md](skills/CATEGORIZATION.md) - Complete catalog
- [docs/PLAN_MODE.md](docs/PLAN_MODE.md) - Plan Mode guide
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [docs/CLAUDE_CODE_EXPLORER.md](docs/CLAUDE_CODE_EXPLORER.md) - Explorer guide
- [INDEX.md](INDEX.md) - Complete index

---

**Version:** 0.4.2  
**Date:** April 1, 2026  
**Status:** ✅ **ALL 53+ SKILLS REGISTERED AND WORKING**
