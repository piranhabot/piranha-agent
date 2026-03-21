"""Task definitions for Piranha agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from piranha.agent import Agent, AgentResponse


@dataclass
class Task:
    """A task to be executed by an agent.
    
    Tasks represent work units that agents can execute. They can be:
    - Simple: Single prompt to an agent
    - Complex: Multi-step workflows with dependencies
    - Hierarchical: Parent tasks that spawn sub-tasks
    
    Attributes:
        description: Task description
        agent: Agent to execute the task
        context: Additional context for the task
        expected_output: Description of expected output
        parent: Parent task if this is a sub-task
    """
    
    description: str
    agent: Agent
    context: str = ""
    expected_output: str = ""
    parent: Optional[Task] = None
    _subtasks: list[Task] = field(default_factory=list)
    
    def run(self) -> TaskResult:
        """Execute the task.

        Returns:
            TaskResult with execution outcome
        """
        # Build the full prompt
        prompt = self._build_prompt()

        # Run with the agent
        response = self.agent.run(prompt)

        # Extract result from response (handles both LLMResponse and AgentResponse)
        result_text = response.content if hasattr(response, 'content') else response.result

        return TaskResult(
            task=self,
            success=True,
            result=result_text,
            agent_response=response,
        )
    
    def _build_prompt(self) -> str:
        """Build the full prompt for this task.
        
        Returns:
            Complete prompt string
        """
        parts = []
        
        if self.context:
            parts.append(f"Context: {self.context}")
        
        parts.append(f"Task: {self.description}")
        
        if self.expected_output:
            parts.append(f"Expected Output: {self.expected_output}")
        
        return "\n\n".join(parts)
    
    def add_subtask(self, description: str, **kwargs: Any) -> Task:
        """Add a subtask to this task.
        
        Args:
            description: Subtask description
            **kwargs: Additional Task arguments
            
        Returns:
            Created subtask
        """
        subtask = Task(
            description=description,
            agent=self.agent,
            parent=self,
            **kwargs,
        )
        self._subtasks.append(subtask)
        return subtask
    
    def run_with_subtasks(self) -> TaskResult:
        """Run the task with all subtasks.
        
        Returns:
            TaskResult with all outcomes
        """
        results = []
        
        # Run subtasks first
        for subtask in self._subtasks:
            result = subtask.run()
            results.append(result)
        
        # Then run main task
        main_result = self.run()
        main_result.subtask_results = results
        
        return main_result


@dataclass
class TaskResult:
    """Result of a task execution.
    
    Attributes:
        task: The task that was executed
        success: Whether execution succeeded
        result: The result text
        error: Error message if failed
        agent_response: Full agent response
        subtask_results: Results from subtasks
    """
    
    task: Task
    success: bool
    result: str
    error: Optional[str] = None
    agent_response: Optional[AgentResponse] = None
    subtask_results: list[TaskResult] = field(default_factory=list)
    
    @property
    def is_cached(self) -> bool:
        """Check if result was from cache."""
        return self.agent_response.cache_hit if self.agent_response else False
    
    def __str__(self) -> str:
        status = "✓" if self.success else "✗"
        return f"[{status}] {self.result}"
