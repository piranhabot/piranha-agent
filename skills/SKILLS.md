# Claude Skills for Piranha Agent

**Version:** 0.4.0  
**Last Updated:** March 2026

---

## 📚 What are Claude Skills?

Claude Skills are specialized capabilities that extend Piranha Agent's functionality. Each skill is a pre-built module that enables the agent to perform specific tasks with expertise.

---

## 🎯 Available Skills (46+)

### 📄 Document Skills (4)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **docx** | Create, edit, analyze Word documents | `file_read`, `file_write` | ✅ |
| **pdf** | Extract text, merge, split PDFs | `file_read`, `file_write` | ✅ |
| **pptx** | Create, edit PowerPoint presentations | `file_read`, `file_write` | ✅ |
| **xlsx** | Create, edit Excel spreadsheets | `file_read`, `file_write` | ✅ |

---

### 💻 Development Skills (5)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **frontend-design** | React + Tailwind + shadcn/ui designs | `network_read` | ✅ |
| **mcp-builder** | Build MCP servers for API integration | `network_write` | ✅ |
| **test-driven-development** | TDD methodology implementation | `file_write` | ✅ |
| **code-review** | Code quality review | `file_read` | ✅ |
| **software-architecture** | Clean Architecture, SOLID principles | `file_read` | ✅ |

---

### 🔍 Research & Analysis Skills (5)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **deep-research** | Multi-step autonomous research | `network_read` | ✅ |
| **root-cause-tracing** | Error tracing and analysis | `file_read` | ✅ |
| **lead-research-assistant** | Lead qualification and research | `network_read` | ✅ |
| **analyze_complex_problem** | Systematic problem breakdown | - | ✅ |
| **logical_reasoning** | Logical argument evaluation | - | ✅ |

---

### 🎨 Creative Skills (5)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **canvas-design** | Visual art creation (PNG/PDF) | `file_write` | ✅ |
| **brand-guidelines** | Apply brand colors/typography | - | ✅ |
| **brainstorming** | Structured idea development | - | ✅ |
| **imagen** | AI image generation | `network_write` | ✅ |
| **creative_writing** | Stories, poems, articles | `file_write` | ✅ |

---

### ✍️ Communication Skills (5)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **internal-comms** | Status reports, newsletters | `file_write` | ✅ |
| **article-extractor** | Web article extraction | `network_read` | ✅ |
| **content-research-writer** | Research-backed content | `network_read`, `file_write` | ✅ |
| **summarize_text** | Document summarization | - | ✅ |
| **edit_improve_text** | Text editing and improvement | - | ✅ |

---

### 📊 Data & Analytics Skills (4)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **csv-data-summarizer** | CSV analysis and insights | `file_read` | ✅ |
| **postgres** | Safe SQL queries | `network_read` | ✅ |
| **statistical_analysis** | Statistical methods | - | ✅ |
| **meeting-insights-analyzer** | Meeting transcript analysis | `file_read` | ✅ |

---

### 📁 Productivity Skills (6)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **file-organizer** | Intelligent file organization | `file_read`, `file_write` | ✅ |
| **git-workflows** | Git branch/PR management | `file_read`, `file_write` | ✅ |
| **skill-creator** | Interactive skill creation | `file_write` | ✅ |
| **kaizen** | Continuous improvement | - | ✅ |
| **extract_information** | Information extraction | - | ✅ |
| **step_by_step_solver** | Complex problem solving | - | ✅ |

---

### 🌐 Social Media Skills (3)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **reddit-fetch** | Reddit content retrieval | `network_read` | ✅ |
| **youtube-transcript** | YouTube transcripts | `network_read` | ✅ |
| **twitter-algorithm-optimizer** | Tweet optimization | `network_read`, `network_write` | ✅ |

---

### 💼 Business Skills (4)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **competitive-ads-extractor** | Competitor ad analysis | `network_read` | ✅ |
| **domain-name-brainstormer** | Domain name generation | `network_read` | ✅ |
| **compare_options** | Multi-criteria comparison | - | ✅ |
| **tailored-resume-generator** | Resume generation | `file_read`, `file_write` | ✅ |

---

### 🧠 Reasoning Skills (5)

| Skill | Description | Permissions | Status |
|-------|-------------|-------------|--------|
| **analyze_data** | Data insights | `file_read` | ✅ |
| **solve_math_problem** | Math problem solving | - | ✅ |
| **explain_code** | Code explanation | `file_read` | ✅ |
| **generate_code** | Code generation | `file_write` | ✅ |
| **debug_code** | Bug fixing | `file_read`, `file_write` | ✅ |

---

## 🔧 Skill Permissions

| Permission | Description | Required For |
|------------|-------------|--------------|
| `file_read` | Read files from disk | Document processing, code analysis |
| `file_write` | Write files to disk | Document creation, code generation |
| `network_read` | Read from network/Internet | Research, web scraping |
| `network_write` | Write to network/Internet | API calls, image generation |
| `code_execution` | Execute code | Code testing, Wasm execution |
| `spawn_sub_agent` | Create sub-agents | Multi-agent collaboration |
| `external_api` | Call external APIs | Third-party integrations |
| `cache_access` | Access semantic cache | Caching operations |

---

## 📖 Using Skills

### Via Python

```python
from piranha import Agent
from piranha.claude_skills import register_complete_claude_skills

# Create agent
agent = Agent(name="assistant", model="ollama/llama3:latest")

# Register all 46+ skills
register_complete_claude_skills(agent)

# Use specific skill
from piranha.complete_claude_skills import deep_research

result = deep_research(
    topic="AI agent frameworks",
    depth="deep"
)
```

### Via UI

1. Open **Skills** page: http://localhost:3000/skills
2. Browse available skills
3. Click **Install** to enable a skill
4. Use skill in agent tasks

---

## 🛠️ Creating Custom Skills

### Skill Template

```python
from piranha import skill

@skill(
    name="my_custom_skill",
    description="Does something useful",
    parameters={
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Input text"}
        },
        "required": ["input"]
    },
    permissions=["file_read"],
    auto_monitor=True
)
def my_custom_skill(input: str) -> str:
    """Custom skill implementation."""
    return f"Processed: {input}"
```

### SKILL.md Format

```markdown
# Skill Name

## Overview
Brief description of what the skill does.

## When to Use
Conditions for activating this skill.

## Process
1. Step 1
2. Step 2
3. Step 3

## Output Format
Expected output structure.

## Resources
- Related files
- Templates
- References
```

---

## 📊 Skill Statistics

| Metric | Value |
|--------|-------|
| **Total Skills** | 46+ |
| **Document Skills** | 4 |
| **Development Skills** | 5 |
| **Research Skills** | 5 |
| **Creative Skills** | 5 |
| **Communication Skills** | 5 |
| **Data Skills** | 4 |
| **Productivity Skills** | 6 |
| **Social Media Skills** | 3 |
| **Business Skills** | 4 |
| **Reasoning Skills** | 5 |

---

## 🔗 References

- [Skills UI](http://localhost:3000/skills)
- [Skills API Documentation](docs/SKILLS_API.md)
- [Creating Custom Skills](docs/CUSTOM_SKILLS.md)
- [Piranha Agent README](README.md)

---

*Last updated: March 2026*  
*Version: 0.4.0*
