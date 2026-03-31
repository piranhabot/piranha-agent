import pytest
from unittest.mock import MagicMock, patch
from piranha_agent.agent import Agent
from piranha_agent.llm_provider import LLMResponse, LLMProvider
from piranha_agent.skill import skill

@skill(
    name="get_weather",
    description="Get weather for a city",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string"}
        }
    }
)
def get_weather(city: str):
    return f"The weather in {city} is sunny."

def test_run_autonomous_loop():
    agent = Agent(name="auto-agent", model="gpt-4")
    agent.add_skill(get_weather)
    
    # Mock the LLM responses
    # Turn 1: Call tool
    # Turn 2: Provide final answer
    responses = [
        LLMResponse(
            content=None,
            model="gpt-4",
            tool_calls=[{
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"city": "San Francisco"}'
                }
            }],
            finish_reason="tool_calls"
        ),
        LLMResponse(
            content="The weather in San Francisco is sunny. You should wear a t-shirt.",
            model="gpt-4",
            finish_reason="stop"
        )
    ]
    
    with patch.object(LLMProvider, 'chat') as mock_chat:
        mock_chat.side_effect = responses
        
        final_answer = agent.run_autonomous("What is the weather in SF?")
        
        assert "San Francisco is sunny" in final_answer
        assert "t-shirt" in final_answer
        assert mock_chat.call_count == 2
        
        # Verify message history
        history = agent.get_history()
        # 1. system prompt (if any)
        # 2. user: task
        # 3. assistant: tool_calls
        # 4. tool: result
        # 5. user: continue
        # 6. assistant: final answer
        
        roles = [m["role"] for m in history]
        assert "user" in roles
        assert "assistant" in roles
        assert "tool" in roles
