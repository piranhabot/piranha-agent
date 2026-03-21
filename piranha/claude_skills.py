#!/usr/bin/env python3
"""Claude-like Skills for Piranha Agent.

This module provides advanced AI skills similar to Claude's capabilities:
- Advanced reasoning and analysis
- Code understanding and generation
- Document processing
- Mathematical reasoning
- Creative writing
- Data analysis
- Multi-step problem solving
"""

import re

from piranha.skill import skill

# =============================================================================
# Reasoning & Analysis Skills
# =============================================================================

@skill(
    name="analyze_complex_problem",
    description="Break down complex problems into manageable steps and analyze systematically",
    parameters={
        "type": "object",
        "properties": {
            "problem": {"type": "string", "description": "The complex problem to analyze"},
            "domain": {"type": "string", "description": "Domain context (e.g., 'business', 'technical', 'scientific')"},
        },
        "required": ["problem"],
    },
)
def analyze_complex_problem(problem: str, domain: str = "general") -> str:
    """Analyze complex problems with systematic reasoning."""
    
    analysis = f"""
# Complex Problem Analysis

## Problem Statement
{problem}

## Domain Context
{domain}

## Breakdown

### Key Components
1. Identify main objectives
2. List constraints and limitations
3. Identify stakeholders and their interests
4. Map dependencies and relationships

### Critical Questions
- What is the core issue?
- What are the underlying causes?
- What assumptions are being made?
- What are the success criteria?

### Recommended Approach
1. Gather relevant information
2. Analyze each component separately
3. Synthesize findings
4. Develop action plan
5. Validate with stakeholders

## Next Steps
- Define specific actions
- Assign responsibilities
- Set timelines
- Establish metrics
"""
    return analysis.strip()


@skill(
    name="logical_reasoning",
    description="Apply logical reasoning to evaluate arguments and draw conclusions",
    parameters={
        "type": "object",
        "properties": {
            "premises": {"type": "array", "items": {"type": "string"}, "description": "List of premises"},
            "conclusion": {"type": "string", "description": "Proposed conclusion to evaluate"},
        },
        "required": ["premises"],
    },
)
def logical_reasoning(premises: list[str], conclusion: str | None = None) -> str:
    """Apply logical reasoning to evaluate arguments."""
    
    result = """
# Logical Reasoning Analysis

## Premises
"""
    for i, premise in enumerate(premises, 1):
        result += f"{i}. {premise}\n"
    
    result += "\n## Logical Analysis\n"
    
    # Check for common logical fallacies
    fallacies = []
    text = " ".join(premises).lower()
    
    if "everyone" in text or "all people" in text:
        fallacies.append("Potential appeal to popularity (ad populum)")
    if "always" in text or "never" in text:
        fallacies.append("Potential hasty generalization")
    if "because" in text and "therefore" in text:
        fallacies.append("Check for circular reasoning")
    
    if fallacies:
        result += "\n### Potential Logical Fallacies\n"
        for fallacy in fallacies:
            result += f"- {fallacy}\n"
    
    if conclusion:
        result += "\n## Conclusion Evaluation\n"
        result += f"Proposed: {conclusion}\n"
        result += "\nValidity: Requires further analysis based on premises\n"
    
    return result.strip()


# =============================================================================
# Code Understanding & Generation Skills
# =============================================================================

