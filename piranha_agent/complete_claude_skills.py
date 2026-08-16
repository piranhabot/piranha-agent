#!/usr/bin/env python3
"""Complete Claude Skills Collection.

Based on:
- https://github.com/anthropics/skills
- https://github.com/ComposioHQ/awesome-claude-skills

This module contains 16 "additional" Claude skills (corrected August
2026 - previously claimed "100+", which was never true; see
docs/SKILLS_REGISTRATION.md for the full, verified per-module count).
"""


from piranha_agent.skill import skill

# =============================================================================
# Research & Analysis Skills
# =============================================================================

@skill(
    name="deep-research",
    description="Execute autonomous multi-step research using deep research agents",
    parameters={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Research topic"},
            "depth": {"type": "string", "enum": ["shallow", "medium", "deep"], "description": "Research depth"},
            "sources": {"type": "array", "items": {"type": "string"}, "description": "Preferred sources"},
        },
        "required": ["topic"],
    },
    permissions=["network_read"],
)
def deep_research(topic: str, depth: str = "medium", sources: list[str] | None = None) -> str:
    """Deep research skill - runs a real web search, not an LLM-only template.

    "sources" (preferred source types) is accepted but not currently used
    to filter/bias search results - it's echoed back for now.
    "depth" controls how many search results are pulled (shallow=3,
    medium=6, deep=10), not a multi-step research pipeline.
    """
    from piranha_agent.skills._web_research import web_search

    max_results = {"shallow": 3, "medium": 6, "deep": 10}.get(depth, 6)
    try:
        results = web_search(topic, max_results=max_results)
    except ImportError as e:
        return f"❌ Error: {e}"
    except Exception as e:
        return f"❌ Error searching for '{topic}': {e}"

    if not results:
        findings = "No search results found."
        citations = "(none)"
    else:
        findings = "\n\n".join(
            f"### {i}. {r['title']}\n{r['snippet']}\nSource: {r['url']}"
            for i, r in enumerate(results, 1)
        )
        citations = "\n".join(f"- [{r['title']}]({r['url']})" for r in results)

    return f"""
# Deep Research

## Topic
{topic}

## Depth
{depth} ({max_results} sources searched)

## Preferred Source Types (not used to filter results)
{sources or ['Academic papers', 'Industry reports', 'News articles']}

## Findings
{findings}

## Citations
{citations}

---
*Web search via DuckDuckGo (ddgs) - this returns real search results and
snippets, not full-text synthesis or fact-checking. Treat as a research
starting point, not a finished report.*
"""


@skill(
    name="root-cause-tracing",
    description="Trace errors deep in execution to find original triggers",
    parameters={
        "type": "object",
        "properties": {
            "error": {"type": "string", "description": "Error message or symptom"},
            "context": {"type": "string", "description": "System/context where error occurred"},
            "timeline": {"type": "string", "description": "When the error started"},
        },
        "required": ["error"],
    },
)
def root_cause_tracing(error: str, context: str | None = None, timeline: str | None = None) -> str:
    """Root cause analysis skill."""
    return f"""
# Root Cause Tracing

## Error
{error}

## Context
{context or "Not specified"}

## Timeline
{timeline or "Not specified"}

## Analysis Method: 5 Whys

### Why 1?
[Initial cause]

### Why 2?
[Deeper cause]

### Why 3?
[Root cause emerging]

### Why 4?
[Getting to root]

### Why 5?
[Root cause identified]

## Contributing Factors
- [Factor 1]
- [Factor 2]
- [Factor 3]

## Recommended Fixes
1. Immediate: [Quick fix]
2. Short-term: [Proper fix]
3. Long-term: [Preventive measure]

---
*Based on root cause analysis best practices*
"""


