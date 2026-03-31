import pytest
from unittest.mock import MagicMock, patch
from piranha_agent.agent import Agent
from piranha_agent.llm_provider import LLMResponse, LLMProvider
from piranha_agent.skill import skill

@skill(
    name="sensitive_action",
    description="A dangerous action that needs approval",
    requires_confirmation=True
)
def sensitive_action():
    return "Action performed!"

def test_hitl_approval():
    agent = Agent(name="guard-agent", model="gpt-4")
    agent.add_skill(sensitive_action)
    
    responses = [
        LLMResponse(
            content=None,
            model="gpt-4",
            tool_calls=[{
                "id": "call_1",
                "type": "function",
                "function": {"name": "sensitive_action", "arguments": "{}"}
            }],
            finish_reason="tool_calls"
        ),
        LLMResponse(content="Final answer", model="gpt-4")
    ]
    
    with patch.object(LLMProvider, 'chat', side_effect=responses):
        # Mock input to return 'y' (approved)
        with patch('builtins.input', return_value='y'):
            result = agent.run_autonomous("Do something dangerous")
            assert result == "Final answer"
            
            # Check history to see if skill result is there
            history = agent.get_history()
            tool_msg = next(m for m in history if m["role"] == "tool")
            assert tool_msg["content"] == "Action performed!"

def test_hitl_denial():
    agent = Agent(name="guard-agent", model="gpt-4")
    agent.add_skill(sensitive_action)
    
    responses = [
        LLMResponse(
            content=None,
            model="gpt-4",
            tool_calls=[{
                "id": "call_1",
                "type": "function",
                "function": {"name": "sensitive_action", "arguments": "{}"}
            }],
            finish_reason="tool_calls"
        ),
        LLMResponse(content="I couldn't do it because you said no.", model="gpt-4")
    ]
    
    with patch.object(LLMProvider, 'chat', side_effect=responses):
        # Mock input to return 'n' (denied)
        with patch('builtins.input', return_value='n'):
            result = agent.run_autonomous("Do something dangerous")
            
            # Check history to see if denial message was sent to LLM
            history = agent.get_history()
            tool_msg = next(m for m in history if m["role"] == "tool")
            assert "User denied execution" in tool_msg["content"]
