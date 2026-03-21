#!/usr/bin/env python3
"""Claude-like Skills Demo.

This example demonstrates using Piranha Agent with Claude-like capabilities.

Usage:
    python examples/09_claude_skills.py
"""

from piranha import Agent, Task
from piranha.claude_skills import (
    analyze_complex_problem,
    logical_reasoning,
    explain_code,
    generate_code,
    debug_code,
    summarize_text,
    extract_information,
    solve_math_problem,
    statistical_analysis,
    compare_options,
    step_by_step_solver,
    register_claude_skills,
)


def main():
    print("=" * 70)
    print("CLAUDE-LIKE SKILLS DEMO")
    print("=" * 70)
    print()

    # Create agent with Claude-like skills
    agent = Agent(
        name="claude_assistant",
        model="ollama/llama3:latest",
        description="AI assistant with Claude-like capabilities",
        skills=[
            analyze_complex_problem,
            logical_reasoning,
            explain_code,
            generate_code,
            debug_code,
            summarize_text,
            extract_information,
            solve_math_problem,
            statistical_analysis,
            compare_options,
            step_by_step_solver,
        ],
    )

    print(f"Created agent: {agent.name}")
    print(f"Skills registered: {len(agent.skills)}")
    print()

    # =========================================================================
    # Demo 1: Complex Problem Analysis
    # =========================================================================
    print("-" * 70)
    print("Demo 1: Complex Problem Analysis")
    print("-" * 70)
    print()

    result = analyze_complex_problem(
        problem="How to reduce customer churn in a SaaS business?",
        domain="business"
    )
    print(result)
    print()

    # =========================================================================
    # Demo 2: Logical Reasoning
    # =========================================================================
    print("-" * 70)
    print("Demo 2: Logical Reasoning")
    print("-" * 70)
    print()

    result = logical_reasoning(
        premises=[
            "All developers write code",
            "Alice is a developer",
            "People who write code use computers"
        ],
        conclusion="Alice uses a computer"
    )
    print(result)
    print()

    # =========================================================================
    # Demo 3: Code Explanation
    # =========================================================================
    print("-" * 70)
    print("Demo 3: Code Explanation")
    print("-" * 70)
    print()

    sample_code = '''
def fibonacci(n):
    """Generate fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    sequence = [0, 1]
    while len(sequence) < n:
        next_val = sequence[-1] + sequence[-2]
        sequence.append(next_val)
    
    return sequence
'''

    result = explain_code(
        code=sample_code,
        language="python",
        audience="beginner"
    )
    print(result)
    print()

    # =========================================================================
    # Demo 4: Code Generation
    # =========================================================================
    print("-" * 70)
    print("Demo 4: Code Generation")
    print("-" * 70)
    print()

    result = generate_code(
        task="Calculate the average of a list of numbers",
        language="python",
        requirements=[
            "Handle empty lists",
            "Support both integers and floats",
            "Return None for invalid input"
        ]
    )
    print(result)
    print()

    # =========================================================================
    # Demo 5: Code Debugging
    # =========================================================================
    print("-" * 70)
    print("Demo 5: Code Debugging")
    print("-" * 70)
    print()

    buggy_code = '''
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers) + 1):
        total += numbers[i]
    return total
'''

    result = debug_code(
        code=buggy_code,
        error_message="IndexError: list index out of range",
        expected_behavior="Sum all numbers in the list"
    )
    print(result)
    print()

    # =========================================================================
    # Demo 6: Statistical Analysis
    # =========================================================================
    print("-" * 70)
    print("Demo 6: Statistical Analysis")
    print("-" * 70)
    print()

    data = [23.5, 25.1, 22.8, 24.3, 26.0, 23.9, 25.5, 24.1, 23.2, 25.8]
    result = statistical_analysis(
        data=data,
        analysis_type="descriptive"
    )
    print(result)
    print()

    # =========================================================================
    # Demo 7: Compare Options
    # =========================================================================
    print("-" * 70)
    print("Demo 7: Compare Options")
    print("-" * 70)
    print()

    result = compare_options(
        options=[
            "Build in-house solution",
            "Buy commercial software",
            "Use open-source alternative"
        ],
        criteria=["Cost", "Time", "Customization", "Support", "Security"]
    )
    print(result)
    print()

    # =========================================================================
    # Demo 8: Step-by-Step Problem Solver
    # =========================================================================
    print("-" * 70)
    print("Demo 8: Step-by-Step Problem Solver")
    print("-" * 70)
    print()

    result = step_by_step_solver(
        problem="A train travels at 60 mph for 2 hours, then at 80 mph for 3 hours. What is the average speed?",
        context="Physics problem involving distance, speed, and time"
    )
    print(result)
    print()

    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 70)
    print("CLAUDE-LIKE SKILLS DEMO COMPLETE!")
    print("=" * 70)
    print()
    print("Skills Demonstrated:")
    print("  ✓ Complex Problem Analysis")
    print("  ✓ Logical Reasoning")
    print("  ✓ Code Explanation")
    print("  ✓ Code Generation")
    print("  ✓ Code Debugging")
    print("  ✓ Statistical Analysis")
    print("  ✓ Options Comparison")
    print("  ✓ Step-by-Step Problem Solving")
    print()
    print("Additional Available Skills:")
    print("  - Text Summarization")
    print("  - Information Extraction")
    print("  - Mathematical Problem Solving")
    print("  - Creative Writing")
    print("  - Text Editing")
    print("  - Data Analysis")
    print()
    print("Usage:")
    print("  from piranha.claude_skills import register_claude_skills")
    print("  register_claude_skills(agent)")
    print()


if __name__ == "__main__":
    main()