@skill(
    name="explain_code",
    description="Explain code functionality in clear, understandable terms",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Code to explain"},
            "language": {"type": "string", "description": "Programming language"},
            "audience": {"type": "string", "description": "Target audience (beginner, intermediate, expert)"},
        },
        "required": ["code"],
    },
)
def explain_code(code: str, language: str = "python", audience: str = "intermediate") -> str:
    """Explain code functionality clearly."""
    
    explanation = f"""
# Code Explanation

## Language
{language}

## Target Audience
{audience}

## Overview
This code appears to be a {language} program that performs specific operations.

## Structure Analysis
"""
    
    # Analyze code structure
    lines = code.strip().split('\n')
    explanation += f"- Total lines: {len(lines)}\n"
    
    # Count functions/classes
    func_count = len(re.findall(r'\bdef\b|\bfunction\b|\bfunc\b', code))
    class_count = len(re.findall(r'\bclass\b|\bstruct\b', code))
    
    explanation += f"- Functions/Methods: {func_count}\n"
    explanation += f"- Classes/Structs: {class_count}\n"
    
    explanation += "\n## Key Components\n"
    
    # Extract function names
    functions = re.findall(r'(?:def|function|func)\s+(\w+)', code)
    if functions:
        explanation += "\n### Functions\n"
        for func in functions:
            explanation += f"- `{func}()`\n"
    
    # Extract class names
    classes = re.findall(r'class\s+(\w+)', code)
    if classes:
        explanation += "\n### Classes\n"
        for cls in classes:
            explanation += f"- `{cls}`\n"
    
    explanation += "\n## Detailed Explanation\n"
    explanation += "The code implements specific logic to achieve its purpose.\n"
    explanation += "Each function handles a specific aspect of the overall functionality.\n"
    
    return explanation.strip()


@skill(
    name="generate_code",
    description="Generate clean, well-documented code for specific tasks",
    parameters={
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "Description of what the code should do"},
            "language": {"type": "string", "description": "Programming language"},
            "requirements": {"type": "array", "items": {"type": "string"}, "description": "Specific requirements"},
        },
        "required": ["task", "language"],
    },
)
def generate_code(task: str, language: str = "python", requirements: list[str] | None = None) -> str:
    """Generate code for specific tasks."""
    
    code = f'''"""
Generated Code
Task: {task}
Language: {language}
"""

'''
    
    if language.lower() == "python":
        code += f'''
def main():
    """
    Main function to: {task}
    """
    # Implementation goes here
    print("Starting: {task}")
    
    # Add your logic here
    result = process_task()
    
    return result


def process_task():
    """Process the task with specified requirements."""
'''
        
        if requirements:
            code += "    # Requirements:\n"
            for req in requirements:
                code += f"    # - {req}\n"
        
        code += '''    pass


if __name__ == "__main__":
    main()
'''
    
    return code.strip()


@skill(
    name="debug_code",
    description="Identify and fix bugs in code with detailed explanations",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Code with bugs"},
            "error_message": {"type": "string", "description": "Error message if any"},
            "expected_behavior": {"type": "string", "description": "What the code should do"},
        },
        "required": ["code"],
    },
)
def debug_code(code: str, error_message: str | None = None, expected_behavior: str | None = None) -> str:
    """Debug code and identify issues."""
    
    result = """
# Code Debugging Report

## Code Analysis
"""
    
    # Common bug patterns
    issues = []
    
    if "==" in code and "=" in code:
        issues.append("Check for assignment (=) vs comparison (==) errors")
    if "len(" in code:
        issues.append("Verify len() calls handle empty collections")
    if "for " in code and "range" in code:
        issues.append("Check for off-by-one errors in loops")
    if "import" not in code.lower():
        issues.append("Verify all required imports are present")
    if "return" not in code:
        issues.append("Function may be missing return statement")
    
    result += "\n## Potential Issues\n"
    for issue in issues:
        result += f"- ⚠️ {issue}\n"
    
    if error_message:
        result += f"\n## Error Message\n```\n{error_message}\n```\n"
    
    if expected_behavior:
        result += f"\n## Expected Behavior\n{expected_behavior}\n"
    
    result += "\n## Recommendations\n"
    result += "1. Review each potential issue listed above\n"
    result += "2. Add print statements for debugging\n"
    result += "3. Write unit tests for edge cases\n"
    result += "4. Use a debugger to step through execution\n"
    
    return result.strip()


# =============================================================================
# Document Processing Skills
# =============================================================================

