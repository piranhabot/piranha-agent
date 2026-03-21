"""Async Agent support with concurrent execution.

Provides async/await interface for agents, enabling:
- Concurrent agent execution
- Parallel tool calls
- Streaming responses
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from typing import Any

from piranha_core import EventStore, GuardrailEngine, SemanticCache, SkillRegistry

from piranha.llm_provider import LLMMessage, LLMProvider, LLMResponse
from piranha.session import Session
from piranha.skill import Skill
from piranha.memory import ContextManager, MemoryManager


logger = logging.getLogger(__name__)


class AsyncAgent:
    """Async agent for concurrent execution.
    
    Example:
        agent = AsyncAgent(name="assistant")
        response = await agent.run("Hello!")
        print(response.content)
    """
    
    def __init__(
        self,
        name: str,
        model: str = "ollama/llama3:latest",
        description: str = "",
        system_prompt: str = "",
        skills: list[Skill] | None = None,
        api_base: str | None = None,
        api_key: str | None = None,
    ):
        """Initialize async agent.
        
        Args:
            name: Agent name
            model: LLM model identifier
            description: Agent description
            system_prompt: System prompt for the agent
            skills: List of skills
            api_base: API base URL (for Ollama)
            api_key: API key (for cloud providers)
        """
        self.name = name
        self.model = model
        self.description = description
        self.system_prompt = system_prompt
        self.skills = skills or []
        
        # Initialize components
        self._event_store = EventStore()
        self._skill_registry = SkillRegistry()
        self._guardrail_engine = GuardrailEngine()
        self._semantic_cache = SemanticCache(ttl_hours=24, max_entries=10000)
        self._llm = LLMProvider(
            model=model,
            api_base=api_base,
            api_key=api_key,
        )
        
        # Session management
        self.session = Session.create(self._event_store)

        # Context and memory management
        self._context = ContextManager(system_prompt=system_prompt)
        self._memory = MemoryManager()

        # Conversation history
        self._messages: list[LLMMessage] = []
        if system_prompt:
            self._messages.append(LLMMessage(role="system", content=system_prompt))
        
        # Register skills
        self._register_skills()
    
    def _register_skills(self) -> None:
        """Register skills with the registry."""
        for skill in self.skills:
            self._skill_registry.register_skill(
                skill_id=skill.id,
                name=skill.name,
                description=skill.description,
                parameters_schema=skill.parameters_schema,
                permissions=skill.required_permissions,
                inheritable=skill.inheritable,
            )
    
    def add_skill(self, skill: Skill) -> None:
        """Add a skill to the agent."""
        self.skills.append(skill)
        # Register only the newly added skill for efficiency
        self._skill_registry.register_skill(
            skill_id=skill.id,
            name=skill.name,
            description=skill.description,
            parameters_schema=skill.parameters_schema,
            permissions=skill.required_permissions,
            inheritable=skill.inheritable,
        )

    def add_to_memory(self, content: str, tags: list[str] | None = None) -> None:
        """Add content to agent's memory."""
        self._memory.add(content, tags=tags)

    @property
    def context(self) -> ContextManager:
        """Get the context manager."""
        return self._context

    @property
    def memory(self) -> MemoryManager:
        """Get the memory manager."""
        return self._memory
    
    async def run(
        self,
        task: str,
        stream: bool = False,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        """Run a task asynchronously.
        
        Args:
            task: Task description
            stream: If True, stream the response
            
        Returns:
            LLMResponse or async generator for streaming
        """
        # Add user message
        self._messages.append(LLMMessage(role="user", content=task))
        
        # Check cache
        cache_key = self._semantic_cache.compute_key(
            self.model,
            [m.to_dict() for m in self._messages],
        )
        cached = self._semantic_cache.get(cache_key)
        if cached:
            return LLMResponse(
                content=cached["response"],
                model=cached["model"],
                prompt_tokens=cached["prompt_tokens"],
                completion_tokens=cached["completion_tokens"],
                cost_usd=0.0,
                finish_reason="cache_hit",
            )
        
        # Call LLM
        if stream:
            return self._stream_response(task)
        
        response = await self._llm.chat_async(self._messages)
        
        # Store response
        self._messages.append(LLMMessage(role="assistant", content=response.content))
        
        # Record in event store
        self._record_llm_event(response)
        
        # Cache response
        self._semantic_cache.put(
            key=cache_key,
            response=response.content,
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            cost_usd=response.cost_usd,
        )
        
        return response
    
    async def _stream_response(
        self,
        task: str,
    ) -> AsyncGenerator[str, None]:
        """Stream response token by token."""
        full_response = ""
        
        async for chunk in self._llm.chat_async(self._messages, stream=True):
            full_response += chunk
            yield chunk
        
        # Store complete response
        self._messages.append(LLMMessage(role="assistant", content=full_response))
        
        # Record event
        response = LLMResponse(content=full_response, model=self.model)
        self._record_llm_event(response)
    
    def _record_llm_event(self, response: LLMResponse) -> None:
        """Record LLM call in event store."""
        try:
            self._event_store.record_llm_call(
                session_id=self.session.id,
                agent_id=self.name,  # Use agent name as identifier
                model=response.model,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                cost_usd=response.cost_usd,
                cache_hit=response.finish_reason == "cache_hit",
                context_event_count=len(self._messages),
            )
        except Exception as exc:
            # Non-critical, don't fail the request, but log for observability
            logger.warning(
                "Failed to record LLM call for session '%s', agent '%s': %s",
                self.session.id,
                self.name,
                exc,
                exc_info=True,
            )

    @property
    def session_id(self) -> str:
        """Get session ID."""
        return self.session.id
    
    def get_history(self) -> list[dict[str, str]]:
        """Get conversation history."""
        return [m.to_dict() for m in self._messages]
    
    def clear_history(self) -> None:
        """Clear conversation history, keeping system prompt."""
        if self.system_prompt:
            self._messages = [LLMMessage(role="system", content=self.system_prompt)]
        else:
            self._messages = []
    
    async def chat(self, message: str) -> str:
        """Chat with the agent."""
        response = await self.run(message)
        if isinstance(response, LLMResponse):
            return response.content
        return ""
    
    def get_cost_report(self) -> dict[str, Any]:
        """Get cost report for current session."""
        import json
        report_json = self._event_store.get_cost_report(self.session.id)
        return json.loads(report_json) if isinstance(report_json, str) else report_json


class AgentGroup:
    """Group of agents for concurrent execution.
    
    Example:
        group = AgentGroup([agent1, agent2, agent3])
        results = await group.run_parallel("Same task for all")
    """
    
    def __init__(self, agents: list[AsyncAgent]):
        self.agents = agents
    
    async def run_parallel(
        self,
        task: str,
    ) -> list[LLMResponse]:
        """Run same task on all agents in parallel.
        
        Args:
            task: Task to run
            
        Returns:
            List of responses from each agent
        """
        tasks = [agent.run(task) for agent in self.agents]
        return await asyncio.gather(*tasks)
    
    async def run_sequential(
        self,
        task: str,
    ) -> list[LLMResponse]:
        """Run same task on all agents sequentially.
        
        Args:
            task: Task to run
            
        Returns:
            List of responses from each agent
        """
        results = []
        for agent in self.agents:
            result = await agent.run(task)
            results.append(result)
        return results
    
    async def run_pipeline(
        self,
        initial_task: str,
        transform: Callable[[str, int], str] | None = None,
    ) -> list[LLMResponse]:
        """Run agents in pipeline, each receiving previous output.
        
        Args:
            initial_task: Initial task
            transform: Optional function to transform output between agents
            
        Returns:
            List of responses from each agent
        """
        results = []
        current_input = initial_task
        
        for i, agent in enumerate(self.agents):
            if transform:
                current_input = transform(current_input, i)
            
            result = await agent.run(current_input)
            results.append(result)
            
            if isinstance(result, LLMResponse):
                current_input = result.content
        
        return results
