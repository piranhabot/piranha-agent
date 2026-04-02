#!/usr/bin/env python3
"""Example of Autonomous Agent Orchestration.

This example shows how a Coordinator agent can autonomously delegate
tasks to sub-agents and aggregate results using the run_autonomous loop.
"""

from piranha_agent.orchestration import create_orchestrated_team


def main():
    print("🚀 Initializing Autonomous Orchestrated Team...")
    
    # Create a team with a coordinator
    # Note: In a real scenario, you'd use a model like 'gpt-4' or 'claude-3-opus'
    # that supports tool calling.
    team = create_orchestrated_team(
        name="ResearchTeam",
        coordinator_model="ollama/llama3:latest" 
    )
    
    coordinator = team.coordinator
    
    print(f"Coordinator '{coordinator.name}' is ready.")
    print(f"Available skills: {[s.name for s in coordinator.skills]}")
    print("-" * 60)
    
    task = (
        "We need to research the impact of autonomous agents on software engineering. "
        "1. Delegate research to a 'researcher' agent. "
        "2. Delegate writing a summary to a 'writer' agent. "
        "3. Provide the final aggregated report."
    )
    
    print(f"Assignment: {task}")
    print("\nRunning autonomously (simulated)...")
    
    # In a real environment with a tool-capable LLM, you would just call:
    # final_report = coordinator.run_autonomous(task)
    # print(final_report)
    
    print("\n[NOTE] To run this for real, ensure your LLM (like Llama3 via Ollama) "
          "is configured correctly for tool calling in LiteLLM.")
    
    # Manual demonstration of what the loop does:
    print("\n--- Manual Step-by-Step Delegation (Simulating the loop) ---")
    
    delegate_skill = next(s for s in coordinator.skills if s.name == "delegate_task")
    
    # Step 1: Delegate Research
    print("\n[Coordinator -> Researcher]: Researching...")
    res1 = delegate_skill(
        agent_name="researcher",
        role="expert researcher",
        task_description="Research the top 3 benefits of AI agents in coding."
    )
    print(f"Result: {res1[:100]}...")
    
    # Step 2: Delegate Writing
    print("\n[Coordinator -> Writer]: Writing summary...")
    res2 = delegate_skill(
        agent_name="writer",
        role="technical writer",
        task_description=f"Write a short summary based on this research: {res1}"
    )
    print(f"Result: {res2[:100]}...")
    
    # Step 3: Get Status
    status_skill = next(s for s in coordinator.skills if s.name == "get_team_status")
    print("\n[Team Status]:")
    print(status_skill())

if __name__ == "__main__":
    main()
