#!/usr/bin/env python3
"""Skills example: Creating and using custom skills.

This example demonstrates:
- Creating skills with the @skill decorator
- Adding skills to an agent
- Using skills in task execution
"""

from piranha_agent import Agent, Task
from piranha_agent.skill import skill


# Define custom skills using the decorator
@skill(
    name="web_search",
    description="Search the web for information",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"],
    },
    permissions=["network_read"],
)
def web_search(query: str) -> str:
    """Search the web and return results."""
    # In a real implementation, this would call a search API
    return f"Search results for '{query}': [mock results]"


@skill(
    name="calculator",
    description="Perform mathematical calculations",
    parameters={
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Math expression"}
        },
        "required": ["expression"],
    },
)
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        # Note: eval is dangerous in production - use a proper parser
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


@skill(
    name="file_reader",
    description="Read contents of a file",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path"}
        },
        "required": ["path"],
    },
    permissions=["file_read"],
)
def read_file(path: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(path) as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def main():
    # Create an agent with skills
    agent = Agent(
        name="researcher",
        model="ollama/llama3:latest",
        description="A research assistant with web search capabilities",
        skills=[web_search, calculator],
    )
    
    print(f"Created agent: {agent.name}")
    print(f"Available skills: {[s.name for s in agent.skills]}")
    print()
    
    # Test the calculator skill directly
    print("Testing calculator skill directly:")
    result = calculator("2 + 2 * 3")
    print(f"  2 + 2 * 3 = {result}")
    print()
    
    # Create a task that would use skills
    task = Task(
        description="Search for the latest news about AI and summarize it",
        agent=agent,
        context="You have access to web_search and calculator skills",
    )
    
    print(f"Running task: {task.description}")
    print("-" * 50)
    
    result = task.run()
    print(f"Result: {result.result}")
    
    # Export trace for debugging
    trace = agent.export_trace()
    print(f"\nTrace exported ({len(trace)} bytes)")


if __name__ == "__main__":
    main()
