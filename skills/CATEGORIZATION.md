# Piranha Agent Skills - Complete Categorization

Comprehensive categorization of all 46+ Claude Skills available in Piranha Agent.

---

## 📊 Skills Overview

| Category | Count | Module |
|----------|-------|--------|
| 📄 Document Processing | 4 | official_claude_skills |
| 💻 Development & Code | 5 | official_claude_skills + complete_claude_skills |
| 🔍 Research & Analysis | 5 | complete_claude_skills |
| 🎨 Creative & Design | 5 | official_claude_skills + complete_claude_skills |
| ✍️ Communication & Writing | 5 | official_claude_skills + complete_claude_skills |
| 📊 Data & Analytics | 4 | official_claude_skills + complete_claude_skills |
| 📁 Productivity & Workflow | 6 | official_claude_skills + complete_claude_skills |
| 🌐 Social Media | 3 | complete_claude_skills |
| 💼 Business & Marketing | 4 | complete_claude_skills |
| 🧠 Reasoning & Problem Solving | 5 | claude_skills |
| **TOTAL** | **46+** | **3 modules** |

---

## 📄 Category 1: Document Processing (4 skills)

*Official Anthropic Skills*

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `docx` | Create, edit, analyze Word documents | official_claude_skills | `docx_skill(action="create", content="...")` |
| `pdf` | Extract text, merge, split, annotate PDFs | official_claude_skills | `pdf_skill(action="extract", file_path="...")` |
| `pptx` | Create, edit PowerPoint presentations | official_claude_skills | `pptx_skill(action="create", slides=[...])` |
| `xlsx` | Create, edit Excel spreadsheets | official_claude_skills | `xlsx_skill(action="analyze", file_path="...")` |

**Use Cases:**
- Automated report generation
- Document conversion
- Data extraction from files
- Presentation creation

---

## 💻 Category 2: Development & Code (5 skills)

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `frontend-design` | React + Tailwind + shadcn/ui designs | official_claude_skills | `frontend_design(type="landing-page", ...)` |
| `mcp-builder` | Build MCP servers for API integration | official_claude_skills | `mcp_builder(api_name="Stripe", ...)` |
| `test-driven-development` | TDD methodology implementation | official_claude_skills | `test_driven_development(feature="...", ...)` |
| `code-review` | Code quality review | official_claude_skills | `code_review(code="...", focus_areas=[...])` |
| `software-architecture` | Clean Architecture, SOLID principles | complete_claude_skills | `software_architecture(project_type="...", ...)` |

**Use Cases:**
- Web application development
- API integration
- Code quality assurance
- System design

---

## 🔍 Category 3: Research & Analysis (5 skills)

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `deep-research` | Multi-step autonomous research | complete_claude_skills | `deep_research(topic="...", depth="deep")` |
| `root-cause-tracing` | Error tracing and root cause analysis | complete_claude_skills | `root_cause_tracing(error="...", ...)` |
| `lead-research-assistant` | Lead qualification and research | complete_claude_skills | `lead_research_assistant(industry="...", ...)` |
| `analyze_complex_problem` | Systematic problem breakdown | claude_skills | `analyze_complex_problem(problem="...", ...)` |
| `logical_reasoning` | Logical argument evaluation | claude_skills | `logical_reasoningpremises=[...], ...)` |

**Use Cases:**
- Market research
- Competitive analysis
- Debugging complex issues
- Strategic planning

---

## 🎨 Category 4: Creative & Design (5 skills)

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `canvas-design` | Visual art creation (PNG/PDF) | official_claude_skills | `canvas_design(type="poster", ...)` |
| `brand-guidelines` | Apply brand colors/typography | official_claude_skills | `brand_guidelines(artifact_type="...", ...)` |
| `brainstorming` | Structured idea development | complete_claude_skills | `brainstorming(idea="...", ...)` |
| `imagen` | AI image generation | complete_claude_skills | `imagen(prompt="...", style="...")` |
| `creative_writing` | Stories, poems, articles | claude_skills | `creative_writing(topic="...", format="...")` |

**Use Cases:**
- Marketing materials
- Brand consistency
- Creative campaigns
- Visual content creation

---