@skill(
    name="lead-research-assistant",
    description="Identify and qualify high-quality leads with actionable outreach strategies",
    parameters={
        "type": "object",
        "properties": {
            "industry": {"type": "string", "description": "Target industry"},
            "company_size": {"type": "string", "description": "Company size range"},
            "location": {"type": "string", "description": "Geographic location"},
            "criteria": {"type": "array", "items": {"type": "string"}, "description": "Lead criteria"},
        },
        "required": ["industry"],
    },
    permissions=["network_read"],
)
def lead_research_assistant(industry: str, company_size: str | None = None,
                            location: str | None = None, criteria: list[str] | None = None) -> str:
    """Lead research assistant skill - finds real candidate companies via web
    search to research further.

    Deliberately does NOT fabricate named contacts/emails - a plain web
    search can't verify who the actual decision-maker or their contact
    info is, and presenting invented names/emails as real leads would be
    worse than an honest placeholder. It surfaces real companies matching
    the criteria as a starting point for the outreach strategy below.
    """
    from piranha_agent.skills._web_research import web_search

    query = f"{industry} companies" + (f" in {location}" if location else "")
    if company_size:
        query += f" {company_size}"
    try:
        results = web_search(query, max_results=8)
    except ImportError as e:
        return f"❌ Error: {e}"
    except Exception as e:
        return f"❌ Error searching for '{query}': {e}"

    candidates = "\n".join(f"| {r['title']} | {r['url']} |" for r in results) if results else "| (no results) | - |"

    return f"""
# Lead Research Assistant

## Target Profile
- **Industry:** {industry}
- **Company Size:** {company_size or "Any"}
- **Location:** {location or "Global"}

## Criteria
{chr(10).join(f'- {c}' for c in (criteria or ['Decision maker access', 'Budget available', 'Active hiring']))}

## Lead Qualification Framework: BANT
- **Budget:** Does the prospect have budget?
- **Authority:** Are we talking to the decision maker?
- **Need:** Do they have a need for our solution?
- **Timeline:** What is their implementation timeline?

## Outreach Strategy
1. Research company news
2. Identify pain points
3. Craft personalized message
4. Choose optimal channel
5. Follow-up sequence

## Candidate Companies (from web search: "{query}")
| Result | Link |
|--------|------|
{candidates}

*These are real search results for the query above, not verified leads -
no contact names/emails are fabricated. Use these as a starting point,
then research each company's actual decision-makers before outreach.*

---
*Based on sales best practices*
"""


@skill(
    name="skill-creator",
    description="Interactive tool for creating effective Claude Skills",
    parameters={
        "type": "object",
        "properties": {
            "skill_name": {"type": "string", "description": "Name of the skill to create"},
            "purpose": {"type": "string", "description": "What the skill should do"},
            "target_audience": {"type": "string", "description": "Who will use this skill"},
        },
        "required": ["skill_name", "purpose"],
    },
)
def skill_creator(skill_name: str, purpose: str, target_audience: str | None = None) -> str:
    """Skill creator interactive tool."""
    return f"""
# Skill Creator

## Creating: {skill_name}

### Purpose
{purpose}

### Target Audience
{target_audience or "General users"}

## Skill Structure

### 1. Metadata
```yaml
name: {skill_name}
version: "1.0.0"
description: {purpose}
author: [Your name]
```

### 2. Instructions
```markdown
# {skill_name}

## Overview
[Describe what this skill does]

## When to Use
[Describe when Claude should activate this skill]

## Process
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Output Format
[Describe expected output]
```

### 3. Resources
- [List any files, templates, or references]

### 4. Testing
- Test with sample inputs
- Verify output quality
- Refine instructions

## Next Steps
1. Create SKILL.md file
2. Add any resource files
3. Test the skill
4. Share with team

---
*Based on official Anthropic skill-creator skill*
"""


