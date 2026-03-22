"""Tests for AsyncAgent and AgentGroup.

Target: Increase async_agent.py coverage from 26% to 80%+
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from piranha.async_agent import AsyncAgent, AgentGroup
from piranha.skill import Skill, skill
from piranha.llm_provider import LLMResponse


class TestAsyncAgent:
    """Tests for AsyncAgent class."""

    def test_create_async_agent(self):
        """Test creating an async agent."""
        agent = AsyncAgent(name="test-agent", model="ollama/llama3:latest")
        
        assert agent.name == "test-agent"
        assert agent.model == "ollama/llama3:latest"
        assert agent.description == ""
        assert agent.system_prompt == ""
        assert agent.skills == []
        assert agent.session is not None
        assert agent._llm is not None
        assert agent._context is not None
        assert agent._memory is not None

    def test_create_async_agent_with_options(self):
        """Test creating an async agent with custom options."""
        agent = AsyncAgent(
            name="custom-agent",
            model="gpt-4",
            description="A custom agent",
            system_prompt="You are a helpful assistant",
            api_base="http://localhost:11434",
            api_key="test-key",
        )
        
        assert agent.name == "custom-agent"
        assert agent.model == "gpt-4"
        assert agent.description == "A custom agent"
        assert agent.system_prompt == "You are a helpful assistant"
        assert agent._llm.api_base == "http://localhost:11434"
        assert agent._llm.api_key == "test-key"

    def test_create_async_agent_with_skills(self):
        """Test creating an async agent with skills."""
        @skill(description="Test skill")
        def test_func():
            return "test"
        
        agent = AsyncAgent(
            name="skilled-agent",
            model="ollama/llama3:latest",
            skills=[test_func],
        )
        
        assert len(agent.skills) == 1
        assert agent.skills[0].name == "test_func"

    def test_add_skill(self):
        """Test adding a skill to an async agent."""
        agent = AsyncAgent(name="test-agent")

        # Verify that the default model is correctly set when not specified
        assert agent.model == "ollama/llama3:latest"

        new_skill = Skill(name="new_skill", description="A new skill")
        agent.add_skill(new_skill)

        assert len(agent.skills) == 1
        assert agent.skills[0].name == "new_skill"

    @pytest.mark.asyncio
    async def test_create_async_agent_with_invalid_model(self):
        """Test creating an async agent with an invalid/unsupported model."""
        agent = AsyncAgent(name="invalid-agent", model="invalid-model")
        # Ensure the model attribute reflects the provided invalid value
        assert agent.model == "invalid-model"
        
        # Mock the underlying LLM call to avoid real network/model interactions
        mock_response = LLMResponse(
            content="Mocked response for invalid model",
            model="invalid-model",
            prompt_tokens=1,
            completion_tokens=1,
            cost_usd=0.0,
            finish_reason="stop",
        )
        with patch.object(agent._llm, "chat_async", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_response
            response = await agent.chat("Hello")
            # Current behavior: the agent should still return the mocked response
            assert response == "Mocked response for invalid model"

    @pytest.mark.asyncio
    async def test_chat_basic(self):
        """Test basic chat functionality."""
        agent = AsyncAgent(name="test-agent", model="ollama/llama3:latest")

        # Create a proper async mock response
        mock_response = LLMResponse(
            content="Hello! How can I help you?",
            model="ollama/llama3:latest",
            prompt_tokens=10,
            completion_tokens=20,
            cost_usd=0.001,
            finish_reason="stop",
        )
        
        with patch.object(agent._llm, 'chat_async', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_response

            response = await agent.chat("Hello")
            
            assert response == "Hello! How can I help you?"
            assert len(agent.get_history()) == 2  # user + assistant

    @pytest.mark.asyncio
    async def test_run_with_system_prompt(self):
        """Test run with system prompt."""
        agent = AsyncAgent(
            name="test-agent",
            model="ollama/llama3:latest",
            system_prompt="You are a coding assistant",
        )

        with patch.object(agent._llm, 'chat_async', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = LLMResponse(
                content="Here's the code...",
                model="ollama/llama3:latest",
                prompt_tokens=50,
                completion_tokens=100,
                cost_usd=0.005,
                finish_reason="stop",
            )

            response = await agent.run("Write a function")

            assert response.content == "Here's the code..."
            # System prompt should be in history
            history = agent.get_history()
            assert history[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_run_cache_hit(self):
        """Test run with cache hit."""
        agent = AsyncAgent(name="test-agent", model="ollama/llama3:latest")

        # Mock cache to return a hit
        mock_cache_response = {
            "response": "Cached response",
            "model": "ollama/llama3:latest",
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "cost_usd": 0.001,
        }
        
        with patch.object(agent._semantic_cache, 'get', return_value=mock_cache_response):
            with patch.object(agent._semantic_cache, 'compute_key', return_value="test_key"):
                response = await agent.run("Test query")

                assert response.content == "Cached response"
                assert response.finish_reason == "cache_hit"

    @pytest.mark.asyncio
    async def test_run_with_memory_context(self):
        """Test run with memory context."""
        agent = AsyncAgent(name="test-agent", model="ollama/llama3:latest")

        # Add memory
        agent.add_to_memory("User prefers Python", tags=["preference"])

        with patch.object(agent._llm, 'chat_async', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = LLMResponse(
                content="Response with context",
                model="ollama/llama3:latest",
                prompt_tokens=30,
                completion_tokens=40,
                cost_usd=0.002,
                finish_reason="stop",
            )

            response = await agent.run("Help me code")

            assert response.content == "Response with context"
            
            # Verify that the added memory is actually used to build the LLM input.
            # We don't rely on a specific interface; instead, we check that the
            # memory text appears somewhere in the arguments passed to chat_async.
            _, kwargs = mock_chat.call_args
            args_str = repr(kwargs)
            assert "User prefers Python" in args_str, "Memory content should be passed to LLM"

    @pytest.mark.asyncio
    async def test_run_streaming(self):
        """Test streaming response."""
        agent = AsyncAgent(name="test-agent", model="ollama/llama3:latest")

        async def mock_stream():
            yield "Hello"
            yield " "
            yield "World"

        # Create async mock that returns the stream generator
        mock_chat = AsyncMock()
        mock_chat.return_value = mock_stream()

        with patch.object(agent._llm, 'chat_async', mock_chat):
            # Don't await when streaming - get the async generator
            response = agent.run("Test", stream=True)

            # Collect streaming response
            chunks = []
            async for chunk in response:
                chunks.append(chunk)

            assert chunks == ["Hello", " ", "World"]

            # Verify that the full streamed response is recorded in history
            full_response = "".join(chunks)
            history = agent.get_history()
            # Find the last assistant message in the history
            assistant_messages = [m for m in history if m.get("role") == "assistant"]
            assert assistant_messages, "Expected at least one assistant message in history"
            assert assistant_messages[-1].get("content") == full_response

    def test_get_history(self):
        """Test getting conversation history."""
        agent = AsyncAgent(name="test-agent", model="ollama/llama3:latest")
        
        # Initial history should be empty (or just system prompt)
        history = agent.get_history()
        assert isinstance(history, list)

    def test_clear_history(self):
        """Test clearing conversation history."""
        agent = AsyncAgent(
            name="test-agent",
            model="ollama/llama3:latest",
            system_prompt="You are helpful",
        )
        
        # Add some messages
        agent._messages.append({"role": "user", "content": "Hello"})
        agent._messages.append({"role": "assistant", "content": "Hi"})
        
        # Clear history
        agent.clear_history()
        
        # Should only have system prompt
        history = agent.get_history()
        assert len(history) == 1
        assert history[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_get_cost_report(self):
        """Test getting cost report after operations with known cost."""
        agent = AsyncAgent(name="test-agent", model="ollama/llama3:latest")

        # Perform a chat with a mocked LLM response that has a known cost
        with patch.object(agent._llm, 'chat_async', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = LLMResponse(
                content="Mocked response",
                model="ollama/llama3:latest",
                prompt_tokens=10,
                completion_tokens=20,
                cost_usd=0.01,
                finish_reason="stop",
            )
            await agent.chat("Test message")

        report = agent.get_cost_report()

        assert isinstance(report, dict)
        assert "total_cost_usd" in report
        # The total cost should reflect the mocked LLM response cost
        assert report["total_cost_usd"] == pytest.approx(0.01)

    @pytest.mark.asyncio
    async def test_multiple_chat_turns(self):
        """Test multiple chat turns maintain context."""
        agent = AsyncAgent(name="test-agent", model="ollama/llama3:latest")

        responses = [
            "First response",
            "Second response",
            "Third response",
        ]

        with patch.object(agent._llm, 'chat_async', new_callable=AsyncMock) as mock_chat:
            for i, expected_response in enumerate(responses):
                mock_chat.return_value = LLMResponse(
                    content=expected_response,
                    model="ollama/llama3:latest",
                    prompt_tokens=10 * (i + 1),
                    completion_tokens=20,
                    cost_usd=0.001,
                    finish_reason="stop",
                )

                response = await agent.chat(f"Message {i+1}")
                assert response == expected_response

        # History should have all turns
        history = agent.get_history()
        assert len(history) == len(responses) * 2  # user + assistant for each

    @pytest.mark.asyncio
    async def test_run_error_handling(self):
        """Test error handling in run."""
        agent = AsyncAgent(name="test-agent", model="ollama/llama3:latest")
        
        with patch.object(agent._llm, 'chat_async', new_callable=AsyncMock) as mock_chat:
            mock_chat.side_effect = Exception("LLM error")
            
            with pytest.raises(Exception):
                await agent.run("Test")

    def test_agent_session_id_property(self):
        """Test agent session ID property."""
        agent = AsyncAgent(name="test-agent")

        assert agent.session_id is not None
        assert len(agent.session_id) > 0

    def test_context_manager_property(self):
        """Test context manager property."""
        agent = AsyncAgent(name="test-agent")
        
        assert agent.context is not None
        assert agent._context is agent.context

    def test_memory_manager_property(self):
        """Test memory manager property."""
        agent = AsyncAgent(name="test-agent")
        
        assert agent.memory is not None
        assert agent._memory is agent.memory


class TestAgentGroup:
    """Tests for AgentGroup class."""

    def test_create_agent_group(self):
        """Test creating an agent group."""
        agent1 = AsyncAgent(name="agent1")
        agent2 = AsyncAgent(name="agent2")
        
        group = AgentGroup([agent1, agent2])
        
        assert len(group.agents) == 2
        assert group.agents[0].name == "agent1"
        assert group.agents[1].name == "agent2"

    @pytest.mark.asyncio
    async def test_run_parallel(self):
        """Test running tasks in parallel."""
        agent1 = AsyncAgent(name="agent1")
        agent2 = AsyncAgent(name="agent2")
        
        group = AgentGroup([agent1, agent2])
        
        with patch.object(agent1._llm, 'chat_async', new_callable=AsyncMock) as mock1:
            with patch.object(agent2._llm, 'chat_async', new_callable=AsyncMock) as mock2:
                mock1.return_value = MagicMock(
                    content="Response from agent 1",
                    model="ollama/llama3:latest",
                    prompt_tokens=10,
                    completion_tokens=20,
                    cost_usd=0.001,
                    finish_reason="stop",
                )
                mock2.return_value = MagicMock(
                    content="Response from agent 2",
                    model="ollama/llama3:latest",
                    prompt_tokens=15,
                    completion_tokens=25,
                    cost_usd=0.002,
                    finish_reason="stop",
                )
                
                results = await group.run_parallel("Same task")
                
                assert len(results) == 2
                assert results[0].content == "Response from agent 1"
                assert results[1].content == "Response from agent 2"

    @pytest.mark.asyncio
    async def test_run_sequential(self):
        """Test running tasks sequentially."""
        agent1 = AsyncAgent(name="agent1")
        agent2 = AsyncAgent(name="agent2")
        
        group = AgentGroup([agent1, agent2])
        
        with patch.object(agent1._llm, 'chat_async', new_callable=AsyncMock) as mock1:
            with patch.object(agent2._llm, 'chat_async', new_callable=AsyncMock) as mock2:
                mock1.return_value = MagicMock(
                    content="First response",
                    model="ollama/llama3:latest",
                    prompt_tokens=10,
                    completion_tokens=20,
                    cost_usd=0.001,
                    finish_reason="stop",
                )
                mock2.return_value = MagicMock(
                    content="Second response",
                    model="ollama/llama3:latest",
                    prompt_tokens=15,
                    completion_tokens=25,
                    cost_usd=0.002,
                    finish_reason="stop",
                )
                
                results = await group.run_sequential("Same task")
                
                assert len(results) == 2
                assert results[0].content == "First response"
                assert results[1].content == "Second response"

    @pytest.mark.asyncio
    async def test_run_pipeline(self):
        """Test running tasks in pipeline (each receives previous output)."""
        agent1 = AsyncAgent(name="agent1")
        agent2 = AsyncAgent(name="agent2")
        agent3 = AsyncAgent(name="agent3")
        
        group = AgentGroup([agent1, agent2, agent3])
        
        with patch.object(agent1._llm, 'chat_async', new_callable=AsyncMock) as mock1:
            with patch.object(agent2._llm, 'chat_async', new_callable=AsyncMock) as mock2:
                with patch.object(agent3._llm, 'chat_async', new_callable=AsyncMock) as mock3:
                    mock1.return_value = MagicMock(
                        content="Step 1 output",
                        model="ollama/llama3:latest",
                        prompt_tokens=10,
                        completion_tokens=20,
                        cost_usd=0.001,
                        finish_reason="stop",
                    )
                    mock2.return_value = MagicMock(
                        content="Step 2 output",
                        model="ollama/llama3:latest",
                        prompt_tokens=15,
                        completion_tokens=25,
                        cost_usd=0.002,
                        finish_reason="stop",
                    )
                    mock3.return_value = MagicMock(
                        content="Final output",
                        model="ollama/llama3:latest",
                        prompt_tokens=20,
                        completion_tokens=30,
                        cost_usd=0.003,
                        finish_reason="stop",
                    )
                    
                    results = await group.run_pipeline("Initial task")
                    
                    assert len(results) == 3
                    assert results[0].content == "Step 1 output"
                    assert results[1].content == "Step 2 output"
                    assert results[2].content == "Final output"

    @pytest.mark.asyncio
    async def test_run_pipeline_with_transform(self):
        """Test running pipeline with transform function."""
        agent1 = AsyncAgent(name="agent1")
        agent2 = AsyncAgent(name="agent2")

        group = AgentGroup([agent1, agent2])

        transform_calls = []

        def transform_fn(output, index):
            transform_calls.append((output, index))
            return f"Transformed: {output}"

        with patch.object(agent1._llm, 'chat_async', new_callable=AsyncMock) as mock1:
            with patch.object(agent2._llm, 'chat_async', new_callable=AsyncMock) as mock2:
                mock1.return_value = LLMResponse(
                    content="First output",
                    model="ollama/llama3:latest",
                    prompt_tokens=10,
                    completion_tokens=20,
                    cost_usd=0.001,
                    finish_reason="stop",
                )
                mock2.return_value = LLMResponse(
                    content="Second output",
                    model="ollama/llama3:latest",
                    prompt_tokens=15,
                    completion_tokens=25,
                    cost_usd=0.002,
                    finish_reason="stop",
                )

                results = await group.run_pipeline("Task", transform=transform_fn)

                assert len(results) == 2
                # Transform should be called for both agents
                assert len(transform_calls) == 2
                # First call with initial task, second with first agent's output
                assert transform_calls[0] == ("Task", 0)
                assert transform_calls[1][1] == 1

    @pytest.mark.asyncio
    async def test_run_parallel_concurrent_execution(self):
        """Test that parallel execution is actually concurrent."""
        agent1 = AsyncAgent(name="agent1")
        agent2 = AsyncAgent(name="agent2")
        
        group = AgentGroup([agent1, agent2])
        
        execution_order = []
        
        async def slow_chat1(*args, **kwargs):
            execution_order.append("agent1_start")
            await asyncio.sleep(0.1)
            execution_order.append("agent1_end")
            return MagicMock(
                content="Response 1",
                model="ollama/llama3:latest",
                prompt_tokens=10,
                completion_tokens=20,
                cost_usd=0.001,
                finish_reason="stop",
            )
        
        async def slow_chat2(*args, **kwargs):
            execution_order.append("agent2_start")
            await asyncio.sleep(0.05)  # agent2 is faster
            execution_order.append("agent2_end")
            return MagicMock(
                content="Response 2",
                model="ollama/llama3:latest",
                prompt_tokens=15,
                completion_tokens=25,
                cost_usd=0.002,
                finish_reason="stop",
            )
        
        with patch.object(agent1._llm, 'chat_async', side_effect=slow_chat1):
            with patch.object(agent2._llm, 'chat_async', side_effect=slow_chat2):
                await group.run_parallel("Task")
        
        # With parallel execution, both should start before either ends
        assert execution_order.index("agent1_start") < execution_order.index("agent1_end")
        assert execution_order.index("agent2_start") < execution_order.index("agent2_end")
        # Both should start before either ends (concurrent)
        assert execution_order.index("agent1_start") < execution_order.index("agent2_end")
        assert execution_order.index("agent2_start") < execution_order.index("agent1_end")

    def test_agent_group_empty_list(self):
        """Test creating agent group with empty list."""
        group = AgentGroup([])
        
        assert len(group.agents) == 0

    def test_agent_group_single_agent(self):
        """Test creating agent group with single agent."""
        agent = AsyncAgent(name="solo-agent")
        group = AgentGroup([agent])
        
        assert len(group.agents) == 1
        assert group.agents[0].name == "solo-agent"

    def test_agent_group_many_agents(self):
        """Test creating agent group with many agents."""
        agents = [AsyncAgent(name=f"agent-{i}") for i in range(10)]
        group = AgentGroup(agents)
        
        assert len(group.agents) == 10
