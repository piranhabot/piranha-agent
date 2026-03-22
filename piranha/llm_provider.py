"""LLM Provider integration with LiteLLM.

Supports 100+ LLM providers including:
- Ollama (local)
- OpenAI
- Anthropic
- Google Gemini
- Azure OpenAI
- And more via LiteLLM
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass, field
from typing import Any

import litellm
from litellm import acompletion, completion


@dataclass
class LLMMessage:
    """A message in an LLM conversation."""
    
    role: str  # "system", "user", "assistant"
    content: str
    
    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    """Response from an LLM call."""
    
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    finish_reason: str = "stop"
    raw_response: Any | None = field(default=None, repr=False)
    
    @property
    def is_complete(self) -> bool:
        return self.finish_reason == "stop"


class LLMProvider:
    """LLM provider using LiteLLM for unified interface.
    
    Supports sync and async calls, streaming, and cost tracking.
    
    Example:
        provider = LLMProvider(model="ollama/llama3:latest")
        response = provider.chat("Hello!")
        print(response.content)
    """
    
    def __init__(
        self,
        model: str = "ollama/llama3:latest",
        api_base: str | None = None,
        api_key: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 120,
    ):
        """Initialize LLM provider.
        
        Args:
            model: Model identifier (e.g., "ollama/llama3:latest", "gpt-4")
            api_base: Optional API base URL (for Ollama: http://localhost:11434)
            api_key: Optional API key
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.model = model
        self.api_base = api_base
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # Set LiteLLM defaults
        litellm.set_verbose = False
        litellm.suppress_debug_info = True
    
    def chat(
        self,
        messages: list[LLMMessage],
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse | Generator[str, None, None]:
        """Send a chat request.
        
        Args:
            messages: List of conversation messages
            stream: If True, return a generator for streaming
            **kwargs: Additional LiteLLM arguments
            
        Returns:
            LLMResponse or streaming generator
        """
        message_dicts = [m.to_dict() for m in messages]
        
        response = completion(
            model=self.model,
            messages=message_dicts,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            timeout=kwargs.get("timeout", self.timeout),
            api_base=self.api_base,
            api_key=self.api_key,
            stream=stream,
            **kwargs,
        )
        
        if stream:
            return self._stream_generator(response)
        
        return self._parse_response(response)
    
    async def chat_async(
        self,
        messages: list[LLMMessage],
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        """Send an async chat request.
        
        Args:
            messages: List of conversation messages
            stream: If True, return an async generator
            **kwargs: Additional LiteLLM arguments
            
        Returns:
            LLMResponse or async streaming generator
        """
        message_dicts = [m.to_dict() for m in messages]
        
        response = await acompletion(
            model=self.model,
            messages=message_dicts,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            timeout=kwargs.get("timeout", self.timeout),
            api_base=self.api_base,
            api_key=self.api_key,
            stream=stream,
            **kwargs,
        )
        
        if stream:
            return self._async_stream_generator(response)
        
        return self._parse_response(response)
    
    def _stream_generator(
        self,
        response: Any,
    ) -> Generator[str, None, None]:
        """Generate streaming chunks."""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _async_stream_generator(
        self,
        response: Any,
    ) -> AsyncGenerator[str, None]:
        """Generate async streaming chunks."""
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _parse_response(self, response: Any) -> LLMResponse:
        """Parse LiteLLM response to LLMResponse."""
        choice = response.choices[0]
        usage = response.usage
        
        # Calculate cost
        cost = litellm.cost_calculator.completion_cost(response)
        
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            cost_usd=cost if cost else 0.0,
            finish_reason=choice.finish_reason or "stop",
            raw_response=response,
        )
    
    def get_available_models(self) -> list[str]:
        """Get list of available models from provider.
        
        Note: This is a static list from LiteLLM. For Ollama,
        use the /api/tags endpoint directly.
        """
        return litellm.model_list or []


def create_provider(
    provider_type: str,
    model: str,
    **kwargs: Any,
) -> LLMProvider:
    """Factory function to create LLM providers.
    
    Args:
        provider_type: Provider type ("ollama", "openai", "anthropic", etc.)
        model: Model name
        **kwargs: Provider-specific arguments
        
    Returns:
        Configured LLMProvider
        
    Example:
        ollama = create_provider("ollama", "llama3:latest")
        gpt4 = create_provider("openai", "gpt-4", api_key="sk-...")
    """
    if provider_type == "ollama":
        return LLMProvider(
            model=f"ollama/{model}",
            api_base=kwargs.get("api_base", "http://localhost:11434"),
            **kwargs,
        )
    elif provider_type == "openai":
        return LLMProvider(
            model=f"openai/{model}",
            api_key=kwargs.get("api_key"),
            **kwargs,
        )
    elif provider_type == "anthropic":
        return LLMProvider(
            model=f"anthropic/{model}",
            api_key=kwargs.get("api_key"),
            **kwargs,
        )
    elif provider_type == "gemini":
        return LLMProvider(
            model=f"gemini/{model}",
            api_key=kwargs.get("api_key"),
            **kwargs,
        )
    else:
        # Generic provider
        return LLMProvider(model=model, **kwargs)
