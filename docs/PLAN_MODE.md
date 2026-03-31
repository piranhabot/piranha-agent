# Plan Mode - Architecture-First Workflow

## 🎯 Overview

**Plan Mode** enforces architectural thinking before code execution, ensuring agents think before they act.

**New in v0.4.2**

---

## 🚀 Quick Start

```python
from piranha_agent import Agent

agent = Agent(name="architect")

# Plan Mode: Agent MUST draft PLAN.md before acting
result = agent.run_autonomous(
    task="Build a REST API",
    plan_first=True  # ← Forces planning workflow
)
```

---

## 📋 How It Works

### Workflow

```
1. User Request
   ↓
2. Agent Analyzes Task
   ↓
3. Agent drafts PLAN.md ✍️
   ↓
4. Human Reviews & Approves ✅ (HITL Checkpoint)
   ↓
5. Agent Executes According to Plan 🚀
   ↓
6. Progress Tracked Against Plan 📊
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Mandatory Planning** | Agent cannot execute code-changing skills without approved plan |
| **Human-in-the-Loop** | Plan approval required before execution |
| **Audit Trail** | PLAN.md created as permanent record |
| **Progress Tracking** | Execution tracked against plan milestones |
| **Adaptive Prompts** | System prompt updated for Plan Mode |

---

## 🛠️ Planning Skills

### `draft_plan`

Write architectural strategy to PLAN.md.

**Parameters:**
- `content` (required): Markdown content of the plan
- `filename` (optional): Name of plan file (default: "PLAN.md")

**Example:**
```python
from piranha_agent.skills.planning import draft_plan

result = draft_plan(
    content="""
# API Development Plan

## Architecture
- FastAPI backend
- PostgreSQL database
- JWT authentication

## Steps
1. Set up project structure
2. Define database models
3. Create API endpoints
4. Add authentication
5. Write tests
"""
)
print(result)
# Output: "Plan successfully written to PLAN.md. Please review and approve."
```

**Requires Confirmation:** ✅ Yes (Human MUST approve)

---

### `get_plan`

Retrieve and review current strategy.

**Parameters:**
- `filename` (optional): Name of plan file (default: "PLAN.md")

**Example:**
```python
from piranha_agent.skills.planning import get_plan

plan = get_plan()
print(plan)
# Output: Contents of PLAN.md
```

---

## 🎭 Plan Mode Behavior

### Without Plan Mode (Normal)
```python
agent.run_autonomous("Build a REST API")
# Agent starts coding immediately
```

### With Plan Mode
```python
agent.run_autonomous("Build a REST API", plan_first=True)
# 1. Agent drafts PLAN.md
# 2. Waits for human approval
# 3. Executes according to plan
```

---

## 📝 Example PLAN.md

```markdown
# Project Plan: REST API

## Objective
Build a secure REST API for user management.

## Architecture
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Auth**: JWT tokens
- **Testing**: pytest

## Milestones
1. [ ] Project setup
2. [ ] Database models
3. [ ] API endpoints
4. [ ] Authentication
5. [ ] Testing
6. [ ] Documentation

## Risks
- Database schema changes
- Auth edge cases

## Timeline
- Estimated: 4 hours
```

---

## 🔧 Configuration

### Enable Plan Mode
```python
# Method 1: run_autonomous
agent.run_autonomous(task, plan_first=True)

# Method 2: Agent default
agent = Agent(name="architect", default_plan_first=True)
```

### Custom Plan File
```python
agent.run_autonomous(
    task="Refactor module",
    plan_first=True,
    plan_filename="REFACTOR_PLAN.md"
)
```

---

## ✅ Benefits

| Benefit | Description |
|---------|-------------|
| **Prevents Rash Changes** | Forces thinking before coding |
| **Architectural Thinking** | Encourages big-picture view |
| **Audit Trail** | PLAN.md documents decisions |
| **Human Oversight** | HITL approval for complex tasks |
| **Progress Tracking** | Clear milestones to track |
| **Reduced Errors** | Planning catches issues early |

---

## 🎯 Use Cases

### 1. Large Refactoring
```python
agent.run_autonomous(
    "Refactor authentication module",
    plan_first=True
)
```

### 2. New Feature Development
```python
agent.run_autonomous(
    "Add user profile feature",
    plan_first=True
)
```

### 3. Bug Fix Investigation
```python
agent.run_autonomous(
    "Fix memory leak in data processor",
    plan_first=True
)
```

### 4. System Integration
```python
agent.run_autonomous(
    "Integrate Stripe payments",
    plan_first=True
)
```

---

## 📊 Comparison

| Approach | Planning | HITL | Audit | Error Rate |
|----------|----------|------|-------|------------|
| **Plan Mode** | ✅ Mandatory | ✅ Required | ✅ PLAN.md | Low |
| **Normal Mode** | ⚠️ Optional | ⚠️ Optional | ⚠️ Logs | Medium |
| **No Planning** | ❌ None | ❌ None | ❌ None | High |

---

## 🔒 Security

### Human-in-the-Loop Checkpoint

Plan Mode enforces:
1. **Plan Review**: Human must review architectural approach
2. **Approval Required**: Execution blocked until approved
3. **Change Tracking**: Deviations from plan logged
4. **Audit Trail**: PLAN.md preserved for compliance

---

## 📚 Related Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Skills Documentation](skills.md)
- [Security Hardening](docs/SECURITY.md)
- [CHANGELOG](CHANGELOG.md#042---2026-04-01)

---

## 🎓 Best Practices

### 1. Write Clear Plans
```markdown
# Good Plan
- Specific milestones
- Clear acceptance criteria
- Risk assessment

# Bad Plan
- Vague steps
- No success criteria
- No risk consideration
```

### 2. Review Thoroughly
- Check architectural alignment
- Verify security considerations
- Ensure test coverage planned
- Confirm timeline realistic

### 3. Track Progress
- Update PLAN.md as work completes
- Document deviations and why
- Keep audit trail current

---

**Version:** 0.4.2  
**Status:** ✅ Production Ready  
**Added:** v0.4.2 (April 2026)
