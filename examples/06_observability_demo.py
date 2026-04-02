#!/usr/bin/env python3
"""Observability Demo: Live Thought Process.

This example shows the new 'verbose' mode in run_autonomous, 
which provides a rich terminal dashboard of the agent's actions.
"""

from unittest.mock import patch

from piranha_agent.agent import Agent, LLMResponse
from piranha_agent.llm_provider import LLMProvider
from piranha_agent.skill import skill


@skill(name="fetch_data", description="Fetch data from a source")
def fetch_data(source: str):
    return f"Data from {source}: [Result A, Result B, Result C]"

@skill(name="analyze_results", description="Analyze the fetched data")
def analyze_results(data: str):
    return f"Analysis complete: Found 3 items in '{data}'."

def main():
    agent = Agent(name="VisibleAgent")
    agent.add_skill(fetch_data)
    agent.add_skill(analyze_results)
    
    # Mock LLM to simulate a multi-turn autonomous process
    responses = [
        # Turn 1: Call fetch_data
        LLMResponse(
            content=None,
            model="gpt-4",
            tool_calls=[{
                "id": "c1", "type": "function", 
                "function": {"name": "fetch_data", "arguments": '{"source": "database"}'}
            }]
        ),
        # Turn 2: Call analyze_results
        LLMResponse(
            content=None,
            model="gpt-4",
            tool_calls=[{
                "id": "c2", "type": "function", 
                "function": {"name": "analyze_results", "arguments": '{"data": "Result A, Result B, Result C"}'}
            }]
        ),
        # Turn 3: Final Answer
        LLMResponse(
            content="I have fetched and analyzed the data. There are 3 items: A, B, and C.",
            model="gpt-4"
        )
    ]
    
    print("🎬 Starting Observability Demo...")
    print("Wait for the 'Rich' output below:\n")
    
    with patch.object(LLMProvider, 'chat', side_effect=responses):
        agent.run_autonomous("Fetch and analyze the data from the database.", verbose=True)

if __name__ == "__main__":
    main()
