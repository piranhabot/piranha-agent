#!/usr/bin/env python3
"""Multi-agent example: Coordinating multiple agents.

This example demonstrates:
- Creating multiple specialized agents
- Coordinating work between agents
- Aggregating results from multiple agents
"""

from piranha_agent import Agent, Task


def main():
    # Create specialized agents
    researcher = Agent(
        name="researcher",
        model="ollama/llama3:latest",
        description="Researches topics and gathers information",
        system_prompt="You are a research expert. Gather comprehensive information on any topic.",
    )
    
    writer = Agent(
        name="writer",
        model="ollama/llama3:latest",
        description="Writes clear, engaging content",
        system_prompt="You are a writing expert. Transform information into well-written content.",
    )
    
    reviewer = Agent(
        name="reviewer",
        model="ollama/llama3:latest",
        description="Reviews and improves content",
        system_prompt="You are a quality reviewer. Identify issues and suggest improvements.",
    )
    
    print("Created multi-agent team:")
    print(f"  - {researcher.name}: {researcher.description}")
    print(f"  - {writer.name}: {writer.description}")
    print(f"  - {reviewer.name}: {reviewer.description}")
    print()
    
    # Topic to research and write about
    topic = "The history and future of renewable energy"
    
    # Step 1: Research
    print("Step 1: Researching topic...")
    research_task = Task(
        description=f"Research {topic}. Provide key facts, dates, and trends.",
        agent=researcher,
    )
    research_result = research_task.run()
    print("  ✓ Research complete")
    
    # Step 2: Write
    print("Step 2: Writing content...")
    writing_task = Task(
        description=f"Write a 300-word article about {topic}",
        agent=writer,
        context=research_result.result,
    )
    writing_result = writing_task.run()
    print("  ✓ Writing complete")
    
    # Step 3: Review
    print("Step 3: Reviewing content...")
    review_task = Task(
        description="Review the article for accuracy, clarity, and engagement. Suggest improvements.",
        agent=reviewer,
        context=writing_result.result,
    )
    review_result = review_task.run()
    print("  ✓ Review complete")
    
    print()
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"\n📝 Article:\n{writing_result.result}")
    print(f"\n🔍 Review:\n{review_result.result}")
    
    # Show session info
    print("\n📊 Session Statistics:")
    print(f"  Researcher session: {researcher.session}")
    print(f"  Writer session: {writer.session}")
    print(f"  Reviewer session: {reviewer.session}")


if __name__ == "__main__":
    main()