@skill(
    name="software-architecture",
    description="Implement design patterns: Clean Architecture, SOLID principles, best practices",
    parameters={
        "type": "object",
        "properties": {
            "project_type": {"type": "string", "description": "Type of project"},
            "language": {"type": "string", "description": "Programming language"},
            "scale": {"type": "string", "enum": ["small", "medium", "enterprise"], "description": "Project scale"},
        },
        "required": ["project_type"],
    },
)
def software_architecture(project_type: str, language: str = "typescript", scale: str = "medium") -> str:
    """Software architecture skill."""
    return f"""
# Software Architecture

## Project
- **Type:** {project_type}
- **Language:** {language}
- **Scale:** {scale}

## SOLID Principles

### S - Single Responsibility
Each class should have one reason to change.

### O - Open/Closed
Open for extension, closed for modification.

### L - Liskov Substitution
Subtypes must be substitutable for base types.

### I - Interface Segregation
Many specific interfaces > one general interface.

### D - Dependency Inversion
Depend on abstractions, not concretions.

## Clean Architecture Layers

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│         (UI, API, Controllers)      │
├─────────────────────────────────────┤
│          Domain Layer               │
│      (Entities, Use Cases)          │
├─────────────────────────────────────┤
│         Data Layer                  │
│    (Repositories, Data Sources)     │
└─────────────────────────────────────┘
```

## Recommended Structure
```
src/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   └── services/
├── application/
│   ├── use_cases/
│   └── interfaces/
├── infrastructure/
│   ├── repositories/
│   └── external/
└── presentation/
    ├── controllers/
    └── views/
```

---
*Based on Clean Architecture and SOLID principles*
"""


@skill(
    name="brainstorming",
    description="Transform rough ideas into fully-formed designs through structured questioning",
    parameters={
        "type": "object",
        "properties": {
            "idea": {"type": "string", "description": "Initial idea or concept"},
            "domain": {"type": "string", "description": "Domain/context"},
            "constraints": {"type": "array", "items": {"type": "string"}, "description": "Constraints to consider"},
        },
        "required": ["idea"],
    },
)
def brainstorming(idea: str, domain: str | None = None, constraints: list[str] | None = None) -> str:
    """Brainstorming skill for idea development."""
    return f"""
# Brainstorming Session

## Initial Idea
{idea}

## Domain
{domain or "General"}

## Constraints
{chr(10).join(f'- {c}' for c in (constraints or ['None specified']))}

## Divergent Thinking

### What If Questions
- What if we had unlimited resources?
- What if this was for 10M users?
- What if we had to launch in 24 hours?
- What if this was our only feature?

### Alternative Approaches
1. [Alternative 1]
2. [Alternative 2]
3. [Alternative 3]

### Analogous Solutions
- How do others solve this?
- What can we learn from other industries?

## Convergent Thinking

### Evaluation Criteria
| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Feasibility | High | - | - | - |
| Impact | High | - | - | - |
| Cost | Medium | - | - | - |
| Time | Medium | - | - | - |

### Recommended Direction
[Selected approach with justification]

## Next Steps
1. [Action 1]
2. [Action 2]
3. [Action 3]

---
*Based on design thinking methodology*
"""