## ✍️ Category 5: Communication & Writing (5 skills)

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `internal-comms` | Status reports, newsletters, FAQs | official_claude_skills | `internal_comms(type="status-report", ...)` |
| `article-extractor` | Web article extraction | official_claude_skills | `article_extractor(url="...", ...)` |
| `content-research-writer` | Research-backed content writing | complete_claude_skills | `content_research_writer(topic="...", ...)` |
| `summarize_text` | Document summarization | claude_skills | `summarize_text(text="...", length="medium")` |
| `edit_improve_text` | Text editing and improvement | claude_skills | `edit_improve_text(text="...", goal="clarity")` |

**Use Cases:**
- Internal communications
- Content marketing
- Documentation
- Copywriting

---

## 📊 Category 6: Data & Analytics (4 skills)

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `csv-data-summarizer` | CSV analysis and insights | official_claude_skills | `csv_data_summarizer(file_path="...", ...)` |
| `postgres` | Safe read-only SQL queries | official_claude_skills | `postgres(query="SELECT...", ...)` |
| `statistical_analysis` | Statistical analysis on datasets | claude_skills | `statistical_analysis(data=[...], ...)` |
| `meeting-insights-analyzer` | Meeting transcript analysis | complete_claude_skills | `meeting_insights_analyzer(transcript="...", ...)` |

**Use Cases:**
- Data analysis
- Business intelligence
- Meeting summaries
- Database queries

---

## 📁 Category 7: Productivity & Workflow (6 skills)

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `file-organizer` | Intelligent file organization | official_claude_skills | `file_organizer(directory="...", ...)` |
| `git-workflows` | Git branch/PR management | official_claude_skills | `git_workflows(action="branch", ...)` |
| `skill-creator` | Interactive skill creation | complete_claude_skills | `skill_creator(skill_name="...", ...)` |
| `kaizen` | Continuous improvement methodology | complete_claude_skills | `kaizen(process="...", ...)` |
| `extract_information` | Information extraction from text | claude_skills | `extract_information(text="...", ...)` |
| `step_by_step_solver` | Complex problem solving | claude_skills | `step_by_step_solver(problem="...", ...)` |

**Use Cases:**
- Project organization
- Version control
- Process improvement
- Knowledge management

---

## 🌐 Category 8: Social Media (3 skills)

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `reddit-fetch` | Fetch Reddit content | complete_claude_skills | `reddit_fetch(subreddit="python", ...)` |
| `youtube-transcript` | YouTube transcript extraction | complete_claude_skills | `youtube_transcript(video_url="...", ...)` |
| `twitter-algorithm-optimizer` | Tweet optimization | complete_claude_skills | `twitter_algorithm_optimizer(content="...", ...)` |

**Use Cases:**
- Social media monitoring
- Content research
- Engagement optimization
- Trend analysis

---

## 💼 Category 9: Business & Marketing (4 skills)

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `competitive-ads-extractor` | Competitor ad analysis | complete_claude_skills | `competitive_ads_extractor(competitors=[...], ...)` |
| `domain-name-brainstormer` | Domain name generation | complete_claude_skills | `domain_name_brainstormer(keywords=[...], ...)` |
| `compare_options` | Multi-criteria comparison | claude_skills | `compare_options(options=[...], ...)` |
| `tailored-resume-generator` | Job-specific resume generation | complete_claude_skills | `tailored_resume_generator(job_description="...", ...)` |

**Use Cases:**
- Competitive intelligence
- Brand naming
- Decision making
- Career development

---

## 🧠 Category 10: Reasoning & Problem Solving (5 skills)

| Skill | Function | Module | Usage |
|-------|----------|--------|-------|
| `analyze_data` | Data set analysis and insights | claude_skills | `analyze_data(data_description="...", ...)` |
| `solve_math_problem` | Mathematical problem solving | claude_skills | `solve_math_problem(problem="...", ...)` |
| `explain_code` | Code functionality explanation | claude_skills | `explain_code(code="...", ...)` |
| `generate_code` | Code generation for tasks | claude_skills | `generate_code(task="...", ...)` |
| `debug_code` | Bug identification and fixing | claude_skills | `debug_code(code="...", ...)` |

**Use Cases:**
- Problem solving
- Code understanding
- Mathematical analysis
- Debugging

---

## 📦 By Source/Origin

### Official Anthropic Skills (16)
From https://github.com/anthropics/skills

```python
from piranha_agent.official_claude_skills import register_official_claude_skills
register_official_claude_skills(agent)
```

**Skills:** docx, pdf, pptx, xlsx, frontend-design, mcp-builder, test-driven-development, code-review, canvas-design, brand-guidelines, internal-comms, article-extractor, csv-data-summarizer, postgres, file-organizer, git-workflows

