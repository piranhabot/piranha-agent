#!/usr/bin/env python3
"""Autonomous Agent Orchestration for Piranha.

This module provides the 'Team' and 'Coordinator' patterns for autonomous 
multi-agent collaboration, similar to Claude Code's agent swarms.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, cast

# Optional dependency for nested event loop support
try:
    import nest_asyncio as _nest_asyncio  # type: ignore[import]
except ImportError:
    _nest_asyncio = None  # type: ignore[assignment]

from piranha_agent.agent import Agent
from piranha_agent.collaboration import (
    AgentRole,
    MessageBus,
    SharedState,
    SupportsCollaboration,
)
from piranha_agent.skill import skill
from piranha_agent.task import Task

logger = logging.getLogger(__name__)


@dataclass
class Team:
    """A team of autonomous agents working together.
    
    Teams provide a shared environment (MessageBus, SharedState) for agents
    to collaborate on complex tasks.
    """
    
    name: str
    coordinator: Agent
    members: dict[str, Agent] = field(default_factory=dict)
    message_bus: MessageBus = field(default_factory=MessageBus)
    shared_state: SharedState = field(default_factory=SharedState)
    active_tasks: dict[str, asyncio.Task] = field(default_factory=dict)
    _team_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Initialize the team and link the coordinator."""
        self._setup_agent(self.coordinator, "coordinator")
        
    def add_member(self, agent: Agent, role: str):
        """Add a member to the team."""
        self._setup_agent(agent, role)
        self.members[agent.id] = agent
        
    def _setup_agent(self, agent: Agent, role: str):
        """Inject shared team environment into an agent."""
        collab_agent = cast(SupportsCollaboration, agent)
        collab_agent.message_bus = self.message_bus
        collab_agent.shared_state = self.shared_state
        
        # Add team-specific system prompt info
        team_info = f"\nYou are part of team '{self.name}' as the '{role}'."
        agent.system_prompt += team_info
        
    def get_member_by_name(self, name: str) -> Agent | None:
        """Find a team member by name."""
        if self.coordinator.name == name:
            return self.coordinator
        for agent in self.members.values():
            if agent.name == name:
                return agent
        return None


