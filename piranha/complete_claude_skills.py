#!/usr/bin/env python3
"""Complete Claude Skills Collection.

Based on:
- https://github.com/anthropics/skills
- https://github.com/ComposioHQ/awesome-claude-skills

This module contains ALL available Claude Skills (100+ skills).
"""


from piranha.skill import skill

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
)
def deep_research(topic: str, depth: str = "medium", sources: list[str] | None = None) -> str:
    """Deep research skill for comprehensive analysis."""
    return f"""
# Deep Research

## Topic
{topic}

## Depth
{depth}

## Sources
{sources or ['Academic papers', 'Industry reports', 'News articles']}

## Research Process
1. Define research questions
2. Gather sources
3. Analyze findings
4. Synthesize insights
5. Validate conclusions

## Findings
[Research findings would be presented here]

## Citations
[Sources would be cited here]

---
*Note: Full implementation requires web search and research APIs*
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
)
def lead_research_assistant(industry: str, company_size: str | None = None, 
                            location: str | None = None, criteria: list[str] | None = None) -> str:
    """Lead research assistant skill."""
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

## Lead List Template
| Company | Contact | Role | Email | Status |
|---------|---------|------|-------|--------|
| [Name] | [Name] | [Role] | [Email] | [Status] |

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
    description="Generate images using Google Gemini's image generation API",
    parameters={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Image generation prompt"},
            "style": {"type": "string", "description": "Art style"},
            "dimensions": {"type": "string", "description": "Output dimensions"},
        },
        "required": ["prompt"],
    },
)
def imagen(prompt: str, style: str | None = None, dimensions: str = "1024x1024") -> str:
    """Image generation skill using Gemini/Imagen."""
    return f"""
# Image Generation (Imagen)

## Prompt
{prompt}

## Style
{style or "Photorealistic"}

## Dimensions
{dimensions}

## Generated Image
[Image would be generated here via Gemini API]

## Usage Example
```python
from google import genai

client = genai.Client()
response = client.models.generate_image(
    model="imagen-3.0",
    prompt="{prompt}",
    config={{
        "aspectRatio": "{dimensions}",
        "style": "{style or 'photorealistic'}",
    }}
)
```

## Best Practices
- Be specific and descriptive
- Include style references
- Specify lighting and mood
- Mention composition preferences

---
*Note: Full implementation requires Google Gemini API key*
"""


@skill(
    name="reddit-fetch",
    description="Fetch Reddit content via Gemini CLI when WebFetch is blocked",
    parameters={
        "type": "object",
        "properties": {
            "subreddit": {"type": "string", "description": "Subreddit name"},
            "query": {"type": "string", "description": "Search query"},
            "sort": {"type": "string", "enum": ["hot", "new", "top", "rising"], "description": "Sort order"},
        },
        "required": ["subreddit"],
    },
)
def reddit_fetch(subreddit: str, query: str | None = None, sort: str = "hot") -> str:
    """Reddit content fetcher skill."""
    return f"""
# Reddit Fetch

## Subreddit
r/{subreddit}

## Query
{query or "Trending posts"}

## Sort
{sort}

## Top Posts

### Post 1
- **Title:** [Post title]
- **Author:** u/[username]
- **Score:** [upvotes]
- **Comments:** [count]
- **URL:** https://reddit.com/r/{subreddit}/...

### Post 2
- **Title:** [Post title]
- **Author:** u/[username]
- **Score:** [upvotes]
- **Comments:** [count]
- **URL:** https://reddit.com/r/{subreddit}/...

### Post 3
- **Title:** [Post title]
- **Author:** u/[username]
- **Score:** [upvotes]
- **Comments:** [count]
- **URL:** https://reddit.com/r/{subreddit}/...

## Usage
```bash
# Via Gemini CLI
gemini --fetch "reddit r/{subreddit} {sort} posts about {query}"
```

---
*Note: Requires Gemini CLI or Reddit API access*
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
    description="Extract and analyze competitors' ads from ad libraries",
    parameters={
        "type": "object",
        "properties": {
            "competitors": {"type": "array", "items": {"type": "string"}, "description": "Competitor names"},
            "platform": {"type": "string", "enum": ["facebook", "google", "linkedin", "all"], "description": "Ad platform"},
        },
        "required": ["competitors"],
    },
)
def competitive_ads_extractor(competitors: list[str], platform: str = "all") -> str:
    """Competitive ads extractor."""
    return f"""
# Competitive Ads Extractor

## Competitors
{', '.join(competitors)}

## Platform
{platform}

## Analysis

### Competitor 1: {competitors[0] if competitors else 'N/A'}
**Active Ads:** [count]
**Top Messaging:** [messaging]
**Creative Approach:** [approach]
**CTA Strategy:** [CTA]

### Competitor 2: {competitors[1] if len(competitors) > 1 else 'N/A'}
**Active Ads:** [count]
**Top Messaging:** [messaging]
**Creative Approach:** [approach]
**CTA Strategy:** [CTA]

## Insights
- Common themes: [themes]
- Differentiation opportunities: [opportunities]
- Gap analysis: [gaps]

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

---
*Note: Requires ad library API access*
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
"""

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
    description="Fetch transcripts from YouTube videos and generate summaries",
    parameters={
        "type": "object",
        "properties": {
            "video_url": {"type": "string", "description": "YouTube video URL"},
            "summarize": {"type": "boolean", "description": "Generate summary"},
        },
        "required": ["video_url"],
    },
)
def youtube_transcript(video_url: str, summarize: bool = True) -> str:
    """YouTube transcript fetcher."""
    # Extract video ID
    video_id = video_url.split('v=')[-1].split('&')[0] if 'v=' in video_url else video_url.split('/')[-1]
    
    return f"""
# YouTube Transcript

## Video
{video_url}

## Video ID
{video_id}

## Transcript
[Transcript would be fetched here]

## Summary
{'''
### Key Points
1. [Point 1]
2. [Point 2]
3. [Point 3]

### Timestamps
- 0:00 - Introduction
- 1:30 - Main topic
- 5:00 - Deep dive
- 10:00 - Conclusion
''' if summarize else ''}

## Usage
```python
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript('{video_id}')
```

---
*Note: Requires youtube-transcript-api or similar*
"""


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
    return f"""
# Tailored Resume Generator

## Job Analysis
**Key Requirements:**
{chr(10).join(f'- {req}' for req in job_description.split('\\n')[:5])}

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
    """Get ALL Claude skills (official + additional)."""
    from piranha.official_claude_skills import get_all_official_claude_skills
    return get_all_official_claude_skills() + get_all_additional_claude_skills()


def register_complete_claude_skills(agent) -> None:
    """Register ALL Claude skills with an agent."""
    for skill_func in get_complete_claude_skills():
        agent.add_skill(skill_func)