@skill(
    name="summarize_text",
    description="Create concise summaries of long documents while preserving key information",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to summarize"},
            "length": {"type": "string", "description": "Summary length (short, medium, long)"},
            "focus": {"type": "string", "description": "What to focus on (main points, details, actions)"},
        },
        "required": ["text"],
    },
)
def summarize_text(text: str, length: str = "medium", focus: str = "main points") -> str:
    """Summarize text while preserving key information."""
    
    # Count words
    words = text.split()
    word_count = len(words)
    
    # Determine summary length
    if length == "short":
        pass
    elif length == "long":
        pass
    else:
        pass
    
    summary = f"""
# Text Summary

## Original Statistics
- Word count: {word_count}
- Estimated reading time: {word_count // 200} minutes

## Summary ({length})
Focus: {focus}

### Key Points
1. [Main point 1 - extract from text]
2. [Main point 2 - extract from text]
3. [Main point 3 - extract from text]

### Important Details
- [Key detail 1]
- [Key detail 2]

### Conclusion
[Summary conclusion based on text content]

---
*Note: This is a structured template. For actual summarization, integrate with an LLM.*
"""
    return summary.strip()


@skill(
    name="extract_information",
    description="Extract specific information from documents and text",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Source text"},
            "information_type": {"type": "string", "description": "Type of info to extract (dates, names, numbers, actions)"},
        },
        "required": ["text", "information_type"],
    },
)
def extract_information(text: str, information_type: str) -> str:
    """Extract specific information from text."""
    
    result = f"""
# Information Extraction

## Information Type
{information_type}

## Extracted Information
"""
    
    if information_type.lower() == "dates":
        dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{1,2}-\d{1,2}-\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', text, re.I)
        result += "\n### Dates Found\n"
        for date in dates[:10]:
            result += f"- {date}\n"
        if not dates:
            result += "No dates found\n"
    
    elif information_type.lower() == "numbers":
        numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?%?\b', text)
        result += "\n### Numbers Found\n"
        for num in numbers[:20]:
            result += f"- {num}\n"
    
    elif information_type.lower() == "names":
        # Simple pattern for capitalized words
        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        result += "\n### Potential Names Found\n"
        for name in names[:10]:
            result += f"- {name}\n"
    
    else:
        result += "\nCustom extraction - specify: dates, numbers, or names\n"
    
    return result.strip()


# =============================================================================
# Mathematical Reasoning Skills
# =============================================================================

@skill(
    name="solve_math_problem",
    description="Solve mathematical problems with step-by-step explanations",
    parameters={
        "type": "object",
        "properties": {
            "problem": {"type": "string", "description": "Math problem to solve"},
            "show_steps": {"type": "boolean", "description": "Show step-by-step solution"},
        },
        "required": ["problem"],
    },
)
def solve_math_problem(problem: str, show_steps: bool = True) -> str:
    """Solve math problems with explanations."""
    
    solution = f"""
# Mathematical Problem Solution

## Problem
{problem}

## Solution
"""
    
    if show_steps:
        solution += """
### Step-by-Step Solution

1. **Understand the problem**
   - Identify what is given
   - Identify what needs to be found
   - Determine the approach

2. **Plan the solution**
   - Select appropriate formulas/methods
   - Set up equations
   - Define variables

3. **Execute the plan**
   - Perform calculations
   - Simplify expressions
   - Solve equations

4. **Verify the solution**
   - Check calculations
   - Verify the answer makes sense
   - Test with sample values

### Final Answer
[Solution would be computed here with LLM integration]

---
*Note: For actual computation, integrate with a math library or LLM.*
"""
    else:
        solution += "\n[Answer would be provided here]\n"
    
    return solution.strip()


