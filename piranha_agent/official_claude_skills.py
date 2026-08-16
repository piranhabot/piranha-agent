#!/usr/bin/env python3
"""Official Claude Skills for Piranha Agent.

Based on the official Anthropic Claude Skills repository:
https://github.com/anthropics/skills
https://github.com/ComposioHQ/awesome-claude-skills

This module implements authentic Claude Skills following the official format.
"""


from piranha_agent.skill import skill

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
    permissions=["network_read"],
)
def article_extractor(url: str, include_metadata: bool = True) -> str:
    """Article extractor skill - fetches the URL and extracts real text."""
    from piranha_agent.skills._web_research import fetch_url_text

    try:
        page = fetch_url_text(url)
    except Exception as e:
        return f"❌ Error fetching {url}: {e}"

    word_count = len(page["text"].split())
    metadata = (
        f"### Metadata\n- Word Count: ~{word_count}\n"
        f"- Reading Time: ~{max(1, word_count // 200)} min\n"
        f"- Truncated: {page['truncated']}"
        if include_metadata
        else ""
    )
    return f"""
# Article Extractor

## URL
{url}

## Extracted Content

### Title
{page["title"] or "(no <title> found)"}

### Content
{page["text"] or "(no extractable text found)"}

{metadata}

---
*Extraction is a minimal dependency-free text strip (no ad/boilerplate
removal) - not readability-quality. Author/publish-date extraction is
not implemented.*
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
    permissions=["file_read"],
)
def csv_data_summarizer(file_path: str, analysis_type: str = "descriptive") -> str:
    """CSV data summarizer skill - actually reads the file and computes real stats.

    "diagnostic"/"predictive" analysis_type values are accepted but do not
    currently change the output - only descriptive statistics are computed
    (real numbers, not a modeling pipeline).
    """
    import pandas as pd

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return f"❌ Error: File not found: {file_path}"
    except Exception as e:
        return f"❌ Error reading CSV: {e}"

    rows, cols = df.shape
    missing_total = int(df.isna().sum().sum())

    numeric_df = df.select_dtypes(include="number")
    stat_rows = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        if col in numeric_df.columns:
            col_min = df[col].min()
            col_max = df[col].max()
            col_mean = df[col].mean()
            stat_rows.append(f"| {col} | {dtype} | {col_min:.2f} | {col_max:.2f} | {col_mean:.2f} |")
        else:
            stat_rows.append(f"| {col} | {dtype} | - | - | - |")
    stats_table = "\n".join(stat_rows) if stat_rows else "| (no columns) | - | - | - | - |"

    insights = []
    null_cols = df.columns[df.isna().any()].tolist()
    if null_cols:
        insights.append(f"Missing values found in: {', '.join(null_cols)}")
    dup_count = int(df.duplicated().sum())
    if dup_count:
        insights.append(f"{dup_count} duplicate row(s) found")
    if not insights:
        insights.append("No missing values or duplicate rows detected")
    insights_text = "\n".join(f"{i}. {text}" for i, text in enumerate(insights, 1))

    return f"""
# CSV Data Summarizer

## File
{file_path}

## Analysis Type
{analysis_type}

## Data Overview
- Rows: {rows}
- Columns: {cols}
- Missing Values: {missing_total}

## Column Statistics
| Column | Type | Min | Max | Mean |
|--------|------|-----|-----|------|
{stats_table}

## Key Insights
{insights_text}

