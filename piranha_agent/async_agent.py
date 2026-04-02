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

from piranha_agent.llm_provider import LLMMessage, LLMProvider, LLMResponse
from piranha_agent.memory import ContextManager, MemoryManager
from piranha_agent.session import Session
from piranha_agent.skill import Skill

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
        permissions: list[str] | None = None,
        allowed_hosts: list[str] | None = None,
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
            permissions: List of agent permissions
            allowed_hosts: List of allowed network hosts
            api_base: API base URL (for Ollama)
            api_key: API key (for cloud providers)
        """
        self.name = name
        self.model = model
        self.description = description
        self.system_prompt = system_prompt
        self.skills = skills or []
        self.permissions = permissions or []
        self.allowed_hosts = allowed_hosts or []
        
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
        """Run a task asynchronously with permission enforcement.
        
        Args:
            task: Task description
            stream: If True, stream the response
            
        Returns:
            LLMResponse or async generator for streaming
        """
        from piranha_agent.skill import agent_allowed_hosts, agent_permissions
        
        # Set agent permissions and allowed hosts for this execution context
        token_perms = agent_permissions.set(self.permissions)
        token_hosts = agent_allowed_hosts.set(self.allowed_hosts)
        
        try:
            # Add user message
            self._messages.append(LLMMessage(role="user", content=task))
            self._context.add_message("user", task)
            
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
            
            # Get relevant memories for context
            memory_context = self._memory.get_context(task, max_tokens=500)
            
            # Call LLM
            if stream:
                return self._stream_response(task, memory_context)
            
            # Build messages with context if available
            messages = self._messages
            if memory_context:
                context_msg = LLMMessage(
                    role="system",
                    content=f"Relevant context from memory:\n{memory_context}"
                )
                messages = [context_msg] + self._messages
                
            response = await self._llm.chat_async(messages)
            
            # Store response
            self._messages.append(LLMMessage(role="assistant", content=response.content))
            self._context.add_message("assistant", response.content)
            
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
        finally:
            # Reset context after execution
            agent_permissions.reset(token_perms)
            agent_allowed_hosts.reset(token_hosts)
    
    async def _stream_response(
        self,
        task: str,
        memory_context: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response token by token."""
        full_response = ""
        
        # Build messages with context if available
        messages = self._messages
        if memory_context:
            context_msg = LLMMessage(
                role="system",
                content=f"Relevant context from memory:\n{memory_context}"
            )
            messages = [context_msg] + self._messages
        
        async for chunk in self._llm.chat_async(messages, stream=True):
            full_response += chunk
            yield chunk
        
        # Store complete response
        self._messages.append(LLMMessage(role="assistant", content=full_response))
        self._context.add_message("assistant", full_response)

        # Record event with complete token and cost information
        response = LLMResponse(
            content=full_response,
            model=self.model,
            prompt_tokens=0,  # Token counts not available in streaming mode
            completion_tokens=0,
            cost_usd=0.0,
            finish_reason="stream",
        )
        self._record_llm_event(response)
    
    def _record_llm_event(self, response: LLMResponse) -> None:
        """Record LLM call in event store."""
        try:
            # The EventStore requires a UUID for agent_id. Since the agent's name
            # may not be a valid UUID, we use the session ID for now, as the 
            # cost reporting and debugging suite relies on valid UUIDs.
            # In a production environment, this should be the agent's unique UUID.
            self._event_store.record_llm_call(
                session_id=self.session.id,
                agent_id=self.session.id,  # Use session ID which is a valid UUID
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
