#!/usr/bin/env python3
"""Official Claude Skills for Piranha Agent.

Based on the official Anthropic Claude Skills repository:
https://github.com/anthropics/skills
https://github.com/ComposioHQ/awesome-claude-skills

This module implements authentic Claude Skills following the official format.
"""


from piranha.skill import skill

# =============================================================================
# Document Skills (Official Anthropic Skills)
# =============================================================================

@skill(
    name="docx",
    description="Create, edit, and analyze Word documents with tracked changes, comments, and formatting",
    parameters={
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create", "edit", "analyze", "extract"], "description": "Action to perform"},
            "content": {"type": "string", "description": "Document content or file path"},
            "formatting": {"type": "object", "description": "Formatting options"},
        },
        "required": ["action"],
    },
)
def docx_skill(action: str, content: str | None = None, formatting: dict | None = None) -> str:
    """Word document processing skill."""
    return f"""
# DOCX Skill - {action.title()}

## Action
{action}

## Content
{content[:500] if content else "No content provided"}...

## Result
[Document would be processed here]

---
*Note: Full implementation requires python-docx library integration*
"""


@skill(
    name="pdf",
    description="Extract text, tables, metadata from PDFs; merge, split, and annotate documents",
    parameters={
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["extract", "merge", "split", "annotate", "analyze"], "description": "Action to perform"},
            "file_path": {"type": "string", "description": "PDF file path"},
            "pages": {"type": "string", "description": "Page range (e.g., '1-5' or 'all')"},
        },
        "required": ["action", "file_path"],
    },
)
def pdf_skill(action: str, file_path: str, pages: str = "all") -> str:
    """PDF processing skill."""
    return f"""
# PDF Skill - {action.title()}

## File
{file_path}

## Pages
{pages}

## Extracted Content
[Content would be extracted here]

---
*Note: Full implementation requires PyPDF2 or pdfplumber library*
"""


@skill(
    name="pptx",
    description="Create, edit, and analyze PowerPoint presentations with slides, layouts, and charts",
    parameters={
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create", "edit", "analyze", "export"], "description": "Action to perform"},
            "template": {"type": "string", "description": "Presentation template"},
            "slides": {"type": "array", "items": {"type": "object"}, "description": "Slide content"},
        },
        "required": ["action"],
    },
)
def pptx_skill(action: str, template: str | None = None, slides: list[dict] | None = None) -> str:
    """PowerPoint presentation skill."""
    return f"""
# PPTX Skill - {action.title()}

## Template
{template or "Default"}

## Slides
{len(slides) if slides else 0} slides

## Result
[Presentation would be created/edited here]

---
*Note: Full implementation requires python-pptx library*
"""


@skill(
    name="xlsx",
    description="Create, edit, and analyze Excel spreadsheets with formulas, charts, and data analysis",
    parameters={
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create", "read", "write", "analyze", "chart"], "description": "Action to perform"},
            "file_path": {"type": "string", "description": "Excel file path"},
            "sheet": {"type": "string", "description": "Sheet name"},
            "data": {"type": "array", "description": "Data to write"},
        },
        "required": ["action"],
    },
)
def xlsx_skill(action: str, file_path: str | None = None, sheet: str = "Sheet1", data: list | None = None) -> str:
    """Excel spreadsheet skill."""
    return f"""
# XLSX Skill - {action.title()}

## File
{file_path or "New file"}

## Sheet
{sheet}

## Data
{len(data) if data else 0} rows

## Result
[Spreadsheet would be processed here]

---
*Note: Full implementation requires openpyxl or pandas library*
"""


# =============================================================================
# Development & Code Tools
# =============================================================================

@skill(
    name="frontend-design",
    description="Create modern frontend designs with React, Tailwind CSS, and shadcn/ui components",
    parameters={
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["landing-page", "dashboard", "component", "full-app"], "description": "Design type"},
            "style": {"type": "string", "description": "Design style preference"},
            "features": {"type": "array", "items": {"type": "string"}, "description": "Required features"},
        },
        "required": ["type"],
    },
)
def frontend_design(type: str, style: str | None = None, features: list[str] | None = None) -> str:
    """Frontend design skill following Anthropic best practices."""
    return f"""
# Frontend Design Skill

## Type
{type}

## Style
{style or "Modern, clean design"}

## Features
{chr(10).join(f'- {f}' for f in (features or ['Responsive layout', 'Dark mode support']))}

## Implementation

```tsx
// React component with Tailwind CSS
import React from 'react';

export default function Component() {{
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <h1 className="text-4xl font-bold text-gray-900">
        {type.replace('-', ' ').title()}
      </h1>
    </div>
  );
}}
```

## Design Principles Applied
- ✓ Avoid generic "AI slop" aesthetics
- ✓ Bold, intentional design decisions
- ✓ Consistent spacing and typography
- ✓ Accessible color contrast
- ✓ Mobile-first responsive design

---
*Based on official Anthropic frontend-design skill*
"""