### Community Skills (16)
From https://github.com/ComposioHQ/awesome-claude-skills

```python
from piranha_agent.complete_claude_skills import register_additional_claude_skills
register_additional_claude_skills(agent)
```

**Skills:** deep-research, root-cause-tracing, lead-research-assistant, skill-creator, software-architecture, brainstorming, imagen, reddit-fetch, youtube-transcript, twitter-algorithm-optimizer, meeting-insights-analyzer, competitive-ads-extractor, domain-name-brainstormer, kaizen, content-research-writer, tailored-resume-generator

### Custom Skills (14)
Piranha-specific implementations

```python
from piranha_agent.claude_skills import register_claude_skills
register_claude_skills(agent)
```

**Skills:** analyze_complex_problem, logical_reasoning, explain_code, generate_code, debug_code, summarize_text, extract_information, solve_math_problem, statistical_analysis, creative_writing, edit_improve_text, analyze_data, compare_options, step_by_step_solver

---

## 🚀 Quick Reference by Use Case

### For Developers
```python
from piranha_agent.official_claude_skills import (
    frontend_design,
    mcp_builder,
    test_driven_development,
    code_review,
)
```

### For Researchers
```python
from piranha_agent.complete_claude_skills import (
    deep_research,
    root_cause_tracing,
    article_extractor,
)
```

### For Business Users
```python
from piranha_agent.complete_claude_skills import (
    competitive_ads_extractor,
    domain_name_brainstormer,
    lead_research_assistant,
    tailored_resume_generator,
)
```

### For Content Creators
```python
from piranha_agent.claude_skills import (
    creative_writing,
    summarize_text,
    edit_improve_text,
)
from piranha_agent.complete_claude_skills import (
    content_research_writer,
    brainstorming,
)
```

### For Data Analysts
```python
from piranha_agent.official_claude_skills import (
    csv_data_summarizer,
    postgres,
)
from piranha_agent.claude_skills import (
    statistical_analysis,
)
```

---

## 📋 Complete Skills List (Alphabetical)

1. `analyze_complex_problem` - claude_skills
2. `analyze_data` - claude_skills
3. `article-extractor` - official_claude_skills
4. `brainstorming` - complete_claude_skills
5. `brand-guidelines` - official_claude_skills
6. `canvas-design` - official_claude_skills
7. `code-review` - official_claude_skills
8. `competitive-ads-extractor` - complete_claude_skills
9. `content-research-writer` - complete_claude_skills
10. `creative_writing` - claude_skills
11. `csv-data-summarizer` - official_claude_skills
12. `debug_code` - claude_skills
13. `deep-research` - complete_claude_skills
14. `docx` - official_claude_skills
15. `domain-name-brainstormer` - complete_claude_skills
16. `edit_improve_text` - claude_skills
17. `explain_code` - claude_skills
18. `extract_information` - claude_skills
19. `file-organizer` - official_claude_skills
20. `frontend-design` - official_claude_skills
21. `generate_code` - claude_skills
22. `git-workflows` - official_claude_skills
23. `imagen` - complete_claude_skills
24. `internal-comms` - official_claude_skills
25. `kaizen` - complete_claude_skills
26. `lead-research-assistant` - complete_claude_skills
27. `logical_reasoning` - claude_skills
28. `mcp-builder` - official_claude_skills
29. `meeting-insights-analyzer` - complete_claude_skills
30. `pdf` - official_claude_skills
31. `postgres` - official_claude_skills
32. `pptx` - official_claude_skills
33. `reddit-fetch` - complete_claude_skills
34. `root-cause-tracing` - complete_claude_skills
35. `skill-creator` - complete_claude_skills
36. `software-architecture` - complete_claude_skills
37. `solve_math_problem` - claude_skills
38. `statistical_analysis` - claude_skills
39. `step_by_step_solver` - claude_skills
40. `summarize_text` - claude_skills
41. `tailored-resume-generator` - complete_claude_skills
42. `test-driven-development` - official_claude_skills
43. `twitter-algorithm-optimizer` - complete_claude_skills
44. `xlsx` - official_claude_skills
45. `youtube-transcript` - complete_claude_skills

---

## 📚 Documentation

- **Main Skills README:** `skills/README.md`
- **Module 1:** `piranha/claude_skills.py`
- **Module 2:** `piranha/official_claude_skills.py`
- **Module 3:** `piranha/complete_claude_skills.py`

---

*Last updated: March 2026*
*Version: 0.3.0*
*Total Skills: 46+*