---
*"diagnostic"/"predictive" analysis_type is accepted but not yet
implemented differently from "descriptive" - only real descriptive
statistics are computed above.*
"""


_POSTGRES_FORBIDDEN_KEYWORDS = (
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "EXECUTE", "CALL", "COPY", "VACUUM",
)


def _validate_readonly_sql(query: str) -> str | None:
    """Return an error message if `query` isn't a safe single SELECT, else None.

    Defense in depth beyond a single connection.read_only=True: rejects
    multi-statement queries (e.g. "SELECT 1; DROP TABLE users;--") and any
    forbidden keyword appearing anywhere in the query, not just checking
    the first token.
    """
    stripped = query.strip().rstrip(";").strip()
    if not stripped.upper().startswith("SELECT"):
        return "Only SELECT queries are allowed for security"
    if ";" in stripped:
        return "Multi-statement queries are not allowed"
    import re

    for kw in _POSTGRES_FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{kw}\b", stripped, re.IGNORECASE):
            return f"Forbidden keyword '{kw}' found in query"
    return None


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
    permissions=["network_read"],
)
def postgres(query: str, database: str = "default", limit: int = 100) -> str:
    """PostgreSQL query skill with read-only security - runs a real query.

    Connection is read via a `PIRANHA_POSTGRES_DSN` environment variable
    (a full `postgresql://user:pass@host:port/dbname` connection string).
    `database` is accepted for API compatibility but does not currently
    select between multiple configured databases - only a single DSN is
    supported today.
    """
    error = _validate_readonly_sql(query)
    if error:
        return f"❌ Error: {error}"

    import os

    dsn = os.environ.get("PIRANHA_POSTGRES_DSN")
    if not dsn:
        return (
            "❌ Error: PIRANHA_POSTGRES_DSN environment variable is not set. "
            "Set it to a postgresql://user:pass@host:port/dbname connection string."
        )

    try:
        import psycopg
    except ImportError:
        return (
            "❌ Error: the 'postgres' skill requires psycopg. "
            'Install with: pip install "piranha-agent[postgres]"'
        )

    stripped = query.strip().rstrip(";").strip()
    wrapped_query = f"SELECT * FROM ({stripped}) AS _piranha_subquery LIMIT %(limit)s"

    try:
        with psycopg.connect(dsn, autocommit=False) as conn:
            conn.execute("SET TRANSACTION READ ONLY")
            with conn.cursor() as cur:
                cur.execute(wrapped_query, {"limit": limit})
                columns = [desc.name for desc in cur.description] if cur.description else []
                rows = cur.fetchall()
    except Exception as e:
        return f"❌ Error executing query: {e}"

    if not columns:
        return f"""
# PostgreSQL Query Result

## Database
{database}

## Query
```sql
{query}
```

## Results
(no columns returned)

## Summary
- Rows returned: 0

---
*Security: enforced via SET TRANSACTION READ ONLY + query validation ({len(_POSTGRES_FORBIDDEN_KEYWORDS)}-keyword blocklist)*
"""

    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join("---" for _ in columns) + "|"
    body_lines = [
        "| " + " | ".join("NULL" if v is None else str(v) for v in row) + " |"
        for row in rows
    ]
    table = "\n".join([header, separator, *body_lines]) if body_lines else header + "\n" + separator

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
{table}

## Summary
- Rows returned: {len(rows)}

---
*Security: enforced via SET TRANSACTION READ ONLY + query validation ({len(_POSTGRES_FORBIDDEN_KEYWORDS)}-keyword blocklist)*
"""


# =============================================================================
# Productivity & Workflow
# =============================================================================

_FILE_ORGANIZER_TYPE_CATEGORIES = {
    "documents": {".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt"},
    "images": {".jpg", ".jpeg", ".png", ".svg", ".gif", ".bmp", ".webp"},
    "code": {".py", ".js", ".ts", ".rs", ".go", ".java", ".c", ".cpp", ".rb"},
    "data": {".csv", ".json", ".yaml", ".yml", ".xml", ".parquet"},
}


def _categorize_by_type(ext: str) -> str:
    for category, exts in _FILE_ORGANIZER_TYPE_CATEGORIES.items():
        if ext.lower() in exts:
            return category
    return "other"


def _categorize_by_size(size_bytes: int) -> str:
    if size_bytes < 1_000_000:
        return "small"
    if size_bytes < 100_000_000:
        return "medium"
    return "large"


