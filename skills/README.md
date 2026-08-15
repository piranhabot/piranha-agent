# Piranha Agent Skills

Complete collection of Claude Skills for Piranha Agent framework.

## 📚 Skill Categories

### Phase 1-4: Core Skills (Built-in)
- Event Sourcing
- Skill Registry
- Guardrails
- Semantic Cache (with fuzzy matching)
- Wasm Sandbox

### Phase 5-6: Infrastructure Skills
- PostgreSQL Backend
- Distributed Agents

### Claude-Compatible Skills

#### 📄 Document Skills (Official Anthropic)
| Skill | Description |
|-------|-------------|
| `docx` | Create, edit, analyze Word documents |
| `pdf` | Extract text, merge, split PDFs |
| `pptx` | Create, edit PowerPoint presentations |
| `xlsx` | Create, edit Excel spreadsheets |

#### 💻 Development Skills
| Skill | Description |
|-------|-------------|
| `frontend-design` | React + Tailwind + shadcn/ui designs |
| `mcp-builder` | Build MCP servers for API integration |
| `test-driven-development` | TDD methodology implementation |
| `code-review` | Code quality review |
| `software-architecture` | Clean Architecture, SOLID principles |

#### 🔍 Research & Analysis
| Skill | Description |
|-------|-------------|
| `deep-research` | Multi-step autonomous research |
| `root-cause-tracing` | Error tracing and analysis |
| `lead-research-assistant` | Lead qualification and research |

#### 🎨 Creative Skills
| Skill | Description |
|-------|-------------|
| `canvas-design` | Visual art creation (PNG/PDF) |
| `brand-guidelines` | Apply brand colors/typography |
| `brainstorming` | Structured idea development |
| `imagen` | AI image generation |

#### ✍️ Communication Skills
| Skill | Description |
|-------|-------------|
| `internal-comms` | Status reports, newsletters, FAQs |
| `article-extractor` | Web article extraction |
| `content-research-writer` | Research-backed content writing |

#### 📊 Data Skills
| Skill | Description |
|-------|-------------|
| `csv-data-summarizer` | CSV analysis and insights |
| `postgres` | Safe read-only SQL queries |
| `meeting-insights-analyzer` | Meeting transcript analysis |

#### 📁 Productivity Skills
| Skill | Description |
|-------|-------------|
| `file-organizer` | Intelligent file organization |
| `git-workflows` | Git branch/PR management |
| `skill-creator` | Interactive skill creation |
| `kaizen` | Continuous improvement methodology |

#### 🌐 Social Media Skills
| Skill | Description |
|-------|-------------|
| `reddit-fetch` | Fetch Reddit content |
| `youtube-transcript` | YouTube transcript extraction |
| `twitter-algorithm-optimizer` | Tweet optimization |

#### 💼 Business Skills
| Skill | Description |
|-------|-------------|
| `competitive-ads-extractor` | Competitor ad analysis |
| `domain-name-brainstormer` | Domain name generation |
| `compare_options` | Multi-criteria decision comparison |
| `tailored-resume-generator` | Job-specific resume generation |

#### 🧠 Reasoning Skills

*Previously omitted from this page entirely - these 14 `claude_skills.py`
skills were also missing from `register_complete_claude_skills()` until
August 2026 (see Usage below). Full catalog:
[CATEGORIZATION.md](CATEGORIZATION.md).*

| Skill | Description |
|-------|-------------|
| `analyze_data` | Data set analysis and insights |
| `solve_math_problem` | Mathematical problem solving |
| `explain_code` | Code functionality explanation |
| `generate_code` | Code generation for tasks |
| `debug_code` | Bug identification and fixing |
| `analyze_complex_problem` | Systematic problem breakdown |
| `logical_reasoning` | Logical argument evaluation |
| `creative_writing` | Stories, poems, articles |
| `summarize_text` | Document summarization |
| `edit_improve_text` | Text editing and improvement |
| `statistical_analysis` | Statistical analysis on datasets |
| `extract_information` | Information extraction from text |
| `step_by_step_solver` | Complex problem solving |

---

## 🚀 Usage

### Quick Start

```python
from piranha_agent import Agent
from piranha_agent.complete_claude_skills import register_complete_claude_skills

# Create agent
agent = Agent(
    name="assistant",
    model="ollama/llama3:latest",
    description="AI assistant with all Claude skills"
)

# Register all 46 Claude skills
register_complete_claude_skills(agent)

# Or register specific categories
from piranha_agent.official_claude_skills import register_official_claude_skills
register_official_claude_skills(agent)  # 16 official skills

from piranha_agent.complete_claude_skills import register_additional_claude_skills
register_additional_claude_skills(agent)  # 16 additional skills
```

### Using Individual Skills

```python
from piranha_agent.complete_claude_skills import (
    deep_research,
    frontend_design,
    code_review,
)

# Research
result = deep_research(
    topic="AI agent frameworks",
    depth="deep",
    sources=["Academic papers", "Industry reports"]
)

# Frontend design
result = frontend_design(
    type="landing-page",
    style="Modern SaaS",
    features=["Hero section", "Features grid"]
)

# Code review
result = code_review(
    code=my_code,
    focus_areas=["Security", "Performance"]
)
```

---

## 📁 Skill Structure

Each skill follows the official Anthropic format:

```
skills/
├── skill-name/
│   ├── SKILL.md          # Skill definition
│   ├── README.md         # Usage documentation
│   └── resources/        # Additional resources
└── ...
```

### SKILL.md Format

```markdown
# Skill Name

## Overview
Description of what the skill does.

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

| Category | Count |
|----------|-------|
| Document Skills | 4 |
| Development Skills | 5 |
| Research Skills | 5 |
| Creative Skills | 5 |
| Communication Skills | 5 |
| Data Skills | 4 |
| Productivity Skills | 6 |
| Social Media Skills | 3 |
| Business Skills | 4 |
| Reasoning Skills | 5 |
| **Total** | **46** |

See [CATEGORIZATION.md](CATEGORIZATION.md) for the full per-skill
breakdown - this table previously omitted the Reasoning category (and
undercounted several others) because it only reflected the official +
additional skill modules, not `claude_skills.py`.

---

## 🔗 References

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Awesome Claude Skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [Piranha Agent Documentation](https://docs.piranha-agent.dev)

---

## 📝 Notes

1. **Skill Activation**: Skills are automatically activated based on context
2. **Progressive Disclosure**: Skills load in 3 tiers (metadata → instructions → resources)
3. **Security**: Review skills before enabling code execution
4. **Customization**: Create custom skills using `skill_creator`

---

## 🤝 Contributing

To contribute new skills:
1. Create skill directory
2. Write SKILL.md following the format
3. Add Python implementation
4. Add tests
5. Submit PR

---

*Last updated: March 2026; corrected against code August 2026.*
*Current package version: 0.4.2*
