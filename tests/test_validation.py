"""Tests for HITL and Guardrails validation."""

from unittest.mock import patch
from uuid import uuid4

import pytest

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
    """Test that the agent's guardrail engine validates and blocks actions."""
    agent = Agent(name="GuardrailAgent")
    engine = agent._guardrail_engine
    assert engine is not None
    agent_id, session_id = str(uuid4()), str(uuid4())

    # A safe action within budget is allowed
    verdict = engine.check(agent_id, session_id, 0, None, "list files")
    assert verdict["verdict"] == "allow"

    # Crossing 80% of the token budget produces a warning
    verdict = engine.check(agent_id, session_id, 85_000, 100_000, "list files")
    assert verdict["verdict"] == "warn"
    assert "85" in verdict["reason"]

    # A dangerous command trips the hard content filter
    with pytest.raises(RuntimeError, match="dangerous_commands"):
        engine.check(agent_id, session_id, 0, None, "rm -rf /tmp/data")

    # An exhausted token budget hard-blocks any action
    with pytest.raises(RuntimeError, match="token_budget"):
        engine.check(agent_id, session_id, 100_000, 100_000, "list files")
