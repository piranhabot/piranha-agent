import os
from unittest.mock import patch

from piranha_agent.agent import Agent
from piranha_agent.llm_provider import LLMProvider, LLMResponse


def test_plan_mode_injection():
    agent = Agent(name="planner", system_prompt="Help me.")
    
    # Simulate LLM response calling draft_plan
    responses = [
        LLMResponse(
            content=None,
            model="gpt-4",
            tool_calls=[{
                "id": "c1", "type": "function", 
                "function": {"name": "draft_plan", "arguments": '{"content": "# My Plan"}'}
            }],
            finish_reason="tool_calls"
        ),
        LLMResponse(content="Plan approved and executing", model="gpt-4")
    ]
    
    with patch.object(LLMProvider, 'chat', side_effect=responses):
        with patch('builtins.input', return_value='y'): # Approve the plan
            agent.run_autonomous("Implement feature X", plan_first=True, max_iterations=2)
            
            # Verify system prompt was updated
            assert "[PLAN MODE ENABLED]" in agent._messages[0].content
            
            # Verify plan file was created
            assert os.path.exists("PLAN.md")
            with open("PLAN.md") as f:
                assert f.read() == "# My Plan"
            
            os.remove("PLAN.md")

def test_planning_skills_availability():
    agent = Agent(name="planner")
    # Before run_autonomous
    assert "draft_plan" not in [s.name for s in agent.skills]
    
    # We'll mock the run to not actually do anything
    with patch.object(Agent, 'run', return_value=LLMResponse(content="done", model="mock")):
        agent.run_autonomous("Task", plan_first=True, max_iterations=1)
        
    # Skills should have been added
    assert "draft_plan" in [s.name for s in agent.skills]
    assert "get_plan" in [s.name for s in agent.skills]
