#!/usr/bin/env python3
"""Enhanced Multi-Agent Collaboration for Piranha.

Inspired by AutoGen's conversational multi-agent patterns.

Features:
- Role-based agents
- Conversational collaboration
- Task chains
- Shared context
- Automatic monitoring
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from piranha import Agent
from piranha.realtime import RealtimeMonitor, get_monitor


class AgentRole(Enum):
    """Predefined agent roles."""
    RESEARCHER = "researcher"
    WRITER = "writer"
    REVIEWER = "reviewer"
    CODER = "coder"
    TESTER = "tester"
    MANAGER = "manager"
    CRITIC = "critic"
    CUSTOM = "custom"


@dataclass
class ConversationMessage:
    """Message in agent conversation."""
    sender: str
    content: str
    role: str
    timestamp: str = field(default_factory=lambda: "")
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationTask:
    """Task for multi-agent collaboration."""
    id: str
    description: str
    status: str = "pending"
    assigned_roles: list[str] = field(default_factory=list)
    results: list[str] = field(default_factory=list)
    conversation: list[ConversationMessage] = field(default_factory=list)


class MultiAgentCollaboration:
    """Enhanced multi-agent collaboration system.
    
    Similar to AutoGen's group chat but with Piranha's monitoring.
    
    Example:
        from piranha import Agent
        from piranha.collaboration import MultiAgentCollaboration, AgentRole
        
        # Create collaboration
        collab = MultiAgentCollaboration()
        
        # Add agents with roles
        collab.add_agent(
            Agent(name="researcher", model="ollama/llama3:latest"),
            AgentRole.RESEARCHER
        )
        collab.add_agent(
            Agent(name="writer", model="ollama/llama3:latest"),
            AgentRole.WRITER
        )
        
        # Create task
        task_id = collab.create_task("Write article about AI")
        
        # Execute collaboration
        results = await collab.execute_task(task_id)
    """
    
    def __init__(
        self,
        monitor: RealtimeMonitor | None = None,
        max_turns: int = 10,
        auto_monitor: bool = True
    ):
        """Initialize collaboration system.
        
        Args:
            monitor: Real-time monitor (auto-creates if None)
            max_turns: Maximum conversation turns
            auto_monitor: Enable automatic monitoring
        """
        self.agents: dict[str, dict[str, Any]] = {}
        self.tasks: dict[str, CollaborationTask] = {}
        self.max_turns = max_turns
        self.auto_monitor = auto_monitor
        
        # Get or create monitor
        self.monitor = monitor
        if self.monitor is None and self.auto_monitor:
            try:
                self.monitor = get_monitor()
            except Exception:
                self.monitor = None
        
        self.collaboration_log: list[str] = []
    
    def add_agent(self, agent: Agent, role: AgentRole | str, description: str = ""):
        """Add agent with specific role.
        
        Args:
            agent: Agent instance
            role: Agent role (enum or string)
            description: Role description
        """
        role_str = role.value if isinstance(role, AgentRole) else role
        
        self.agents[agent.id] = {
            "agent": agent,
            "role": role_str,
            "description": description or f"Agent with role: {role_str}",
            "status": "idle",
            "tasks_completed": 0,
            "messages_sent": 0
        }
        
        # Register with monitor
        if self.auto_monitor and self.monitor:
            self.monitor.register_agent(
                agent_id=agent.id,
                name=f"{role_str}: {agent.name}",
                model=agent.model
            )
        
        self._log(f"Added {role_str} agent: {agent.name}")
    
    def create_task(
        self,
        description: str,
        agent_roles: list[str] | None = None,
        task_id: str | None = None
    ) -> str:
        """Create collaboration task.
        
        Args:
            description: Task description
            agent_roles: Roles required for task
            task_id: Custom task ID (auto-generated if None)
        
        Returns:
            Task ID
        """
        if task_id is None:
            task_id = f"task-{uuid.uuid4().hex[:8]}"
        
        task = CollaborationTask(
            id=task_id,
            description=description,
            assigned_roles=agent_roles or []
        )
        
        self.tasks[task_id] = task
        
        # Register with monitor
        if self.auto_monitor and self.monitor:
            self.monitor.register_task(task_id, description)
        
        self._log(f"Created task: {description[:50]}")
        
        return task_id
    
    async def execute_task(self, task_id: str) -> list[str]:
        """Execute multi-agent collaboration task.
        
        Args:
            task_id: Task to execute
        
        Returns:
            List of results from each agent
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update status
        task.status = "running"
        self._update_task_status(task_id, "running")
        self._log(f"Executing task: {task_id}")
        
        results = []
        
        # Execute for each required role
        for role in task.assigned_roles:
            # Find agent with matching role
            agent_data = self._find_agent_by_role(role)
            if not agent_data:
                raise ValueError(f"No agent with role: {role}")
            
            agent = agent_data["agent"]
            
            # Update agent status
            self._update_agent_status(agent.id, "busy", task_id)
            
            # Create conversation message
            message = ConversationMessage(
                sender="system",
                content=f"Please execute: {task.description}",
                role="system"
            )
            task.conversation.append(message)
            
            # Execute task (placeholder - would use agent.run in real implementation)
            # In production, this would call agent.run() with the task
            result = f"[{agent_data['role']}] Completed: {task.description}"
            results.append(result)
            
            # Add result to conversation
            result_message = ConversationMessage(
                sender=agent.name,
                content=result,
                role=agent_data["role"]
            )
            task.conversation.append(result_message)
            
            # Update agent status
            self._update_agent_status(agent.id, "idle", None)
            agent_data["tasks_completed"] += 1
            agent_data["messages_sent"] += 1
        
        # Mark task complete
        task.status = "completed"
        task.results = results
        self._update_task_status(task_id, "completed")
        self._log(f"Task completed: {task_id}")
        
        return results
    
    async def chat_round(self, task_id: str) -> ConversationMessage:
        """Execute one round of multi-agent chat.
        
        Similar to AutoGen's group chat - agents take turns responding.
        
        Args:
            task_id: Task being discussed
        
        Returns:
            Message from the speaking agent
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Find next agent to speak (round-robin)
        agents_list = list(self.agents.values())
        if not agents_list:
            raise ValueError("No agents in collaboration")
        
        # Simple round-robin for now
        speaker_data = agents_list[len(task.conversation) % len(agents_list)]
        speaker = speaker_data["agent"]
        
        # Update status
        self._update_agent_status(speaker.id, "busy", task_id)
        
        # Create message (placeholder - would use LLM in production)
        message = ConversationMessage(
            sender=speaker.name,
            content=f"[{speaker_data['role']}] My input on: {task.description}",
            role=speaker_data["role"]
        )
        
        task.conversation.append(message)
        
        # Update status
        self._update_agent_status(speaker.id, "idle", None)
        speaker_data["messages_sent"] += 1
        
        return message
    
    def get_conversation_history(self, task_id: str) -> list[dict[str, str]]:
        """Get conversation history for task.
        
        Args:
            task_id: Task ID
        
        Returns:
            List of conversation messages
        """
        task = self.tasks.get(task_id)
        if not task:
            return []
        
        return [
            {
                "sender": msg.sender,
                "content": msg.content,
                "role": msg.role,
                "timestamp": msg.timestamp
            }
            for msg in task.conversation
        ]
    
    def get_collaboration_report(self) -> dict[str, Any]:
        """Get collaboration report.
        
        Returns:
            Report with statistics
        """
        return {
            "total_agents": len(self.agents),
            "total_tasks": len(self.tasks),
            "agents": [
                {
                    "id": data["agent"].id,
                    "name": data["agent"].name,
                    "role": data["role"],
                    "status": data["status"],
                    "tasks_completed": data["tasks_completed"],
                    "messages_sent": data["messages_sent"]
                }
                for data in self.agents.values()
            ],
            "tasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "status": task.status,
                    "roles": task.assigned_roles,
                    "results_count": len(task.results),
                    "conversation_turns": len(task.conversation)
                }
                for task in self.tasks.values()
            ],
            "log": self.collaboration_log[-20:]  # Last 20 entries
        }
    
    def _find_agent_by_role(self, role: str) -> dict[str, Any] | None:
        """Find agent by role."""
        for agent_data in self.agents.values():
            if agent_data["role"] == role:
                return agent_data
        return None
    
    def _update_agent_status(
        self,
        agent_id: str,
        status: str,
        current_task: str | None
    ):
        """Update agent status in monitor."""
        if self.auto_monitor and self.monitor:
            self.monitor.update_agent_status(
                agent_id=agent_id,
                status=status,
                current_task=current_task
            )
    
    def _update_task_status(self, task_id: str, status: str):
        """Update task status in monitor."""
        if self.auto_monitor and self.monitor:
            self.monitor.update_task_status(
                task_id=task_id,
                status=status
            )
    
    def _log(self, message: str):
        """Add to collaboration log."""
        self.collaboration_log.append(message)
        
        # Record event if monitoring
        if self.auto_monitor and self.monitor:
            self.monitor.record_event(
                "collaboration.log",
                {"message": message}
            )


# Convenience functions
def create_collaboration(
    monitor: RealtimeMonitor | None = None,
    auto_monitor: bool = True
) -> MultiAgentCollaboration:
    """Create multi-agent collaboration system.
    
    Args:
        monitor: Real-time monitor
        auto_monitor: Enable automatic monitoring
    
    Returns:
        Collaboration system
    """
    return MultiAgentCollaboration(monitor=monitor, auto_monitor=auto_monitor)


async def run_collaboration(
    agents: list[Agent],
    roles: list[AgentRole | str],
    task_description: str,
    monitor: RealtimeMonitor | None = None
) -> dict[str, Any]:
    """Quick helper to run multi-agent collaboration.
    
    Args:
        agents: List of agents
        roles: List of roles (one per agent)
        task_description: Task to execute
        monitor: Real-time monitor
    
    Returns:
        Collaboration report
    """
    if len(agents) != len(roles):
        raise ValueError("Number of agents must match number of roles")
    
    # Create collaboration
    collab = create_collaboration(monitor=monitor)
    
    # Add agents
    for agent, role in zip(agents, roles, strict=False):
        collab.add_agent(agent, role)
    
    # Create and execute task
    task_id = collab.create_task(
        task_description,
        agent_roles=[r.value if isinstance(r, AgentRole) else r for r in roles]
    )
    
    await collab.execute_task(task_id)
    
    return collab.get_collaboration_report()