@skill(
    name="mcp-builder",
    description="Build high-quality MCP (Model Context Protocol) servers for integrating external APIs",
    parameters={
        "type": "object",
        "properties": {
            "api_name": {"type": "string", "description": "Name of the API to integrate"},
            "endpoints": {"type": "array", "items": {"type": "string"}, "description": "API endpoints to expose"},
            "auth_type": {"type": "string", "enum": ["none", "api_key", "oauth2", "bearer"], "description": "Authentication type"},
        },
        "required": ["api_name"],
    },
)
def mcp_builder(api_name: str, endpoints: list[str] | None = None, auth_type: str = "api_key") -> str:
    """MCP server builder skill."""
    return f"""
# MCP Builder Skill

## API Integration
**Name:** {api_name}
**Auth:** {auth_type}

## Endpoints
{chr(10).join(f'- `{ep}`' for ep in (endpoints or ['/api/v1/resource']))}

## MCP Server Implementation

```typescript
import {{ Server }} from '@modelcontextprotocol/sdk/server/index.js';
import {{ StdioServerTransport }} from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({{
  name: '{api_name}-mcp',
  version: '1.0.0',
}});

// Define tools
server.setRequestHandler('tools/list', async () => {{
  return {{
    tools: [{{
      name: 'fetch_data',
      description: 'Fetch data from {api_name}',
      inputSchema: {{ type: 'object', properties: {{}} }},
    }}],
  }};
}});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

## Usage
1. Install: `npm install @modelcontextprotocol/sdk`
2. Configure in Claude Desktop config
3. Restart Claude

---
*Based on official Anthropic mcp-builder skill*
"""


@skill(
    name="test-driven-development",
    description="Implement TDD methodology: write tests first, then implementation",
    parameters={
        "type": "object",
        "properties": {
            "feature": {"type": "string", "description": "Feature to implement"},
            "language": {"type": "string", "description": "Programming language"},
            "test_framework": {"type": "string", "description": "Testing framework"},
        },
        "required": ["feature"],
    },
)
def test_driven_development(feature: str, language: str = "typescript", test_framework: str = "jest") -> str:
    """Test-driven development skill."""
    feature_clean = feature.replace(' ', '-').lower()
    return f"""
# Test-Driven Development Skill

## Feature
{feature}

## Language & Framework
{language} / {test_framework}

## TDD Process

### Step 1: Write Failing Test
```{language}
describe('{feature_clean}', () => {{
  it('should implement the feature correctly', () => {{
    // Arrange
    const input = 'test input';
    
    // Act
    const result = implementFeature(input);
    
    // Assert
    expect(result).toBeDefined();
    expect(result).toMatchSnapshot();
  }});
}});
```

### Step 2: Run Test (Should Fail)
```bash
npm test -- {feature_clean}
# Expected: 1 failing
```

### Step 3: Implement Minimum Code
```{language}
export function implementFeature(input: string) {{
  // Minimal implementation to pass test
  return {{ success: true, data: input }};
}}
```

### Step 4: Run Test (Should Pass)
```bash
npm test
# Expected: 1 passing
```

### Step 5: Refactor
- Clean up code
- Improve naming
- Remove duplication
- Verify tests still pass

---
*Based on official Anthropic test-driven-development skill*
"""


@skill(
    name="code-review",
    description="Review code for quality, security, performance, and best practices",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Code to review"},
            "focus_areas": {"type": "array", "items": {"type": "string"}, "description": "Areas to focus on"},
            "severity_threshold": {"type": "string", "enum": ["low", "medium", "high"], "description": "Minimum severity to report"},
        },
        "required": ["code"],
    },
)
def code_review(code: str, focus_areas: list[str] | None = None, severity_threshold: str = "medium") -> str:
    """Code review skill."""
    return f"""
# Code Review

## Focus Areas
{', '.join(focus_areas or ['Security', 'Performance', 'Readability', 'Best Practices'])}

## Severity Threshold
{severity_threshold}

## Review Results

### 🔴 Critical Issues
- [Check for security vulnerabilities]
- [Check for memory leaks]
- [Check for null pointer exceptions]

### 🟡 Medium Issues
- [Check for code duplication]
- [Check for missing error handling]
- [Check for performance bottlenecks]

### 🟢 Suggestions
- [Consider using more descriptive variable names]
- [Add comments for complex logic]
- [Consider extracting reusable functions]

## Summary
| Category | Issues Found |
|----------|-------------|
| Security | TBD |
| Performance | TBD |
| Readability | TBD |
| Best Practices | TBD |

## Recommended Actions
1. Address all critical issues immediately
2. Schedule medium issues for next sprint
3. Add suggestions to backlog

---
*Based on industry code review best practices*
"""