@skill(
    name="imagen",
    description="Generate images via a real image-gen API (LiteLLM - DALL-E, Gemini/Imagen, etc.)",
    parameters={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Image generation prompt"},
            "style": {"type": "string", "description": "Art style"},
            "dimensions": {"type": "string", "description": "Output dimensions"},
        },
        "required": ["prompt"],
    },
    permissions=["network_read", "external_api"],
)
def imagen(prompt: str, style: str | None = None, dimensions: str = "1024x1024") -> str:
    """Image generation skill - real API call via LiteLLM, not a template.

    Model defaults to PIRANHA_IMAGE_MODEL env var, falling back to
    "dall-e-3" (needs OPENAI_API_KEY). Set PIRANHA_IMAGE_MODEL to any
    LiteLLM-supported image model string (e.g. "gemini/imagen-3.0-generate-002"
    with GEMINI_API_KEY) to use a different provider - same env-var-driven
    config pattern as Agent's own LLM provider selection, not hardcoded to
    one vendor like the old "via Gemini API" description implied.

    This has not been live-tested in this session (no image-gen API key
    available) - the call shape is verified against litellm's real
    image_generation() signature, but treat it as less-verified than the
    other skills fixed alongside it (web search, YouTube transcripts,
    Postgres) which were tested against live services.
    """
    import os

    full_prompt = f"{prompt}, {style} style" if style else prompt
    model = os.environ.get("PIRANHA_IMAGE_MODEL", "dall-e-3")

    try:
        import litellm
    except ImportError:
        return "❌ Error: the 'imagen' skill requires litellm (should already be installed as a core dependency)"

    try:
        response = litellm.image_generation(prompt=full_prompt, model=model, size=dimensions, n=1)
    except Exception as e:
        return f"❌ Error generating image via '{model}': {e}"

    image = response.data[0] if response.data else None
    image_ref = (
        f"URL: {image.get('url')}" if image and image.get("url")
        else "base64 image data returned (not printed here)" if image and image.get("b64_json")
        else "(no image data returned)"
    )

    return f"""
# Image Generation (Imagen)

## Prompt
{full_prompt}

## Model
{model}

## Dimensions
{dimensions}

## Generated Image
{image_ref}
"""


@skill(
    name="reddit-fetch",
    description="Fetch real Reddit posts via the official Reddit API (read-only)",
    parameters={
        "type": "object",
        "properties": {
            "subreddit": {"type": "string", "description": "Subreddit name"},
            "query": {"type": "string", "description": "Search query"},
            "sort": {"type": "string", "enum": ["hot", "new", "top", "rising"], "description": "Sort order"},
        },
        "required": ["subreddit"],
    },
    permissions=["network_read"],
)
def reddit_fetch(subreddit: str, query: str | None = None, sort: str = "hot") -> str:
    """Reddit content fetcher - real posts via PRAW (Reddit's official API),
    not the old "Gemini CLI" reference (that tool doesn't exist anywhere in
    this codebase - it was never real).

    Reddit's unauthenticated public .json endpoints now return 403 for most
    non-browser clients (verified August 2026), so this requires a real,
    free Reddit "script" app: create one at
    https://www.reddit.com/prefs/apps, then set PIRANHA_REDDIT_CLIENT_ID
    and PIRANHA_REDDIT_CLIENT_SECRET. No user login/password needed - this
    only uses read-only app-only auth.
    """
    import os

    client_id = os.environ.get("PIRANHA_REDDIT_CLIENT_ID")
    client_secret = os.environ.get("PIRANHA_REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        return (
            "❌ Error: PIRANHA_REDDIT_CLIENT_ID / PIRANHA_REDDIT_CLIENT_SECRET "
            "environment variables are not set. Create a free Reddit \"script\" "
            "app at https://www.reddit.com/prefs/apps and set both."
        )

    try:
        import praw
    except ImportError:
        return (
            "❌ Error: the 'reddit-fetch' skill requires praw. Install with: "
            'pip install "piranha-agent[reddit]"'
        )

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="PiranhaAgent/1.0 (skill:reddit-fetch)",
        )
        sub = reddit.subreddit(subreddit)
        if query:
            # PRAW search sort values differ from listing sort - "rising"
            # isn't a valid search sort, fall back to "hot" for search.
            search_sort = sort if sort in ("relevance", "hot", "top", "new", "comments") else "hot"
            submissions = list(sub.search(query, sort=search_sort, limit=10))
        else:
            listing = {"hot": sub.hot, "new": sub.new, "top": sub.top, "rising": sub.rising}[sort]
            submissions = list(listing(limit=10))
    except Exception as e:
        return f"❌ Error fetching r/{subreddit}: {e}"

    if not submissions:
        posts_text = "(no posts found)"
    else:
        posts_text = "\n\n".join(
            f"### {s.title}\n"
            f"- **Author:** u/{s.author}\n"
            f"- **Score:** {s.score}\n"
            f"- **Comments:** {s.num_comments}\n"
            f"- **URL:** https://reddit.com{s.permalink}"
            for s in submissions
        )

    return f"""
# Reddit Fetch

## Subreddit
r/{subreddit}

## Query
{query or "Trending posts"}

## Sort
{sort}

## Posts ({len(submissions)})

{posts_text}
"""


