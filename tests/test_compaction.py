from unittest.mock import patch

from piranha_agent.agent import Agent, LLMMessage
from piranha_agent.llm_provider import LLMProvider, LLMResponse


def test_compact_history_trigger():
    # Set threshold to 10
    agent = Agent(name="compact-agent", system_prompt="Be helpful", max_history_messages=10)
    
    # Fill history with 15 messages
    for i in range(15):
        agent._messages.append(LLMMessage(role="user", content=f"Message {i}"))
        
    assert len(agent._messages) == 16 # 1 system + 15 user
    
    # Mock summarizer response
    responses = [
        LLMResponse(content="We talked about many things.", model="gpt-4"), # For compaction
        LLMResponse(content="Final answer", model="gpt-4") # For the actual run
    ]
    
    with patch.object(LLMProvider, 'chat', side_effect=responses):
        # Trigger run which triggers compaction
        agent.run("Last message")
        
        # New history should be:
        # 1. System prompt
        # 2. Summary of first 10 messages
        # 3. Last 5 messages kept
        # 4. New user message ("Last message")
        # 5. Assistant response ("Final answer")
        
        # Actual logic:
        # total before run = 16
        # start_idx = 1
        # messages_to_summarize = messages[1:-5] (index 1 to 10 inclusive -> 10 messages)
        # remaining = messages[-5:]
        # new_messages = [system, summary, ...remaining, new_user, new_assistant]
        
        assert len(agent._messages) < 16
        assert agent._messages[0].content == "Be helpful"
        assert "SUMMARY OF PREVIOUS INTERACTION" in agent._messages[1].content
        assert agent._messages[1].role == "system"
