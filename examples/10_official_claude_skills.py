#!/usr/bin/env python3
"""Official Claude Skills Demo.

Demonstrates authentic Claude Skills based on the official Anthropic repository.

Usage:
    python examples/10_official_claude_skills.py
"""

from piranha import Agent
from piranha.official_claude_skills import (
    get_all_official_claude_skills,
)


def main():
    print("=" * 70)
    print("OFFICIAL CLAUDE SKILLS DEMO")
    print("=" * 70)
    print()
    print("Based on: https://github.com/anthropics/skills")
    print("          https://github.com/ComposioHQ/awesome-claude-skills")
    print()

    # Create agent with official Claude skills
    agent = Agent(
        name="claude_official",
        model="ollama/llama3:latest",
        description="AI assistant with official Claude Skills",
        skills=get_all_official_claude_skills(),
    )

    print(f"Created agent: {agent.name}")
    print(f"Official skills registered: {len(agent.skills)}")
    print()

    # =========================================================================
    # Demo 1: Document Skills
    # =========================================================================
    print("-" * 70)
    print("Demo 1: Document Skills (Official Anthropic)")
    print("-" * 70)
    print()

    print("DOCX Skill:")
    result = docx_skill(action="create", content="Sample document content")
    print(result[:500])
    print()

    print("PDF Skill:")
    result = pdf_skill(action="extract", file_path="/path/to/document.pdf")
    print(result[:500])
    print()

    print("XLSX Skill:")
    result = xlsx_skill(action="analyze", file_path="/path/to/data.xlsx")
    print(result[:500])
    print()

    # =========================================================================
    # Demo 2: Development Skills
    # =========================================================================
    print("-" * 70)
    print("Demo 2: Development Skills")
    print("-" * 70)
    print()

    print("Frontend Design Skill:")
    result = frontend_design(
        type="landing-page",
        style="Modern SaaS",
        features=["Hero section", "Features grid", "CTA buttons"]
    )
    print(result[:800])
    print()

    print("MCP Builder Skill:")
    result = mcp_builder(
        api_name="Stripe",
        endpoints=["/v1/charges", "/v1/customers", "/v1/products"],
        auth_type="api_key"
    )
    print(result[:800])
    print()

    print("Test-Driven Development Skill:")
    result = test_driven_development(
        feature="User authentication",
        language="typescript",
        test_framework="jest"
    )
    print(result[:800])
    print()

    # =========================================================================
    # Demo 3: Creative Skills
    # =========================================================================
    print("-" * 70)
    print("Demo 3: Creative Skills")
    print("-" * 70)
    print()

    print("Canvas Design Skill:")
    result = canvas_design(
        type="poster",
        theme="Tech Conference 2025",
        dimensions="1920x1080"
    )
    print(result[:500])
    print()

    print("Brand Guidelines Skill:")
    result = brand_guidelines(
        artifact_type="presentation",
        brand="Anthropic"
    )
    print(result[:500])
    print()

    # =========================================================================
    # Demo 4: Communication Skills
    # =========================================================================
    print("-" * 70)
    print("Demo 4: Communication Skills")
    print("-" * 70)
    print()

    print("Internal Comms Skill:")
    result = internal_comms(
        type="status-report",
        audience="Engineering Team",
        key_points=[
            "Sprint completed successfully",
            "New features deployed",
            "Performance improvements"
        ]
    )
    print(result[:800])
    print()

    print("Article Extractor Skill:")
    result = article_extractor(
        url="https://example.com/article",
        include_metadata=True
    )
    print(result[:500])
    print()

    # =========================================================================
    # Demo 5: Data Skills
    # =========================================================================
    print("-" * 70)
    print("Demo 5: Data Skills")
    print("-" * 70)
    print()

    print("CSV Data Summarizer Skill:")
    result = csv_data_summarizer(
        file_path="/path/to/data.csv",
        analysis_type="descriptive"
    )
    print(result[:500])
    print()

    print("PostgreSQL Skill:")
    result = postgres(
        query="SELECT * FROM users WHERE active = true",
        database="production",
        limit=50
    )
    print(result[:500])
    print()

    # =========================================================================
    # Demo 6: Productivity Skills
    # =========================================================================
    print("-" * 70)
    print("Demo 6: Productivity Skills")
    print("-" * 70)
    print()

    print("File Organizer Skill:")
    result = file_organizer(
        directory="/Downloads",
        strategy="by-type"
    )
    print(result[:500])
    print()

    print("Git Workflows Skill:")
    result = git_workflows(
        action="branch",
        branch="feature/new-skill"
    )
    print(result[:500])
    print()

    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 70)
    print("OFFICIAL CLAUDE SKILLS DEMO COMPLETE!")
    print("=" * 70)
    print()
    print("Skills Demonstrated:")
    print()
    print("📄 Document Skills (Official Anthropic):")
    print("  ✓ docx - Word document processing")
    print("  ✓ pdf - PDF manipulation")
    print("  ✓ pptx - PowerPoint presentations")
    print("  ✓ xlsx - Excel spreadsheets")
    print()
    print("💻 Development Skills:")
    print("  ✓ frontend-design - React/Tailwind/shadcn/ui")
    print("  ✓ mcp-builder - MCP server creation")
    print("  ✓ test-driven-development - TDD methodology")
    print("  ✓ code-review - Code quality review")
    print()
    print("🎨 Creative Skills:")
    print("  ✓ canvas-design - Visual art creation")
    print("  ✓ brand-guidelines - Brand application")
    print()
    print("✍️ Communication Skills:")
    print("  ✓ internal-comms - Internal communications")
    print("  ✓ article-extractor - Web article extraction")
    print()
    print("📊 Data Skills:")
    print("  ✓ csv-data-summarizer - CSV analysis")
    print("  ✓ postgres - PostgreSQL queries")
    print()
    print("📁 Productivity Skills:")
    print("  ✓ file-organizer - File organization")
    print("  ✓ git-workflows - Git management")
    print()
    print("Usage:")
    print("  from piranha.official_claude_skills import register_official_claude_skills")
    print("  register_official_claude_skills(agent)")
    print()
    print("References:")
    print("  - https://github.com/anthropics/skills")
    print("  - https://github.com/ComposioHQ/awesome-claude-skills")
    print()


if __name__ == "__main__":
    main()
