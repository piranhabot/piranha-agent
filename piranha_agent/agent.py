"""Agent implementation for Piranha."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from piranha_core import (
    EventStore,
    GuardrailEngine,
    SemanticCache,
    SkillRegistry,
)

from piranha_agent.llm_provider import LLMMessage, LLMProvider, LLMResponse
from piranha_agent.memory import ContextManager, MemoryManager
from piranha_agent.session import Session
from piranha_agent.skill import Skill

logger = logging.getLogger(__name__)


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
    allowed_hosts: list[str] = field(default_factory=list)
    session: Session | None = None
    api_base: str | None = None
    api_key: str | None = None
    budget_limit: float = 0.0  # $0.0 means unlimited
    total_cost: float = 0.0
    max_history_messages: int = 20  # Trigger compaction after this many messages
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
        
        # Get existing skill IDs to avoid duplicates
        pass  # Skill registry handles duplicates automatically

        for skill in self.skills:
            try:
                self._skill_registry.register_skill(
                    skill_id=skill.id,
                    name=skill.name,
                    description=skill.description,
                    parameters_schema=skill.parameters_schema,
                    permissions=skill.required_permissions,
                    inheritable=skill.inheritable,
                )
            except ValueError as e:
                if "already registered" in str(e):
                    # Skip already registered skills
                    continue
                raise e
    
    def add_skill(self, skill: Skill) -> None:
        """Add a skill to this agent.
        
        Args:
            skill: Skill to add
        """
        self.skills.append(skill)
        self._register_skills()
    
    def compact_history(self) -> None:
        """Compact conversation history by summarizing older messages."""
        if len(self._messages) <= self.max_history_messages:
            return
            
        logger.info(f"Compacting history for agent '{self.name}' ({len(self._messages)} messages)")
        
        # Keep system prompt if it exists at index 0
        start_idx = 1 if self._messages and self._messages[0].role == "system" else 0
        system_prompt = self._messages[0] if start_idx == 1 else None
        
        # We'll summarize the middle part, keeping the last 5 messages for immediate context
        messages_to_summarize = self._messages[start_idx:-5]
        remaining_messages = self._messages[-5:]
        
        if not messages_to_summarize:
            return
            
        summary_prompt = [
            LLMMessage(role="system", content="You are a context compaction assistant. "
                                              "Summarize the following conversation history into a concise "
                                              "paragraph that preserves all key facts, decisions, and task progress."),
            LLMMessage(role="user", content=str([m.to_dict() for m in messages_to_summarize]))
        ]
        
        try:
            # Use a faster/cheaper model for summarization if possible, 
            # but for now use the agent's default model
            response = self._llm.chat(summary_prompt)
            summary_content = response.content or "History summarized."
            
            # Reconstruct history
            new_messages = []
            if system_prompt:
                new_messages.append(system_prompt)
                
            new_messages.append(LLMMessage(
                role="system", 
                content=f"SUMMARY OF PREVIOUS INTERACTION: {summary_content}"
            ))
            new_messages.extend(remaining_messages)
            
            self._messages = new_messages
            logger.info(f"History compacted. New count: {len(self._messages)}")
            
        except Exception as e:
            logger.error(f"Failed to compact history: {e}")

    def run(self, task: str, stream: bool = False, tools: list[dict] | None = None) -> LLMResponse:
        """Run a single-turn task with this agent.
        
        Args:
            task: Task description to execute
            stream: If True, return streaming response (not yet implemented)
            tools: Optional list of tools in LiteLLM/OpenAI format
            
        Returns:
            LLMResponse with result and metadata
        """
        from piranha_agent.skill import agent_allowed_hosts, agent_permissions
        
        # Set agent permissions and allowed hosts for this execution context
        token_perms = agent_permissions.set(self.permissions)
        token_hosts = agent_allowed_hosts.set(self.allowed_hosts)
        
        # Check if context compaction is needed
        self.compact_history()
        
        try:
            # Add user message
            self._messages.append(LLMMessage(role="user", content=task))
            self._context.add_message("user", task)
            
            # Check semantic cache (only if no tools, as tools make it dynamic)
            cache_key = None
            if not tools:
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
            
            # Build messages for LLM
            messages = self._messages.copy()
            if memory_context:
                enhanced_task = f"{task}\n\nRelevant context:\n{memory_context}"
                messages[-1] = LLMMessage(role="user", content=enhanced_task)
            
            # Call LLM
            response = self._llm.chat(messages, tools=tools)
            
            # Update total cost
            self.total_cost += response.cost_usd
            
            # Store response (content might be None if tool_calls exist)
            msg = LLMMessage(role="assistant", content=response.content, tool_calls=response.tool_calls)
            self._messages.append(msg)
            if response.content:
                self._context.add_message("assistant", response.content)
            
            # Record in event store
            self._record_llm_event(response)
            
            # Cache response
            if cache_key and response.content:
                self._semantic_cache.put(
                    key=cache_key,
                    response=response.content,
                    model=response.model,
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    cost_usd=response.cost_usd,
                )
            
            # Store in memory
            if response.content:
                self._memory.add(
                    content=f"User: {task}\nAssistant: {response.content}",
                    tags=["conversation"],
                )
            
            return response
        finally:
            # Reset context after execution
            agent_permissions.reset(token_perms)
            agent_allowed_hosts.reset(token_hosts)

    def run_autonomous(self, task: str, max_iterations: int = 10, verbose: bool = True, plan_first: bool = False) -> str:
        """Run a task autonomously using a Thought-Action-Observation loop.
        
        Args:
            task: Initial user task
            max_iterations: Maximum number of tool-calling turns
            verbose: If True, stream thought process to terminal
            plan_first: If True, force agent to draft a PLAN.md before acting
            
        Returns:
            Final answer from the agent
        """
        import json

        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        
        if plan_first:
            from piranha_agent.skills.planning import draft_plan, get_plan
            self.add_skill(draft_plan)
            self.add_skill(get_plan)
            # Add directive to system prompt for this run
            plan_directive = "\n[PLAN MODE ENABLED] You MUST start by drafting a PLAN.md using the 'draft_plan' skill. " \
                             "Wait for user approval of the plan before executing any other skills."
            
            if self._messages and self._messages[0].role == "system":
                self._messages[0].content += plan_directive
            else:
                self._messages.insert(0, LLMMessage(role="system", content=plan_directive))
        
        # Convert skills to LiteLLM tools format
        tools = []
        for s in self.skills:
            tools.append({
                "type": "function",
                "function": {
                    "name": s.name,
                    "description": s.description,
                    "parameters": s.parameters_schema,
                }
            })
            
        current_task = task
        for i in range(max_iterations):
            # Budget Guardrail Check
            if self.budget_limit > 0.0 and self.total_cost >= self.budget_limit:
                console.print("\n[bold red]💰 BUDGET LIMIT REACHED[/bold red]")
                console.print(f"Current cost: [yellow]${self.total_cost:.4f}[/yellow] / Limit: [green]${self.budget_limit:.4f}[/green]")
                choice = input("Budget exceeded. Increase limit by how much? (e.g. 1.0) or 'exit' to stop: ").lower().strip()
                
                if choice == 'exit' or not choice:
                    return f"Task terminated: Budget limit of ${self.budget_limit} reached."
                
                try:
                    increase = float(choice)
                    self.budget_limit += increase
                    console.print(f"✅ Budget increased. New limit: [green]${self.budget_limit:.4f}[/green]")
                except ValueError:
                    return "Task terminated: Invalid budget increase provided."

            if verbose:
                console.print(f"\n[bold blue]Turn {i+1}/{max_iterations}[/bold blue]")
                console.print(Panel(current_task, title="[bold green]Input[/bold green]", border_style="green"))

            # Run LLM with tools
            response = self.run(current_task, tools=tools if tools else None)
            
            # If no tool calls, we are done
            if not response.tool_calls:
                if verbose:
                    console.print(Panel(response.content or "", title="[bold magenta]Final Answer[/bold magenta]", border_style="magenta"))
                return response.content or "Task completed with no output."
                
            # Process tool calls
            for tool_call in response.tool_calls:
                fn_name = tool_call["function"]["name"]
                fn_args_raw = tool_call["function"]["arguments"]
                
                try:
                    fn_args = json.loads(fn_args_raw)
                except Exception:
                    fn_args = {}
                
                if verbose:
                    console.print(f"[bold yellow]Action:[/bold yellow] calling [cyan]{fn_name}[/cyan] with {fn_args}")
                    
                # Find the skill
                skill = next((s for s in self.skills if s.name == fn_name), None)
                if not skill:
                    result = f"Error: Skill '{fn_name}' not found."
                else:
                    try:
                        # Human-in-the-Loop check
                        if getattr(skill, "requires_confirmation", False):
                            console.print("\n[bold red]⚠️  PERMISSION REQUIRED[/bold red]")
                            console.print(f"Agent wants to run: [cyan]{fn_name}[/cyan]")
                            console.print(f"Arguments: {fn_args}")
                            choice = input("Allow this action? [y/N]: ").lower().strip()
                            if choice != 'y':
                                result = f"User denied execution of skill '{fn_name}'."
                                logger.info(f"User denied execution of skill '{fn_name}' for agent '{self.name}'")
                            else:
                                result = skill(**fn_args)
                        else:
                            # Execute the skill directly
                            result = skill(**fn_args)
                    except Exception as e:
                        result = f"Error executing skill '{fn_name}': {str(e)}"
                
                if verbose:
                    # Truncate long results for display
                    display_result = str(result)
                    if len(display_result) > 500:
                        display_result = display_result[:500] + "... (truncated)"
                    console.print(Panel(display_result, title="[bold cyan]Observation[/bold cyan]", border_style="cyan"))

                # Add tool result to messages
                self._messages.append(LLMMessage(
                    role="tool",
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=fn_name
                ))
            
            # The next turn will just be continuing the conversation with tool results
            current_task = "Please continue based on the tool results above."
            
        return "Error: Maximum iterations reached without a final answer."
    
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
