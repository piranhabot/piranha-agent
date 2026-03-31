import pytest
from unittest.mock import MagicMock, patch
from piranha_agent.agent import Agent
from piranha_agent.llm_provider import LLMResponse, LLMProvider

def test_budget_limit_trigger():
    # Set a very small budget
    agent = Agent(name="budget-agent", budget_limit=0.01)
    
    # Simulate a response that costs $0.02
    responses = [
        LLMResponse(
            content="Expensive thought", 
            model="gpt-4", 
            cost_usd=0.02,
            finish_reason="stop"
        )
    ]
    
    with patch.object(LLMProvider, 'chat', side_effect=responses):
        # First turn runs, cost becomes 0.02
        # Second turn should trigger budget check
        # Mock input to return 'exit'
        with patch('builtins.input', return_value='exit'):
            # We need at least 2 iterations to trigger the check at the START of the turn
            # Or just ensure it checks after the first turn's cost is recorded.
            # In our implementation, it checks at the BEGINNING of each turn.
            
            # 1. Run first task
            agent.run_autonomous("Task 1", max_iterations=2)
            
            assert agent.total_cost == 0.02
            assert agent.total_cost > agent.budget_limit

def test_budget_increase():
    agent = Agent(name="budget-agent", budget_limit=0.01)
    agent.total_cost = 0.02 # Force over budget
    
    # Mock LLM for the turn that happens AFTER increase
    response = LLMResponse(content="I'm back", model="gpt-4", cost_usd=0.001)
    
    with patch.object(LLMProvider, 'chat', return_value=response):
        # Mock input to return '1.0' (increase budget by $1)
        with patch('builtins.input', return_value='1.0'):
            # The loop should check budget, prompt, increase, and THEN run the turn
            agent.run_autonomous("Continue", max_iterations=1)
            
            assert agent.budget_limit == 1.01
            assert agent.total_cost > 0.02