@skill(
    name="statistical_analysis",
    description="Perform statistical analysis on data sets",
    parameters={
        "type": "object",
        "properties": {
            "data": {"type": "array", "items": {"type": "number"}, "description": "Data points"},
            "analysis_type": {"type": "string", "description": "Type of analysis (descriptive, inferential)"},
        },
        "required": ["data"],
    },
)
def statistical_analysis(data: list[float], analysis_type: str = "descriptive") -> str:
    """Perform statistical analysis on data."""
    
    if not data:
        return "No data provided for analysis"
    
    n = len(data)
    mean = sum(data) / n
    sorted_data = sorted(data)
    median = sorted_data[n // 2] if n % 2 == 1 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    min_val = min(data)
    max_val = max(data)
    
    variance = sum((x - mean) ** 2 for x in data) / n
    std_dev = variance ** 0.5
    
    result = f"""
# Statistical Analysis Report

## Data Overview
- Sample size (n): {n}
- Analysis type: {analysis_type}

## Descriptive Statistics
- Mean: {mean:.4f}
- Median: {median:.4f}
- Standard Deviation: {std_dev:.4f}
- Variance: {variance:.4f}
- Minimum: {min_val}
- Maximum: {max_val}
- Range: {max_val - min_val}

## Data Distribution
- The data shows {'normal' if 0.5 < std_dev / mean < 2.0 else 'non-normal'} distribution characteristics

## Recommendations
- Consider visualizing with histograms
- Check for outliers beyond 2 standard deviations
- Verify data quality and completeness
"""
    return result.strip()


# =============================================================================
# Creative Writing Skills
# =============================================================================

@skill(
    name="creative_writing",
    description="Generate creative content including stories, poems, and articles",
    parameters={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Topic or theme"},
            "style": {"type": "string", "description": "Writing style (formal, casual, poetic, technical)"},
            "format": {"type": "string", "description": "Format (story, poem, article, email)"},
            "length": {"type": "string", "description": "Length (short, medium, long)"},
        },
        "required": ["topic", "format"],
    },
)
def creative_writing(topic: str, format: str, style: str = "casual", length: str = "medium") -> str:
    """Generate creative content."""
    
    content = f"""
# {format.title()}: {topic.title()}

## Style: {style.title()}
## Length: {length.title()}

---

[Content would be generated here based on:
- Topic: {topic}
- Format: {format}
- Style: {style}
- Length: {length}]

---

*Note: For actual creative writing, integrate with an LLM for content generation.*
"""
    return content.strip()


@skill(
    name="edit_improve_text",
    description="Edit and improve existing text for clarity, grammar, and style",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to edit"},
            "goal": {"type": "string", "description": "Editing goal (clarity, conciseness, formality, grammar)"},
        },
        "required": ["text"],
    },
)
def edit_improve_text(text: str, goal: str = "clarity") -> str:
    """Edit and improve text."""
    
    word_count = len(text.split())
    
    result = f"""
# Text Editing Report

## Original Text Statistics
- Word count: {word_count}
- Editing goal: {goal}

## Analysis

### Strengths
- [Identify strengths in original text]

### Areas for Improvement
- [Identify areas needing improvement]
- [Grammar issues if any]
- [Clarity issues if any]

## Suggestions

### For {goal.title()}:
1. Review sentence structure
2. Eliminate redundant words
3. Ensure logical flow
4. Check grammar and punctuation
5. Verify tone consistency

## Edited Version
[Edited text would appear here]

---
*Note: For actual editing, integrate with an LLM.*
"""
    return result.strip()


# =============================================================================
# Data Analysis Skills
# =============================================================================

@skill(
    name="analyze_data",
    description="Analyze data sets and provide insights",
    parameters={
        "type": "object",
        "properties": {
            "data_description": {"type": "string", "description": "Description of the data"},
            "questions": {"type": "array", "items": {"type": "string"}, "description": "Questions to answer"},
        },
        "required": ["data_description"],
    },
)
def analyze_data(data_description: str, questions: list[str] | None = None) -> str:
    """Analyze data and provide insights."""
    
    result = f"""
# Data Analysis Report

## Data Description
{data_description}

## Analysis Framework

### 1. Data Quality Assessment
- Completeness: Check for missing values
- Accuracy: Verify data correctness
- Consistency: Ensure uniform formats
- Timeliness: Confirm data is current

### 2. Exploratory Analysis
- Distribution analysis
- Outlier detection
- Pattern identification
- Trend analysis

### 3. Insights Generation
- Key findings
- Correlations discovered
- Anomalies detected
- Recommendations

"""
    
    if questions:
        result += "## Questions to Answer\n"
        for i, q in enumerate(questions, 1):
            result += f"{i}. {q}\n"
        result += "\n[Answers would be provided based on data analysis]\n"
    
    return result.strip()


