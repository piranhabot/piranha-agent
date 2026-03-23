"""Tests for LLM Provider with LiteLLM integration.

Target: Increase llm_provider.py coverage from 68% to 90%+
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from piranha_agent.llm_provider import (
    LLMProvider,
    LLMMessage,
    LLMResponse,
    create_provider,
)


class TestLLMMessage:
    """Tests for LLMMessage class."""

    def test_create_message(self):
        """Test creating a basic message."""
        msg = LLMMessage(role="user", content="Hello")
        
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_create_system_message(self):
        """Test creating a system message."""
        msg = LLMMessage(role="system", content="You are helpful")
        
        assert msg.role == "system"
        assert msg.content == "You are helpful"

    def test_create_assistant_message(self):
        """Test creating an assistant message."""
        msg = LLMMessage(role="assistant", content="How can I help?")
        
        assert msg.role == "assistant"
        assert msg.content == "How can I help?"

    def test_to_dict(self):
        """Test converting message to dictionary."""
        msg = LLMMessage(role="user", content="Test")
        
        result = msg.to_dict()
        
        assert result == {"role": "user", "content": "Test"}
        assert isinstance(result, dict)

    def test_to_dict_system_message(self):
        """Test converting system message to dictionary."""
        msg = LLMMessage(role="system", content="System prompt")
        
        result = msg.to_dict()
        
        assert result == {"role": "system", "content": "System prompt"}


class TestLLMResponse:
    """Tests for LLMResponse class."""

    def test_create_basic_response(self):
        """Test creating a basic response."""
        response = LLMResponse(
            content="Hello!",
            model="gpt-4",
        )
        
        assert response.content == "Hello!"
        assert response.model == "gpt-4"
        assert response.prompt_tokens == 0
        assert response.completion_tokens == 0
        assert response.total_tokens == 0
        assert response.cost_usd == 0.0
        assert response.finish_reason == "stop"

    def test_create_full_response(self):
        """Test creating a response with all fields."""
        response = LLMResponse(
            content="Detailed response",
            model="gpt-4",
            prompt_tokens=50,
            completion_tokens=100,
            total_tokens=150,
            cost_usd=0.005,
            finish_reason="length",
        )
        
        assert response.content == "Detailed response"
        assert response.model == "gpt-4"
        assert response.prompt_tokens == 50
        assert response.completion_tokens == 100
        assert response.total_tokens == 150
        assert response.cost_usd == 0.005
        assert response.finish_reason == "length"

    def test_is_complete_stop(self):
        """Test is_complete property with stop reason."""
        response = LLMResponse(
            content="Complete",
            model="gpt-4",
            finish_reason="stop",
        )
        
        assert response.is_complete is True

    def test_is_complete_length(self):
        """Test is_complete property with length reason."""
        response = LLMResponse(
            content="Truncated",
            model="gpt-4",
            finish_reason="length",
        )
        
        assert response.is_complete is False

    def test_is_complete_cache_hit(self):
        """Test is_complete property with cache hit."""
        response = LLMResponse(
            content="Cached",
            model="gpt-4",
            finish_reason="cache_hit",
        )
        
        assert response.is_complete is True


class TestLLMProvider:
    """Tests for LLMProvider class."""

    def test_create_provider_default(self):
        """Test creating provider with defaults."""
        provider = LLMProvider()
        
        assert provider.model == "ollama/llama3:latest"
        assert provider.api_base is None
        assert provider.api_key is None
        assert provider.temperature == 0.7
        assert provider.max_tokens == 2048
        assert provider.timeout == 120

    def test_create_provider_custom_options(self):
        """Test creating provider with custom options."""
        provider = LLMProvider(
            model="gpt-4",
            api_base="http://localhost:11434",
            api_key="sk-test",
            temperature=0.5,
            max_tokens=1024,
            timeout=60,
        )
        
        assert provider.model == "gpt-4"
        assert provider.api_base == "http://localhost:11434"
        assert provider.api_key == "sk-test"
        assert provider.temperature == 0.5
        assert provider.max_tokens == 1024
        assert provider.timeout == 60

    def test_chat_sync(self):
        """Test synchronous chat."""
        provider = LLMProvider(model="ollama/llama3:latest")
        
        messages = [LLMMessage(role="user", content="Hello")]
        
        with patch('piranha.llm_provider.completion') as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Hi there!"))],
                usage=MagicMock(prompt_tokens=10, completion_tokens=20, total_tokens=30),
                model="ollama/llama3:latest",
            )
            
            with patch('piranha.llm_provider.litellm.cost_calculator.completion_cost', return_value=0.001):
                response = provider.chat(messages)
                
                assert response.content == "Hi there!"
                assert response.prompt_tokens == 10
                assert response.completion_tokens == 20
                assert response.total_tokens == 30
                assert response.cost_usd == 0.001

    def test_chat_with_custom_temperature(self):
        """Test chat with custom temperature."""
        provider = LLMProvider(model="gpt-4", temperature=0.3)

        messages = [LLMMessage(role="user", content="Test")]

        with patch('piranha.llm_provider.completion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
            mock_response.usage = MagicMock(prompt_tokens=5, completion_tokens=10, total_tokens=15)
            mock_response.model = "gpt-4"
            mock_completion.return_value = mock_response

            with patch('piranha.llm_provider.litellm.cost_calculator.completion_cost', return_value=0.0005):
                # Note: temperature is passed via kwargs but extracted and passed explicitly by chat()
                result = provider.chat(messages)

                # Verify default temperature was passed
                mock_completion.assert_called_once()
                call_kwargs = mock_completion.call_args[1]
                assert call_kwargs['temperature'] == 0.3

    def test_chat_streaming(self):
        """Test streaming chat."""
        provider = LLMProvider(model="ollama/llama3:latest")
        
        messages = [LLMMessage(role="user", content="Stream me")]
        
        def mock_chunk_generator():
            chunks = [
                MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content=" "))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content="World"))]),
            ]
            return iter(chunks)
        
        with patch('piranha.llm_provider.completion', return_value=mock_chunk_generator()):
            stream = provider.chat(messages, stream=True)
            
            chunks = list(stream)
            assert chunks == ["Hello", " ", "World"]

    @pytest.mark.asyncio
    async def test_chat_async(self):
        """Test asynchronous chat."""
        provider = LLMProvider(model="gpt-4")
        
        messages = [LLMMessage(role="user", content="Async hello")]
        
        with patch('piranha.llm_provider.acompletion', new_callable=AsyncMock) as mock_acompletion:
            mock_acompletion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Async hi!"))],
                usage=MagicMock(prompt_tokens=8, completion_tokens=12, total_tokens=20),
                model="gpt-4",
            )
            
            with patch('piranha.llm_provider.litellm.cost_calculator.completion_cost', return_value=0.002):
                response = await provider.chat_async(messages)
                
                assert response.content == "Async hi!"
                assert response.prompt_tokens == 8
                assert response.completion_tokens == 12

    @pytest.mark.asyncio
    async def test_chat_async_streaming(self):
        """Test asynchronous streaming chat."""
        provider = LLMProvider(model="gpt-4")
        
        messages = [LLMMessage(role="user", content="Stream async")]
        
        async def mock_async_generator():
            chunks = [
                MagicMock(choices=[MagicMock(delta=MagicMock(content="Async"))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content=" "))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content="Stream"))]),
            ]
            for chunk in chunks:
                yield chunk
        
        with patch('piranha.llm_provider.acompletion', return_value=mock_async_generator()):
            stream = await provider.chat_async(messages, stream=True)
            
            chunks = []
            async for chunk in stream:
                chunks.append(chunk)
            
            assert chunks == ["Async", " ", "Stream"]

    def test_chat_with_kwargs(self):
        """Test chat with additional kwargs."""
        provider = LLMProvider(model="gpt-4")
        
        messages = [LLMMessage(role="user", content="Test")]
        
        with patch('piranha.llm_provider.completion') as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Response"))],
                usage=MagicMock(prompt_tokens=5, completion_tokens=10, total_tokens=15),
                model="gpt-4",
            )
            
            provider.chat(
                messages,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.3,
            )
            
            call_kwargs = mock_completion.call_args[1]
            assert call_kwargs['top_p'] == 0.9
            assert call_kwargs['frequency_penalty'] == 0.5
            assert call_kwargs['presence_penalty'] == 0.3

    def test_chat_error_handling(self):
        """Test error handling in chat."""
        provider = LLMProvider(model="gpt-4")
        
        messages = [LLMMessage(role="user", content="Test")]
        
        with patch('piranha.llm_provider.completion', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                provider.chat(messages)

    @pytest.mark.asyncio
    async def test_chat_async_error_handling(self):
        """Test error handling in async chat."""
        provider = LLMProvider(model="gpt-4")
        
        messages = [LLMMessage(role="user", content="Test")]
        
        with patch('piranha.llm_provider.acompletion', new_callable=AsyncMock, side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                await provider.chat_async(messages)

    def test_get_available_models(self):
        """Test getting available models."""
        provider = LLMProvider()
        
        with patch('piranha.llm_provider.litellm.model_list', return_value=['gpt-4', 'gpt-3.5-turbo']):
            models = provider.get_available_models()
            
            assert 'gpt-4' in models
            assert 'gpt-3.5-turbo' in models

    def test_get_available_models_empty(self):
        """Test getting available models when list is empty."""
        provider = LLMProvider()
        
        with patch('piranha.llm_provider.litellm.model_list', return_value=None):
            models = provider.get_available_models()
            
            assert models == []


class TestCreateProvider:
    """Tests for create_provider factory function."""

    def test_create_ollama_provider(self):
        """Test creating Ollama provider."""
        provider = create_provider("ollama", "llama3:latest")
        
        assert provider.model == "ollama/llama3:latest"
        assert provider.api_base == "http://localhost:11434"

    def test_create_ollama_provider_custom_base(self):
        """Test creating Ollama provider with custom base."""
        provider = create_provider(
            "ollama",
            "llama3:latest",
            api_base="http://remote-server:11434",
        )
        
        assert provider.model == "ollama/llama3:latest"
        assert provider.api_base == "http://remote-server:11434"

    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        provider = create_provider("openai", "gpt-4", api_key="sk-test")
        
        assert provider.model == "openai/gpt-4"
        assert provider.api_key == "sk-test"

    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider."""
        provider = create_provider("anthropic", "claude-3-5-sonnet", api_key="sk-ant-test")
        
        assert provider.model == "anthropic/claude-3-5-sonnet"
        assert provider.api_key == "sk-ant-test"

    def test_create_gemini_provider(self):
        """Test creating Gemini provider."""
        provider = create_provider("gemini", "gemini-pro", api_key="gemini-key")
        
        assert provider.model == "gemini/gemini-pro"
        assert provider.api_key == "gemini-key"

    def test_create_generic_provider(self):
        """Test creating generic provider."""
        provider = create_provider("custom", "custom-model", api_base="http://custom")
        
        assert provider.model == "custom-model"
        assert provider.api_base == "http://custom"

    def test_create_provider_with_temperature(self):
        """Test creating provider with custom temperature."""
        provider = create_provider(
            "openai",
            "gpt-4",
            temperature=0.3,
            max_tokens=500,
        )
        
        assert provider.temperature == 0.3
        assert provider.max_tokens == 500

    def test_create_provider_with_timeout(self):
        """Test creating provider with custom timeout."""
        provider = create_provider(
            "ollama",
            "llama3:latest",
            timeout=300,
        )
        
        assert provider.timeout == 300


