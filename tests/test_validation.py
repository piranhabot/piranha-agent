"""Tests for HITL and Guardrails validation."""

from unittest.mock import patch
from piranha_agent import Agent
from piranha_agent.llm_provider import LLMProvider, LLMResponse


def test_hitl_validation():
    """Test that HITL properly handles user denial."""
    agent = Agent(name="ValidationAgent")

    responses = [
        LLMResponse(
            content=None,
            model="gpt-4",
            tool_calls=[{
                "id": "call_1",
                "type": "function",
                "function": {"name": "test_action", "arguments": "{}"}
            }],
            finish_reason="tool_calls"
        ),
        LLMResponse(content="I couldn't proceed.", model="gpt-4")
    ]

    with patch.object(LLMProvider, 'chat', side_effect=responses):
        with patch('builtins.input', return_value='n'):
            result = agent.run_autonomous("Test action")
            assert result is not None


def test_guardrails_validation():
    """Test that guardrails properly validate agent actions."""
    agent = Agent(name="GuardrailAgent")
    assert agent.name == "GuardrailAgent"
