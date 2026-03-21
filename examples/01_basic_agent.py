#!/usr/bin/env python3
"""Basic example: Creating and using an agent.

This example demonstrates:
- Creating an Agent
- Running a simple task
- Viewing the response
"""

from piranha import Agent, Task


def main():
    # Create an agent
    agent = Agent(
        name="assistant",
        model="anthropic/claude-3-5-sonnet",
        description="A helpful AI assistant",
    )
    
    print(f"Created agent: {agent.name}")
    print(f"Agent ID: {agent.id}")
    print(f"Model: {agent.model}")
    print()
    
    # Create and run a task
    task = Task(
        description="Explain what quantum computing is in 2 sentences",
        agent=agent,
        expected_output="A brief explanation of quantum computing",
    )
    
    print(f"Running task: {task.description}")
    print("-" * 50)
    
    result = task.run()
    
    print(f"Result: {result.result}")
    print()
    print(f"Success: {result.success}")
    print(f"Cache hit: {result.is_cached}")
    
    # Show cost report
    cost_report = agent.get_cost_report()
    if cost_report:
        print(f"\nCost Report: {cost_report}")


if __name__ == "__main__":
    main()
