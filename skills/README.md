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
| `tailored-resume-generator` | Job-specific resume generation |

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

---

## 🚀 Usage

### Quick Start

```python
from piranha import Agent
from piranha.complete_claude_skills import register_complete_claude_skills

# Create agent
agent = Agent(
    name="assistant",
    model="ollama/llama3:latest",
    description="AI assistant with all Claude skills"
)

# Register ALL skills (100+)
register_complete_claude_skills(agent)

# Or register specific categories
from piranha.official_claude_skills import register_official_claude_skills
register_official_claude_skills(agent)  # 16 official skills

from piranha.complete_claude_skills import register_additional_claude_skills
register_additional_claude_skills(agent)  # 16 additional skills
```

### Using Individual Skills

```python
from piranha.complete_claude_skills import (
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
| Research Skills | 3 |
| Creative Skills | 4 |
| Communication Skills | 3 |
| Data Skills | 3 |
| Productivity Skills | 5 |
| Social Media Skills | 3 |
| Business Skills | 2 |
| **Total** | **32+** |

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

*Last updated: March 2026*
*Version: 0.3.0*