# =============================================================================
# Additional High-Value Skills
# =============================================================================

@skill(
    name="meeting-insights-analyzer",
    description="Analyze meeting transcripts for behavioral patterns and insights",
    parameters={
        "type": "object",
        "properties": {
            "transcript": {"type": "string", "description": "Meeting transcript"},
            "analysis_type": {"type": "string", "enum": ["speaking-time", "sentiment", "action-items", "full"], "description": "Analysis type"},
        },
        "required": ["transcript"],
    },
)
def meeting_insights_analyzer(transcript: str, analysis_type: str = "full") -> str:
    """Meeting insights analyzer."""
    return f"""
# Meeting Insights Analyzer

## Analysis Type
{analysis_type}

## Transcript Length
{len(transcript.split())} words

## Key Metrics

### Speaking Time Distribution
| Speaker | Time | Percentage |
|---------|------|------------|
| [Name] | [X] min | [X]% |

### Sentiment Analysis
- Positive: [X]%
- Neutral: [X]%
- Negative: [X]%

### Action Items Identified
1. [Action item 1] - [Owner]
2. [Action item 2] - [Owner]
3. [Action item 3] - [Owner]

### Key Decisions
- [Decision 1]
- [Decision 2]

### Follow-ups Needed
- [Follow-up 1]
- [Follow-up 2]

---
*Note: Full implementation requires NLP processing*
"""


@skill(
    name="competitive-ads-extractor",
    description="Find real web results about competitors' advertising (not a dedicated ad-library API)",
    parameters={
        "type": "object",
        "properties": {
            "competitors": {"type": "array", "items": {"type": "string"}, "description": "Competitor names"},
            "platform": {"type": "string", "enum": ["facebook", "google", "linkedin", "all"], "description": "Ad platform"},
        },
        "required": ["competitors"],
    },
    permissions=["network_read"],
)
def competitive_ads_extractor(competitors: list[str], platform: str = "all") -> str:
    """Competitive ads extractor.

    Real ad-library APIs (Meta Ad Library, Google Ads Transparency Center)
    require gated developer credentials this skill doesn't have, and
    scraping them directly is ToS-fragile. Instead of faking ad-specific
    data with those APIs' shape, this does a real web search per
    competitor for their advertising/campaigns and is honest about the
    difference - it will NOT return per-ad creative/CTA/spend data the
    way a real ad-library integration would.
    """
    from piranha_agent.skills._web_research import web_search

    platform_term = "" if platform == "all" else f" {platform}"
    sections = []
    for competitor in competitors:
        query = f"{competitor}{platform_term} advertising campaign"
        try:
            results = web_search(query, max_results=5)
        except ImportError as e:
            return f"❌ Error: {e}"
        except Exception as e:
            sections.append(f"### {competitor}\n❌ Error searching: {e}")
            continue
        if results:
            hits = "\n".join(f"- [{r['title']}]({r['url']}) - {r['snippet']}" for r in results)
        else:
            hits = "(no results)"
        sections.append(f"### {competitor}\n{hits}")

    analysis = "\n\n".join(sections) if sections else "(no competitors provided)"

    return f"""
# Competitive Ads Extractor

## Competitors
{', '.join(competitors)}

## Platform
{platform}

## Web Search Results (not ad-library data)
{analysis}

---
*This is general web search about each competitor's advertising, not
per-ad creative/CTA/spend data from Meta Ad Library or Google Ads
Transparency Center - those require gated developer API access this
skill doesn't have configured. Use these results as a research starting
point, not a substitute for the real ad-library tools.*
"""