@skill(
    name="compare_options",
    description="Compare multiple options and provide recommendation",
    parameters={
        "type": "object",
        "properties": {
            "options": {"type": "array", "items": {"type": "string"}, "description": "Options to compare"},
            "criteria": {"type": "array", "items": {"type": "string"}, "description": "Comparison criteria"},
        },
        "required": ["options"],
    },
)
def compare_options(options: list[str], criteria: list[str] | None = None) -> str:
    """Compare multiple options systematically."""
    
    if not criteria:
        criteria = ["Cost", "Quality", "Time", "Risk", "Scalability"]
    
    result = """
# Options Comparison Analysis

## Options to Compare
"""
    for i, opt in enumerate(options, 1):
        result += f"{i}. {opt}\n"
    
    result += "\n## Comparison Criteria\n"
    for criterion in criteria:
        result += f"- {criterion}\n"
    
    result += "\n## Comparison Matrix\n\n"
    result += "| Option | " + " | ".join(criteria) + " |\n"
    result += "|" + "|".join(["--------"] * (len(criteria) + 1)) + "|\n"
    
    for opt in options:
        result += f"| {opt[:20]} | " + " | ".join(["TBD"] * len(criteria)) + " |\n"
    
    result += """
## Recommendation

### Evaluation Summary
- [Summary of evaluation]

### Best Option
[Recommended option with justification]

### Risk Assessment
- [Key risks to consider]

---
*Note: Fill in comparison matrix with actual analysis.*
"""
    
    return result.strip()


# =============================================================================
# Multi-step Problem Solving
# =============================================================================

@skill(
    name="step_by_step_solver",
    description="Solve complex problems with detailed step-by-step guidance",
    parameters={
        "type": "object",
        "properties": {
            "problem": {"type": "string", "description": "Problem to solve"},
            "context": {"type": "string", "description": "Additional context"},
        },
        "required": ["problem"],
    },
)
def step_by_step_solver(problem: str, context: str | None = None) -> str:
    """Solve problems step-by-step."""
    
    solution = f"""
# Step-by-Step Problem Solution

## Problem Statement
{problem}

"""
    
    if context:
        solution += f"## Context\n{context}\n\n"
    
    solution += """
## Solution Approach

### Step 1: Understand the Problem
- Read the problem carefully
- Identify what is given
- Identify what needs to be found
- Note any constraints or conditions

### Step 2: Plan the Solution
- Break down into sub-problems
- Identify relevant concepts/formulas
- Determine the order of operations
- Consider alternative approaches

### Step 3: Execute the Plan
- Work through each step systematically
- Show all calculations
- Document assumptions
- Keep track of units

### Step 4: Review and Verify
- Check each step for errors
- Verify the answer is reasonable
- Test with sample values if applicable
- Consider edge cases

### Step 5: Document the Solution
- Write clear explanations
- Format the final answer
- Summarize key points
- Note any limitations

## Final Answer
[Solution would be provided here]

---
*Note: For actual problem solving, integrate with an LLM.*
"""
    
    return solution.strip()


# =============================================================================
# Skill Registration Helper
# =============================================================================

def get_all_claude_skills() -> list:
    """Get list of all Claude-like skills."""
    return [
        analyze_complex_problem,
        logical_reasoning,
        explain_code,
        generate_code,
        debug_code,
        summarize_text,
        extract_information,
        solve_math_problem,
        statistical_analysis,
        creative_writing,
        edit_improve_text,
        analyze_data,
        compare_options,
        step_by_step_solver,
    ]


def register_claude_skills(agent) -> None:
    """Register all Claude-like skills with an agent."""
    for skill_func in get_all_claude_skills():
        agent.add_skill(skill_func)