class TestLLMProviderIntegration:
    """Integration tests for LLMProvider."""

    def test_full_conversation_flow(self):
        """Test a full conversation flow."""
        provider = LLMProvider(model="gpt-4")
        
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant"),
            LLMMessage(role="user", content="Hello"),
        ]
        
        with patch('piranha.llm_provider.completion') as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Hi! How can I help?"))],
                usage=MagicMock(prompt_tokens=15, completion_tokens=25, total_tokens=40),
                model="gpt-4",
            )
            
            with patch('piranha.llm_provider.litellm.cost_calculator.completion_cost', return_value=0.002):
                response = provider.chat(messages)
                
                assert response.content == "Hi! How can I help?"
                assert response.model == "gpt-4"
                assert response.total_tokens == 40

    def test_multi_turn_conversation(self):
        """Test multi-turn conversation."""
        provider = LLMProvider(model="gpt-4")
        
        conversation = [
            LLMMessage(role="user", content="What is Python?"),
            LLMMessage(role="assistant", content="Python is a programming language"),
            LLMMessage(role="user", content="Show me an example"),
        ]
        
        with patch('piranha.llm_provider.completion') as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="print('Hello')"))],
                usage=MagicMock(prompt_tokens=30, completion_tokens=10, total_tokens=40),
                model="gpt-4",
            )
            
            with patch('piranha.llm_provider.litellm.cost_calculator.completion_cost', return_value=0.002):
                response = provider.chat(conversation)
                
                assert response.content == "print('Hello')"

    def test_cost_calculation_accuracy(self):
        """Test that cost calculation is accurate."""
        provider = LLMProvider(model="gpt-4")
        
        messages = [LLMMessage(role="user", content="Test")]
        
        with patch('piranha.llm_provider.completion') as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Response"))],
                usage=MagicMock(prompt_tokens=100, completion_tokens=200, total_tokens=300),
                model="gpt-4",
            )
            
            # Mock specific cost
            with patch('piranha.llm_provider.litellm.cost_calculator.completion_cost', return_value=0.012):
                response = provider.chat(messages)
                
                assert response.cost_usd == 0.012
                assert response.prompt_tokens == 100
                assert response.completion_tokens == 200

    def test_empty_response_handling(self):
        """Test handling of empty responses."""
        provider = LLMProvider(model="gpt-4")
        
        messages = [LLMMessage(role="user", content="Test")]
        
        with patch('piranha.llm_provider.completion') as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content=None))],
                usage=MagicMock(prompt_tokens=5, completion_tokens=0, total_tokens=5),
                model="gpt-4",
            )
            
            with patch('piranha.llm_provider.litellm.cost_calculator.completion_cost', return_value=0.0):
                response = provider.chat(messages)
                
                assert response.content == ""

    def test_long_response_handling(self):
        """Test handling of long responses truncated by length."""
        provider = LLMProvider(model="gpt-4")
        
        messages = [LLMMessage(role="user", content="Write a long story")]
        
        with patch('piranha.llm_provider.completion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(finish_reason="length", message=MagicMock(content="Once upon a time..."))]
            mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=2048, total_tokens=2058)
            mock_response.model = "gpt-4"
            mock_completion.return_value = mock_response
            
            with patch('piranha.llm_provider.litellm.cost_calculator.completion_cost', return_value=0.1):
                response = provider.chat(messages)
                
                assert response.finish_reason == "length"
                assert response.is_complete is False
