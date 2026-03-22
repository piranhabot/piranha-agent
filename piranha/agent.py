"""Agent implementation for Piranha."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from piranha_core import (
    EventStore,
    GuardrailEngine,
    SemanticCache,
    SkillRegistry,
)

from piranha.llm_provider import LLMMessage, LLMProvider, LLMResponse
from piranha.memory import ContextManager, MemoryManager
from piranha.session import Session
from piranha.skill import Skill


@dataclass
class Agent:
    """An autonomous agent that can execute tasks.
    
    Agents are the primary execution unit in Piranha. They can:
    - Process natural language tasks
    - Use skills/tools to accomplish goals
    - Spawn sub-agents for complex tasks
    - Maintain conversation history
    - Use LiteLLM for 100+ LLM providers
    
    Attributes:
        name: Agent name
        model: LLM model to use (e.g., "ollama/llama3:latest", "gpt-4")
        description: Agent description/purpose
        system_prompt: Custom system prompt
        skills: List of skills available to this agent
        session: Current session
    """
    
    name: str
    model: str = "ollama/llama3:latest"
    description: str = ""
    system_prompt: str = ""
    skills: list[Skill] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    session: Session | None = None
    api_base: str | None = None
    api_key: str | None = None
    _event_store: EventStore | None = field(default=None, repr=False)
    _skill_registry: SkillRegistry | None = field(default=None, repr=False)
    _guardrail_engine: GuardrailEngine | None = field(default=None, repr=False)
    _semantic_cache: SemanticCache | None = field(default=None, repr=False)
    _agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _llm: LLMProvider | None = field(default=None, repr=False)
    _context: ContextManager | None = field(default=None, repr=False)
    _memory: MemoryManager | None = field(default=None, repr=False)
    _messages: list[LLMMessage] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Initialize internal components."""
        if self._event_store is None:
            self._event_store = EventStore()
        if self._skill_registry is None:
            self._skill_registry = SkillRegistry()
        if self._guardrail_engine is None:
            self._guardrail_engine = GuardrailEngine()
        if self._semantic_cache is None:
            self._semantic_cache = SemanticCache(ttl_hours=24, max_entries=10000)
        if self.session is None:
            self.session = Session.create(self._event_store)
        
        # Initialize LLM provider
        self._llm = LLMProvider(
            model=self.model,
            api_base=self.api_base,
            api_key=self.api_key,
        )
        
        # Initialize context and memory
        self._context = ContextManager(system_prompt=self.system_prompt)
        self._memory = MemoryManager()
        
        # Add system prompt to messages
        if self.system_prompt:
            self._messages.append(LLMMessage(role="system", content=self.system_prompt))
        
        # Register skills
        self._register_skills()
    
    def _register_skills(self) -> None:
        """Register all skills with the skill registry."""
        if self._skill_registry is None:
            return
        
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
        """Add a skill to this agent.
        
        Args:
            skill: Skill to add
        """
        self.skills.append(skill)
        self._register_skills()
    
    def run(self, task: str, stream: bool = False) -> LLMResponse | str:
        """Run a task with this agent.
        
        Args:
            task: Task description to execute
            stream: If True, return streaming response (not yet implemented)
            
        Returns:
            LLMResponse with result and metadata
        """
        from piranha.skill import agent_permissions
        
        # Set agent permissions for this execution context
        token = agent_permissions.set(self.permissions)
        
        try:
            # Add user message
            self._messages.append(LLMMessage(role="user", content=task))
            self._context.add_message("user", task)
            
            # Check semantic cache
            cache_key = self._semantic_cache.compute_key(
                self.model,
                [m.to_dict() for m in self._messages],
            )
            cached = self._semantic_cache.get(cache_key)
            if cached:
                return LLMResponse(
                    content=cached["response"],
                    model=cached["model"],
                    cache_hit=True,
                    prompt_tokens=cached["prompt_tokens"],
                    completion_tokens=cached["completion_tokens"],
                    cost_usd=0.0,
                    finish_reason="cache_hit",
                )
            
            # Get relevant memories for context
            memory_context = self._memory.get_context(task, max_tokens=500)
            
            # Build full prompt with context
            if memory_context:
                enhanced_task = f"{task}\n\nRelevant context:\n{memory_context}"
                messages = self._messages.copy()
                messages[-1] = LLMMessage(role="user", content=enhanced_task)
            else:
                messages = self._messages
            
            # Call LLM
            response = self._llm.chat(messages)
            
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
            
            # Store in memory
            self._memory.add(
                content=f"User: {task}\nAssistant: {response.content}",
                tags=["conversation"],
            )
            
            return response
        finally:
            # Reset permissions after execution
            agent_permissions.reset(token)
    
    def add_to_memory(self, content: str, tags: list[str] | None = None) -> None:
        """Add content to agent's long-term memory.
        
        Args:
            content: Content to remember
            tags: Optional tags for categorization
        """
        self._memory.add(content, tags=tags)
    
    def search_memory(self, query: str, top_k: int = 3) -> list[tuple[Memory, float]]:
        """Search agent's long-term memory.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of (memory, score) tuples
        """
        return self._memory.search(query, top_k=top_k)
    
    def chat(self, message: str) -> str:
        """Send a chat message to the agent.
        
        Args:
            message: User message
            
        Returns:
            Agent response text
        """
        response = self.run(message)
        if isinstance(response, LLMResponse):
            return response.content
        return str(response)
    
    def _record_llm_event(self, response: LLMResponse) -> None:
        """Record LLM call in event store."""
        try:
            self._event_store.record_llm_call(
                session_id=self.session.id,
                agent_id=self.id,
                model=response.model,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                cost_usd=response.cost_usd,
                cache_hit=response.finish_reason == "cache_hit",
                context_event_count=len(self._messages),
            )
        except Exception:
            pass  # Non-critical
    
    def get_cost_report(self) -> dict[str, Any]:
        """Get cost report for current session.
        
        Returns:
            Cost report dictionary
        """
        if self.session and self._event_store:
            import json
            report_json = self._event_store.get_cost_report(self.session.id)
            return json.loads(report_json) if isinstance(report_json, str) else report_json
        return {}
    
    def export_trace(self) -> str:
        """Export the session trace.
        
        Returns:
            JSON trace export
        """
        if self.session:
            return self.session.export_trace()
        return "{}"
    
    def get_history(self) -> list[dict[str, str]]:
        """Get conversation history.
        
        Returns:
            List of message dictionaries
        """
        return [m.to_dict() for m in self._messages]
    
    def clear_history(self) -> None:
        """Clear conversation history, keeping system prompt."""
        if self.system_prompt:
            self._messages = [LLMMessage(role="system", content=self.system_prompt)]
        else:
            self._messages = []
        self._context = ContextManager(system_prompt=self.system_prompt)
    
    @property
    def id(self) -> str:
        """Get agent ID."""
        return self._agent_id
    
    @property
    def context(self) -> ContextManager:
        """Get context manager."""
        return self._context
    
    @property
    def memory(self) -> MemoryManager:
        """Get memory manager."""
        return self._memory


@dataclass
class AgentResponse:
    """Response from an agent execution (legacy, use LLMResponse).
    
    Attributes:
        result: The response text
        model: Model used for generation
        cache_hit: Whether response was from cache
        prompt_tokens: Tokens in prompt
        completion_tokens: Tokens in completion
        cost_usd: Cost in USD
    """
    
    result: str
    model: str = ""
    cache_hit: bool = False
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    
    def __str__(self) -> str:
        cache_info = " (cached)" if self.cache_hit else ""
        return f"{self.result}{cache_info}"