@skill(
    name="domain-name-brainstormer",
    description="Generate creative domain names and check availability",
    parameters={
        "type": "object",
        "properties": {
            "keywords": {"type": "array", "items": {"type": "string"}, "description": "Keywords to include"},
            "style": {"type": "string", "enum": ["descriptive", "abstract", "compound", "all"], "description": "Naming style"},
            "tlds": {"type": "array", "items": {"type": "string"}, "description": "Preferred TLDs"},
        },
        "required": ["keywords"],
    },
)
def domain_name_brainstormer(keywords: list[str], style: str = "all",
                             tlds: list[str] | None = None) -> str:
    """Domain name brainstormer."""
    tlds_list = tlds or ['.com', '.io', '.dev', '.ai']
    tld_headers = " | ".join(tlds_list)

    return f"""
# Domain Name Brainstormer

## Keywords
{', '.join(keywords)}

## Style
{style}

## TLDs
{tld_headers}

## Generated Names

### Descriptive
| Name | .com | .io | .dev | .ai |
|------|------|-----|------|-----|
| {keywords[0]}app.com | ? | ? | ? | ? |
| get{keywords[0]}.com | ? | ? | ? | ? |
| {keywords[0]}hq.com | ? | ? | ? | ? |

### Abstract
| Name | .com | .io | .dev | .ai |
|------|------|-----|------|-----|
| zentra.com | ? | ? | ? | ? |
| novus.io | ? | ? | ? | ? |
| velox.dev | ? | ? | ? | ? |

### Compound
| Name | .com | .io | .dev | .ai |
|------|------|-----|------|-----|
| {keywords[0]}flow.com | ? | ? | ? | ? |
| {keywords[0]}lab.io | ? | ? | ? | ? |

## Availability Check
[Would check domain availability via API]

## Recommendations
1. [Top pick 1]
2. [Top pick 2]
3. [Top pick 3]

---
*Note: Full implementation requires domain availability API*
"""


@skill(
    name="youtube-transcript",
    description="Fetch real transcripts from YouTube videos",
    parameters={
        "type": "object",
        "properties": {
            "video_url": {"type": "string", "description": "YouTube video URL"},
            "summarize": {"type": "boolean", "description": "Generate summary"},
        },
        "required": ["video_url"],
    },
    permissions=["network_read"],
)
def youtube_transcript(video_url: str, summarize: bool = True) -> str:
    """YouTube transcript fetcher - fetches the real transcript via
    youtube-transcript-api (no API key needed).

    "summarize" does NOT generate an LLM summary itself - this is a plain
    function with no LLM access. When true, it just adds a note pointing
    the calling agent at the real transcript text below to summarize -
    previously this returned fabricated "[Point 1]"/"[Point 2]" bullets
    and fake timestamps regardless of the video's actual content.
    """
    video_id = video_url.split('v=')[-1].split('&')[0] if 'v=' in video_url else video_url.split('/')[-1]

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return (
            "❌ Error: the 'youtube-transcript' skill requires the "
            "youtube-transcript-api package. Install with: "
            "pip install youtube-transcript-api"
        )

    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)
    except Exception as e:
        return f"❌ Error fetching transcript for video ID '{video_id}': {e}"

    lines = [f"[{snippet.start:.0f}s] {snippet.text}" for snippet in fetched]
    transcript_text = "\n".join(lines)

    summary_note = (
        "\n## Summary\n*Not generated here - this skill has no LLM access. "
        "Ask the calling agent to summarize the transcript above.*\n"
        if summarize
        else ""
    )

    return f"""
# YouTube Transcript

## Video
{video_url}

## Video ID
{video_id}

## Transcript ({len(lines)} segments)
{transcript_text}
{summary_note}"""