class OrchestrationSkillProvider:
    """Provides skills for autonomous agent orchestration."""
    
    def __init__(self, team: Team):
        self.team = team
        
    def get_skills(self) -> list:
        """Get the orchestration skills."""
        import copy
        import uuid
        import functools
        
        # We need to return fresh instances with unique IDs and bound methods
        # to avoid registry conflicts and TypeErrors.
        skills = [
            self.delegate_task,
            self.delegate_parallel_tasks,
            self.wait_for_tasks,
            self.get_team_status,
            self.broadcast_message,
        ]
        
        new_skills = []
        for s in skills:
            # s is a Skill instance because of the @skill decorator
            # s.function is the UNBOUND method of the class
            
            # Create a shallow copy
            new_s = copy.copy(s)
            new_s.id = str(uuid.uuid4())
            
            # Manually bind the function to this instance (self)
            # This ensures that when new_s.function(*args) is called, 
            # 'self' is passed as the first argument.
            new_s.function = functools.partial(s.function, self)
            
            new_skills.append(new_s)
            
        return new_skills
    
    @skill(
        name="delegate_task",
        description="Delegate a sub-task to a specialized team member or create a new one.",
        parameters={
            "type": "object",
            "properties": {
                "agent_name": {"type": "string", "description": "Name of the agent to handle the task"},
                "role": {"type": "string", "description": "Role/Specialty of the agent (if creating new)"},
                "task_description": {"type": "string", "description": "Detailed description of the task"},
                "model": {"type": "string", "description": "LLM model to use (optional)"}
            },
            "required": ["agent_name", "task_description"]
        }
    )
    def delegate_task(self, agent_name: str, task_description: str, role: str = "assistant", model: str | None = None) -> str:
        """Delegate a task to a team member synchronously."""
        agent = self.team.get_member_by_name(agent_name)
        
        if not agent:
            # Create new agent if not found
            logger.info(f"Creating new sub-agent: {agent_name} with role: {role}")
            agent = Agent(
                name=agent_name,
                model=model or self.team.coordinator.model,
                system_prompt=f"You are a specialized agent: {role}."
            )
            self.team.add_member(agent, role)
            
        # Create and run task
        task = Task(description=task_description, agent=agent)
        result = task.run()
        
        # Share result on message bus
        self.team.message_bus.publish(
            topic="task.completed",
            sender=agent_name,
            message={"task": task_description, "result": result.result}
        )
        
        return f"Task completed by {agent_name}. Result: {result.result}"

    @skill(
        name="delegate_parallel_tasks",
        description="Launch multiple sub-tasks in parallel to different agents.",
        parameters={
            "type": "object",
            "properties": {
                "assignments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "agent_name": {"type": "string"},
                            "role": {"type": "string"},
                            "task_description": {"type": "string"}
                        },
                        "required": ["agent_name", "task_description"]
                    }
                }
            },
            "required": ["assignments"]
        }
    )
    def delegate_parallel_tasks(self, assignments: list[dict]) -> str:
        """Delegate multiple tasks to run in the background."""
        task_ids = []
        
        for assignment in assignments:
            agent_name = assignment["agent_name"]
            role = assignment.get("role", "assistant")
            task_desc = assignment["task_description"]
            
            agent = self.team.get_member_by_name(agent_name)
            if not agent:
                agent = Agent(name=agent_name, system_prompt=f"You are a specialized agent: {role}.")
                self.team.add_member(agent, role)
            
            # Use a wrapper to run the task and publish the result
            async def run_and_report(a_name, a_agent, a_task_desc):
                task_obj = Task(description=a_task_desc, agent=a_agent)
                # Note: This is synchronous run inside an async wrapper. 
                # For true non-blocking, we'd need Task.run to be async.
                res = await asyncio.to_thread(task_obj.run)
                self.team.message_bus.publish(
                    topic="task.completed",
                    sender=a_name,
                    message={"task": a_task_desc, "result": res.result}
                )
                return res.result

            # Create an asyncio task
            task_id = f"task-{uuid.uuid4().hex[:8]}"
            async_task = asyncio.create_task(run_and_report(agent_name, agent, task_desc))
            self.team.active_tasks[task_id] = async_task
            task_ids.append(task_id)
            
        return f"Launched {len(task_ids)} tasks in parallel. Task IDs: {', '.join(task_ids)}. Use 'wait_for_tasks' to aggregate results."

    @skill(
        name="wait_for_tasks",
        description="Wait for all parallel tasks to complete and get their results.",
        parameters={
            "type": "object",
            "properties": {
                "task_ids": {"type": "array", "items": {"type": "string"}, "description": "List of task IDs to wait for"}
            },
            "required": ["task_ids"]
        }
    )
    def wait_for_tasks(self, task_ids: list[str]) -> str:
        """Wait for specific parallel tasks to finish."""
        results = []

        async def gather_results():
            for tid in task_ids:
                if tid in self.team.active_tasks:
                    try:
                        res = await self.team.active_tasks[tid]
                        results.append(f"Task {tid}: {res}")
                    except Exception as e:
                        logger.exception("Task %s failed with exception", tid)
                        results.append(f"Task {tid}: Error - {str(e)}")
                    finally:
                        if tid in self.team.active_tasks:
                            del self.team.active_tasks[tid]
                else:
                    results.append(f"Task {tid}: Error - Task not found or already completed.")

        # Handle both running and non-running event loop cases
        try:
            loop = asyncio.get_running_loop()
            # A loop is already running (we're inside async context)
            if _nest_asyncio is None:
                raise RuntimeError(
                    "wait_for_tasks was called while an event loop is already running, "
                    "but the optional 'nest_asyncio' dependency is not installed. "
                    "Install 'nest_asyncio' or call this skill from synchronous code."
                )
            _nest_asyncio.apply()
            loop.run_until_complete(gather_results())
        except RuntimeError:
            # No running event loop; create and run one for this call
            asyncio.run(gather_results())

        return "\n".join(results)

    @skill(
        name="get_team_status",
        description="Get the status of all team members, active parallel tasks, and shared state.",
    )
    def get_team_status(self) -> str:
        """Get team status summary."""
        members = [f"{self.team.coordinator.name} (Coordinator)"]
        for agent in self.team.members.values():
            members.append(f"{agent.name}")
            
        shared_keys = list(self.team.shared_state.get_all().keys())
        active_tids = list(self.team.active_tasks.keys())
        
        return f"""
Team: {self.team.name}
Members: {', '.join(members)}
Active Tasks: {', '.join(active_tids) if active_tids else 'None'}
Shared State Keys: {', '.join(shared_keys) if shared_keys else 'None'}
"""

    @skill(
        name="broadcast_message",
        description="Send a message to all team members via the message bus.",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Message content"}
            },
            "required": ["message"]
        }
    )
    def broadcast_message(self, message: str) -> str:
        """Broadcast a message to the team."""
        self.team.message_bus.publish(
            topic="broadcast",
            sender=self.team.coordinator.name,
            message=message
        )
        return "Message broadcasted to all team members."


def create_orchestrated_team(name: str, coordinator_model: str = "ollama/llama3:latest", is_persistent: bool = False) -> Team:
    """Helper to create a team with an autonomous coordinator."""
    from piranha_agent.skills.git import git_create_isolated_workspace, git_cleanup_workspace
    from piranha_agent.collaboration import PersistentMessageBus, PersistentSharedState
    
    coordinator = Agent(
        name="coordinator",
        model=coordinator_model,
        system_prompt="You are the lead coordinator for a team of autonomous agents. "
                      "Your job is to break down complex requests and delegate them to "
                      "specialized sub-agents using 'delegate_task' or 'delegate_parallel_tasks'."
    )
    
    if is_persistent:
        message_bus = PersistentMessageBus(db_path=f"{name}_messages.db")
        shared_state = PersistentSharedState(db_path=f"{name}_state.db")
        team = Team(name=name, coordinator=coordinator, message_bus=message_bus, shared_state=shared_state)
    else:
        team = Team(name=name, coordinator=coordinator)
    
    # Add orchestration skills to coordinator
    provider = OrchestrationSkillProvider(team)
    for s in provider.get_skills():
        coordinator.add_skill(s)
        
    # Add Git isolation skills
    coordinator.add_skill(git_create_isolated_workspace)
    coordinator.add_skill(git_cleanup_workspace)
        
    return team