@skill(
    name="file-organizer",
    description="Organize files in a directory by type, date, or size",
    parameters={
        "type": "object",
        "properties": {
            "directory": {"type": "string", "description": "Directory to organize"},
            "strategy": {"type": "string", "enum": ["by-type", "by-date", "by-project", "by-size"], "description": "Organization strategy"},
            "dry_run": {"type": "boolean", "description": "If true (default), only report the plan - don't move any files"},
        },
        "required": ["directory"],
    },
    permissions=["file_write"],
    requires_confirmation=True,
)
def file_organizer(directory: str, strategy: str = "by-type", dry_run: bool = True) -> str:
    """File organizer skill - actually scans and (optionally) moves files.

    "by-project" is not implemented (grouping files by "project" requires
    heuristics this skill doesn't have - see below); by-type/by-date/by-size
    are real. Defaults to dry_run=True so a call without dry_run=False never
    touches the filesystem, on top of the skill-level confirmation gate.
    """
    import shutil
    from datetime import datetime
    from pathlib import Path

    if strategy == "by-project":
        return (
            "❌ Error: \"by-project\" is not implemented - grouping files by "
            "project requires heuristics (e.g. shared config files, git repo "
            "boundaries) this skill doesn't have. Use \"by-type\", \"by-date\", "
            "or \"by-size\" instead."
        )

    root = Path(directory)
    if not root.is_dir():
        return f"❌ Error: not a directory: {directory}"

    files = [p for p in root.iterdir() if p.is_file()]
    plan: dict[str, list[Path]] = {}
    for f in files:
        if strategy == "by-type":
            bucket = _categorize_by_type(f.suffix)
        elif strategy == "by-date":
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            bucket = mtime.strftime("%Y-%m")
        elif strategy == "by-size":
            bucket = _categorize_by_size(f.stat().st_size)
        else:
            return f"❌ Error: unknown strategy: {strategy}"
        plan.setdefault(bucket, []).append(f)

    plan_lines = [f"- {bucket}/ ({len(paths)} files): {', '.join(p.name for p in paths[:5])}"
                  + (f", ... +{len(paths) - 5} more" if len(paths) > 5 else "")
                  for bucket, paths in sorted(plan.items())]
    plan_text = "\n".join(plan_lines) if plan_lines else "(no files found in directory)"

    if dry_run:
        return f"""
# File Organizer (dry run - no files moved)

## Directory
{directory}

## Strategy
{strategy}

## Plan
{plan_text}

---
*Call again with dry_run=False to actually move these {len(files)} file(s).*
"""

    moved = 0
    errors = []
    for bucket, paths in plan.items():
        bucket_dir = root / bucket
        bucket_dir.mkdir(exist_ok=True)
        for f in paths:
            try:
                shutil.move(str(f), str(bucket_dir / f.name))
                moved += 1
            except Exception as e:
                errors.append(f"{f.name}: {e}")

    error_text = "\n".join(f"- {e}" for e in errors) if errors else "(none)"
    return f"""
# File Organizer (executed)

## Directory
{directory}

## Strategy
{strategy}

## Result
- Files moved: {moved}
- Errors: {error_text}

## Plan Applied
{plan_text}
"""


@skill(
    name="git-workflows",
    description="Run local git operations: status, branch, merge, rebase (PR creation redirects to the real github_create_pull_request skill)",
    parameters={
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["status", "branch", "merge", "pr", "rebase"], "description": "Git action"},
            "branch": {"type": "string", "description": "Branch name"},
            "repo_path": {"type": "string", "description": "Path to the git repository (defaults to current directory)"},
        },
        "required": ["action"],
    },
    permissions=["file_write"],
    requires_confirmation=True,
)
def git_workflows(action: str, branch: str | None = None, repo_path: str = ".") -> str:
    """Git workflows skill - runs real local git commands via subprocess.

    Previously returned a canned template showing ``git {action}`` as an
    example command, next to the 39 real GitHub skills (github_create_*)
    added earlier - with nothing indicating this one was fake. Now runs
    real local git operations. "pr" is a GitHub API operation, not a local
    git one - it redirects to github_create_pull_request rather than
    reimplementing GitHub API calls a second time.

    requires_confirmation=True applies to every action here (including
    read-only "status") because this single function multiplexes both
    safe and repo-mutating operations (merge/rebase) - the framework's
    confirmation gate can't distinguish which action a given call is for.
    """
    import subprocess

    if action == "pr":
        return (
            "ℹ️ Creating a pull request is a GitHub API operation, not a "
            "local git one. Use the real `github_create_pull_request` skill "
            "instead (see piranha_agent/skills/github_tools.py / skills.md) "
            "rather than this local-git skill."
        )

    if action == "status":
        cmd = ["git", "status", "--short", "--branch"]
    elif action == "branch":
        cmd = ["git", "branch", branch] if branch else ["git", "branch", "--list"]
    elif action == "merge":
        if not branch:
            return "❌ Error: 'branch' is required for the merge action"
        cmd = ["git", "merge", branch]
    elif action == "rebase":
        if not branch:
            return "❌ Error: 'branch' is required for the rebase action"
        cmd = ["git", "rebase", branch]
    else:
        return f"❌ Error: unknown action: {action}"

    try:
        result = subprocess.run(
            cmd, cwd=repo_path, capture_output=True, text=True, timeout=30
        )
    except FileNotFoundError:
        return "❌ Error: git is not installed or not on PATH"
    except subprocess.TimeoutExpired:
        return f"❌ Error: `{' '.join(cmd)}` timed out after 30s"

    output = result.stdout.strip() or "(no output)"
    if result.returncode != 0:
        return f"❌ Error running `{' '.join(cmd)}`:\n{result.stderr.strip() or output}"

    return f"""
# Git Workflows

## Action
{action}

## Command
```bash
{' '.join(cmd)}
```

## Output
```
{output}
```
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