@skill(
    name="kaizen",
    description="Apply continuous improvement methodology based on Japanese Kaizen philosophy",
    parameters={
        "type": "object",
        "properties": {
            "process": {"type": "string", "description": "Process to improve"},
            "current_issues": {"type": "array", "items": {"type": "string"}, "description": "Current issues"},
        },
        "required": ["process"],
    },
)
def kaizen(process: str, current_issues: list[str] | None = None) -> str:
    """Kaizen continuous improvement skill."""
    return f"""
# Kaizen Continuous Improvement

## Process
{process}

## Current Issues
{chr(10).join(f'- {issue}' for issue in (current_issues or ['Not specified']))}

## Kaizen Principles
1. Focus on small, incremental changes
2. Everyone participates (management + workers)
3. Low cost, high impact
4. Continuous, not one-time

## PDCA Cycle

### Plan
- Identify opportunity
- Analyze current state
- Set improvement goals
- Develop action plan

### Do
- Implement changes
- Document process
- Train team members

### Check
- Measure results
- Compare to baseline
- Identify learnings

### Act
- Standardize successful changes
- Address remaining issues
- Start next cycle

## 5S Framework
1. **Sort** - Remove unnecessary items
2. **Set in Order** - Organize remaining items
3. **Shine** - Clean and inspect
4. **Standardize** - Create standards
5. **Sustain** - Maintain improvements

## Recommended Actions
1. [Action 1]
2. [Action 2]
3. [Action 3]

---
*Based on Toyota Kaizen methodology*
"""


@skill(
    name="content-research-writer",
    description="Write high-quality content with research, citations, and improved hooks",
    parameters={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Content topic"},
            "format": {"type": "string", "enum": ["blog", "article", "whitepaper", "social"], "description": "Content format"},
            "tone": {"type": "string", "description": "Writing tone"},
            "word_count": {"type": "integer", "description": "Target word count"},
        },
        "required": ["topic", "format"],
    },
)
def content_research_writer(topic: str, format: str, tone: str | None = None, 
                           word_count: int | None = None) -> str:
    """Content research writer skill."""
    return f"""
# Content Research Writer

## Topic
{topic}

## Format
{format}

## Tone
{tone or "Professional"}

## Target Length
{word_count or '800-1200'} words

## Content Structure

### Hook
[Compelling opening that grabs attention]

### Introduction
- Context setting
- Problem statement
- Promise to reader

### Body

#### Section 1: [Key Point 1]
[Content with research and citations]

#### Section 2: [Key Point 2]
[Content with research and citations]

#### Section 3: [Key Point 3]
[Content with research and citations]

### Conclusion
- Summary of key points
- Call to action
- Final thought

## Research Sources
1. [Source 1]
2. [Source 2]
3. [Source 3]

## SEO Optimization
- Primary keyword: [keyword]
- Secondary keywords: [keywords]
- Meta description: [description]

---
*Based on content marketing best practices*
"""


@skill(
    name="tailored-resume-generator",
    description="Generate tailored resumes that highlight relevant experience for job applications",
    parameters={
        "type": "object",
        "properties": {
            "job_description": {"type": "string", "description": "Job description"},
            "experience": {"type": "string", "description": "Candidate experience"},
            "skills": {"type": "array", "items": {"type": "string"}, "description": "Candidate skills"},
        },
        "required": ["job_description", "experience"],
    },
)
def tailored_resume_generator(job_description: str, experience: str,
                              skills: list[str] | None = None) -> str:
    """Tailored resume generator."""
    # Fix: Cannot use backslash in f-string expression
    lines = job_description.split('\n')[:5]
    requirements = '\n'.join(f'- {req}' for req in lines)
    return f"""
# Tailored Resume Generator

## Job Analysis
**Key Requirements:**
{requirements}

**Keywords to Include:**
[Extracted from job description]

## Resume

### Contact Information
[Name] | [Email] | [Phone] | [LinkedIn] | [Location]

### Professional Summary
[2-3 sentences highlighting most relevant experience for THIS role]

### Skills
{', '.join(skills) if skills else '[Skills matched to job requirements]'}

### Experience

#### [Most Recent Role]
[Company] | [Dates]
- Achievement 1 (quantified, relevant to job)
- Achievement 2 (quantified, relevant to job)
- Achievement 3 (quantified, relevant to job)

#### [Previous Role]
[Company] | [Dates]
- Achievement 1 (quantified)
- Achievement 2 (quantified)

### Education
[Degree] | [University] | [Year]

### Projects/Certifications
[Relevant to job description]

## ATS Optimization
- Keywords matched: [count]
- Format: ATS-friendly
- Length: 1-2 pages

---
*Based on resume best practices and ATS optimization*
"""