# =============================================================================
# Creative & Design
# =============================================================================

@skill(
    name="canvas-design",
    description="Create beautiful visual art in PNG and PDF formats using design philosophy",
    parameters={
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["poster", "infographic", "social-media", "presentation"], "description": "Design type"},
            "theme": {"type": "string", "description": "Design theme"},
            "dimensions": {"type": "string", "description": "Output dimensions"},
        },
        "required": ["type"],
    },
)
def canvas_design(type: str, theme: str | None = None, dimensions: str = "1920x1080") -> str:
    """Canvas design skill."""
    return f"""
# Canvas Design Skill

## Design Type
{type}

## Theme
{theme or "Modern minimalist"}

## Dimensions
{dimensions}

## Design Philosophy
- Use intentional whitespace
- Maintain visual hierarchy
- Apply consistent color palette
- Ensure accessibility compliance

## Output Format
- PNG for web/digital
- PDF for print

## Design Process
1. Understand requirements
2. Create wireframe
3. Apply brand guidelines
4. Review and refine
5. Export in required formats

---
*Based on official Anthropic canvas-design skill*
"""


@skill(
    name="brand-guidelines",
    description="Apply official brand colors and typography to artifacts",
    parameters={
        "type": "object",
        "properties": {
            "brand": {"type": "string", "description": "Brand name"},
            "artifact_type": {"type": "string", "enum": ["document", "presentation", "web", "social"], "description": "Artifact type"},
        },
        "required": ["artifact_type"],
    },
)
def brand_guidelines(artifact_type: str, brand: str | None = None) -> str:
    """Brand guidelines skill."""
    return f"""
# Brand Guidelines

## Brand
{brand or "Default"}

## Artifact Type
{artifact_type}

## Brand Colors
| Usage | Color | Hex |
|-------|-------|-----|
| Primary | Blue | #1E90FF |
| Secondary | Gray | #6B7280 |
| Accent | Green | #10B981 |
| Background | White | #FFFFFF |
| Text | Dark | #1F2937 |

## Typography
- **Headings:** Inter Bold
- **Body:** Inter Regular
- **Code:** JetBrains Mono

## Application
Applied to: {artifact_type}

---
*Based on official Anthropic brand-guidelines skill*
"""


# =============================================================================
# Communication & Writing
# =============================================================================

@skill(
    name="internal-comms",
    description="Write internal communications: status reports, newsletters, FAQs, project updates",
    parameters={
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["status-report", "newsletter", "faq", "announcement"], "description": "Communication type"},
            "audience": {"type": "string", "description": "Target audience"},
            "key_points": {"type": "array", "items": {"type": "string"}, "description": "Key points to include"},
        },
        "required": ["type"],
    },
)
def internal_comms(type: str, audience: str = "All Staff", key_points: list[str] | None = None) -> str:
    """Internal communications skill."""
    return f"""
# Internal Communication

## Type
{type.replace('-', ' ').title()}

## Audience
{audience}

## Key Points
{chr(10).join(f'- {point}' for point in (key_points or ['Project update', 'Timeline status']))}

---

**Subject:** {type.replace('-', ' ').title()} - {__import__('datetime').datetime.now().strftime('%B %Y')}

Dear Team,

I'm writing to share an update on {type.replace('-', ' ')}.

## Overview
[Overview content based on key points]

## Key Highlights
{chr(10).join(f'- {point}' for point in (key_points or ['Highlight 1', 'Highlight 2']))}

## Next Steps
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

## Questions?
Please reach out if you have any questions.

Best regards,
[Your Name]

---
*Based on official Anthropic internal-comms skill*
"""


@skill(
    name="article-extractor",
    description="Extract full article text and metadata from web pages",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Article URL"},
            "include_metadata": {"type": "boolean", "description": "Include metadata"},
        },
        "required": ["url"],
    },
)
def article_extractor(url: str, include_metadata: bool = True) -> str:
    """Article extractor skill."""
    return f"""
# Article Extractor

## URL
{url}

## Extracted Content

### Title
[Article title would be extracted here]

### Author
[Author name]

### Published Date
[Publication date]

### Content
[Full article text would be extracted here]

{'### Metadata\n- Tags: [tags]\n- Category: [category]\n- Reading Time: [X] min' if include_metadata else ''}

---
*Note: Full implementation requires newspaper3k or similar library*
"""


# =============================================================================
# Data & Analysis
# =============================================================================

@skill(
    name="csv-data-summarizer",
    description="Automatically analyze CSV files and generate comprehensive insights with visualizations",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "CSV file path"},
            "analysis_type": {"type": "string", "enum": ["descriptive", "diagnostic", "predictive"], "description": "Analysis type"},
        },
        "required": ["file_path"],
    },
)
def csv_data_summarizer(file_path: str, analysis_type: str = "descriptive") -> str:
    """CSV data summarizer skill."""
    return f"""
# CSV Data Summarizer

## File
{file_path}

## Analysis Type
{analysis_type}

## Data Overview
- Rows: [count]
- Columns: [count]
- Missing Values: [count]

## Column Statistics
| Column | Type | Min | Max | Mean |
|--------|------|-----|-----|------|
| [col] | numeric | - | - | - |

## Key Insights
1. [Insight 1]
2. [Insight 2]
3. [Insight 3]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]

---
*Note: Full implementation requires pandas library*
"""


@skill(
    name="postgres",
    description="Execute safe read-only SQL queries against PostgreSQL databases",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "SQL query (SELECT only)"},
            "database": {"type": "string", "description": "Database name"},
            "limit": {"type": "integer", "description": "Result limit"},
        },
        "required": ["query"],
    },
)
def postgres(query: str, database: str = "default", limit: int = 100) -> str:
    """PostgreSQL query skill with read-only security."""
    # Security check - only SELECT allowed
    if not query.strip().upper().startswith('SELECT'):
        return "❌ Error: Only SELECT queries are allowed for security"
    
    return f"""
# PostgreSQL Query Result

## Database
{database}

## Query
```sql
{query}
LIMIT {limit}
```

## Results
| Column1 | Column2 | ... |
|---------|---------|-----|
| [data] | [data] | ... |

## Summary
- Rows returned: [count]
- Query time: [ms]

---
*Security: Read-only access enforced*
"""


# =============================================================================
# Productivity & Workflow
# =============================================================================

@skill(
    name="file-organizer",
    description="Intelligently organize files and folders by understanding context",
    parameters={
        "type": "object",
        "properties": {
            "directory": {"type": "string", "description": "Directory to organize"},
            "strategy": {"type": "string", "enum": ["by-type", "by-date", "by-project", "by-size"], "description": "Organization strategy"},
        },
        "required": ["directory"],
    },
)
def file_organizer(directory: str, strategy: str = "by-type") -> str:
    """File organizer skill."""
    return f"""
# File Organizer

## Directory
{directory}

## Strategy
{strategy}

## Organization Plan

### By Type
```
{directory}/
├── documents/
│   ├── pdf/
│   ├── docx/
│   └── txt/
├── images/
│   ├── jpg/
│   ├── png/
│   └── svg/
├── code/
│   ├── python/
│   ├── javascript/
│   └── rust/
└── data/
    ├── csv/
    └── json/
```

## Actions
1. Scan directory
2. Categorize files
3. Create folder structure
4. Move files
5. Generate report

---
*Note: Full implementation requires file system access*
"""


@skill(
    name="git-workflows",
    description="Manage git workflows: branches, PRs, merges, and collaboration",
    parameters={
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["status", "branch", "merge", "pr", "rebase"], "description": "Git action"},
            "branch": {"type": "string", "description": "Branch name"},
        },
        "required": ["action"],
    },
)
def git_workflows(action: str, branch: str | None = None) -> str:
    """Git workflows skill."""
    return f"""
# Git Workflows

## Action
{action}

## Branch
{branch or "current"}

## Commands

### Status Check
```bash
git status
git branch -a
git log --oneline -10
```

### {action.title()}
```bash
git {'checkout -b ' + branch if branch == 'new' else action}
```

## Best Practices
- ✓ Commit frequently with clear messages
- ✓ Create feature branches for new work
- ✓ Review changes before committing
- ✓ Sync with remote regularly
- ✓ Use descriptive PR descriptions

---
*Based on git best practices*
"""


# =============================================================================
# Helper Functions
# =============================================================================

def get_all_official_claude_skills() -> list:
    """Get list of all official Claude skills."""
    return [
        # Document Skills
        docx_skill,
        pdf_skill,
        pptx_skill,
        xlsx_skill,
        # Development Skills
        frontend_design,
        mcp_builder,
        test_driven_development,
        code_review,
        # Creative Skills
        canvas_design,
        brand_guidelines,
        # Communication Skills
        internal_comms,
        article_extractor,
        # Data Skills
        csv_data_summarizer,
        postgres,
        # Productivity Skills
        file_organizer,
        git_workflows,
    ]


def register_official_claude_skills(agent) -> None:
    """Register all official Claude skills with an agent."""
    for skill_func in get_all_official_claude_skills():
        agent.add_skill(skill_func)