@skill(
    name="twitter-algorithm-optimizer",
    description="Optimize tweets for maximum reach using Twitter's algorithm insights",
    parameters={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "Tweet content to optimize"},
            "goal": {"type": "string", "enum": ["engagement", "reach", "clicks", "follows"], "description": "Optimization goal"},
        },
        "required": ["content"],
    },
)
def twitter_algorithm_optimizer(content: str, goal: str = "engagement") -> str:
    """Twitter algorithm optimizer."""
    return f"""
# Twitter Algorithm Optimizer

## Original Tweet
{content}

## Optimization Goal
{goal}

## Analysis

### Current State
- **Length:** {len(content)} characters
- **Hashtags:** {content.count('#')}
- **Mentions:** {content.count('@')}
- **Media:** [None detected]
- **Hook:** [Assessment]

### Optimized Version

**Option 1 (Engagement-focused):**
[Optimized tweet with question/CTA]

**Option 2 (Reach-focused):**
[Optimized tweet with trending hashtags]

**Option 3 (Click-focused):**
[Optimized tweet with link placement]

## Best Practices Applied

### Twitter Algorithm Factors (2025)
1. ✅ Recency - Post at optimal time
2. ✅ Engagement - Include engagement hook
3. ✅ Media - Add image/video
4. ✅ Hashtags - Use 2-3 relevant tags
5. ✅ Length - Leave room for engagement
6. ✅ Replies - Plan follow-up thread

### Recommended Hashtags
- #[Hashtag1]
- #[Hashtag2]
- #[Hashtag3]

### Optimal Posting Times
- Tuesday-Thursday: 9-11 AM
- Wednesday: Best overall day

---
*Based on Twitter's open-source algorithm insights*
"""


# =============================================================================
# Helper Functions
# =============================================================================

def get_all_additional_claude_skills() -> list:
    """Get list of all additional Claude skills."""
    return [
        # Research & Analysis
        deep_research,
        root_cause_tracing,
        lead_research_assistant,
        # Skill Creation
        skill_creator,
        # Architecture
        software_architecture,
        # Creative
        brainstorming,
        imagen,
        # Social Media
        reddit_fetch,
        youtube_transcript,
        twitter_algorithm_optimizer,
        # Business
        meeting_insights_analyzer,
        competitive_ads_extractor,
        domain_name_brainstormer,
        # Productivity
        kaizen,
        content_research_writer,
        tailored_resume_generator,
    ]


def register_additional_claude_skills(agent) -> None:
    """Register all additional Claude skills with an agent."""
    for skill_func in get_all_additional_claude_skills():
        agent.add_skill(skill_func)


def get_complete_claude_skills() -> list:
    """Get ALL Claude skills (core + official + additional).

    Previously omitted the 14 skills from claude_skills.py despite the
    name/docstring promising "ALL" - callers of register_complete_claude_skills()
    were silently missing analyze_data, generate_code, debug_code, etc.
    """
    from piranha_agent.claude_skills import get_all_claude_skills
    from piranha_agent.official_claude_skills import get_all_official_claude_skills
    return get_all_claude_skills() + get_all_official_claude_skills() + get_all_additional_claude_skills()


def register_complete_claude_skills(agent) -> None:
    """Register ALL Claude skills with an agent."""
    for skill_func in get_complete_claude_skills():
        agent.add_skill(skill_func)
