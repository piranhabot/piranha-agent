#!/usr/bin/env python3
"""Enhanced Multi-Agent Collaboration for Piranha.

Inspired by AutoGen's conversational multi-agent patterns.

Features:
- Role-based agents
- Conversational collaboration
- Task chains
- Shared context
- Shared Message Bus
- Shared State (Whiteboard)
- Automatic monitoring
"""

from __future__ import annotations

import uuid
import inspect
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Protocol, runtime_checkable, cast

from piranha_agent import Agent
from piranha_agent.realtime import RealtimeMonitor, get_monitor


@runtime_checkable
class SupportsCollaboration(Protocol):
    """Protocol for agents that can participate in collaboration.
    
    Agents implementing this protocol are expected to expose shared
    communication and state attributes used by the collaboration system.
    """
    message_bus: MessageBus
    shared_state: SharedState


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
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
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


class MessageBus:
    """Shared message bus for asynchronous agent communication."""
    
    def __init__(self):
        self._topics: dict[str, list[Callable]] = defaultdict(list)
        self._history: list[dict[str, Any]] = []
    
    def publish(self, topic: str, sender: str, message: Any):
        """Publish a message to a topic."""
        event = {
            "topic": topic,
            "sender": sender,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self._history.append(event)
        
        for handler in self._topics[topic]:
            try:
                handler(event)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error in bus handler: {e}")
            
    def subscribe(self, topic: str, handler: Callable):
        """Subscribe to a topic."""
        self._topics[topic].append(handler)


class PersistentMessageBus(MessageBus):
    """Persistent message bus backed by SQLite."""
    
    def __init__(self, db_path: str = "swarm_messages.db"):
        super().__init__()
        self.db_path = db_path
        self._init_db()
        self._load_history()
        
    def _init_db(self):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT,
                    sender TEXT,
                    message TEXT,
                    timestamp TEXT
                )
            """)
            
    def _load_history(self):
        import sqlite3
        import json
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT topic, sender, message, timestamp FROM messages ORDER BY id")
            for topic, sender, message, timestamp in cursor:
                self._history.append({
                    "topic": topic,
                    "sender": sender,
                    "message": json.loads(message),
                    "timestamp": timestamp
                })
                
    def publish(self, topic: str, sender: str, message: Any):
        import sqlite3
        import json
        # Save to DB first
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (topic, sender, message, timestamp) VALUES (?, ?, ?, ?)",
                (topic, sender, json.dumps(message), datetime.now().isoformat())
            )
        # Then trigger handlers
        super().publish(topic, sender, message)


class SharedState:
    """Shared data store ('whiteboard') for agents in a collaboration."""
    
    def __init__(self):
        self._data: dict[str, Any] = {}
        
    def set(self, key: str, value: Any):
        """Set a value in shared state."""
        self._data[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from shared state."""
        return self._data.get(key, default)
    
    def get_all(self) -> dict[str, Any]:
        """Get all shared data."""
        return self._data.copy()


class PersistentSharedState(SharedState):
    """Persistent shared data store backed by SQLite."""
    
    def __init__(self, db_path: str = "swarm_state.db"):
        super().__init__()
        self.db_path = db_path
        self._init_db()
        self._load_all()
        
    def _init_db(self):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS shared_state (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
    def _load_all(self):
        import sqlite3
        import json
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT key, value FROM shared_state")
            for key, value in cursor:
                self._data[key] = json.loads(value)
                
    def set(self, key: str, value: Any):
        import sqlite3
        import json
        super().set(key, value)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO shared_state (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, json.dumps(value))
            )


class MultiAgentCollaboration:
    """Enhanced multi-agent collaboration system.
    
    Similar to AutoGen's group chat but with Piranha's monitoring.
    
    Example:
        from piranha_agent import Agent
        from piranha_agent.collaboration import MultiAgentCollaboration, AgentRole
        
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
        
        # Shared Communication and State
        self.message_bus = MessageBus()
        self.shared_state = SharedState()
        
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
        
        # Inject shared components into agent using a typed protocol.
        # This maintains loose coupling while preserving type safety.
        collab_agent = cast(SupportsCollaboration, agent)
        collab_agent.message_bus = self.message_bus
        collab_agent.shared_state = self.shared_state
        
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
            
            # Execute task
            raw_result = agent.run(task.description)
            
            # Handle both sync and async agents
            if inspect.iscoroutine(raw_result):
                response = await raw_result
            else:
                response = raw_result
                
            # Extract content from LLMResponse
            result = response.content if hasattr(response, 'content') else str(response)
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
            
            # Publish to bus
            self.message_bus.publish("task.step_completed", agent.name, result)
        
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
        all_agents_list = list(self.agents.values())
        if not all_agents_list:
            raise ValueError("No agents in collaboration")
        
        # If the task specifies assigned_roles, only consider agents with those roles.
        # Otherwise, fall back to all agents.
        assigned_roles = getattr(task, "assigned_roles", None)
        if assigned_roles:
            eligible_agents = [
                agent_data
                for agent_data in all_agents_list
                if agent_data.get("role") in assigned_roles
            ]
        else:
            eligible_agents = all_agents_list
        
        if not eligible_agents:
            raise ValueError(
                f"No agents available with assigned roles for task {task_id}"
            )
        
        # Simple round-robin among eligible agents
        speaker_data = eligible_agents[len(task.conversation) % len(eligible_agents)]
        speaker = speaker_data["agent"]
        
        # Update status
        self._update_agent_status(speaker.id, "busy", task_id)
        
        # Generate response using the agent
        
        # Build prompt from conversation history
        history = "\n".join([f"{msg.sender}: {msg.content}" for msg in task.conversation[-5:]])
        prompt = f"Previous conversation:\n{history}\n\nTask: {task.description}\n\nPlease provide your input as the {speaker_data['role']}."
        
        raw_result = speaker.run(prompt)
        
        # Handle both sync and async agents
        if inspect.iscoroutine(raw_result):
            response = await raw_result
        else:
            response = raw_result
            
        # Extract content
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Create message
        message = ConversationMessage(
            sender=speaker.name,
            content=content,
            role=speaker_data["role"]
        )
        
        task.conversation.append(message)
        
        # Update status
        self._update_agent_status(speaker.id, "idle", None)
        speaker_data["messages_sent"] += 1
        
        # Publish to bus
        self.message_bus.publish("chat.message_sent", speaker.name, content)
        
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
    for agent, role in zip(agents, roles, strict=True):
        collab.add_agent(agent, role)
    
    # Create and execute task
    task_id = collab.create_task(
        task_description,
        agent_roles=[r.value if isinstance(r, AgentRole) else r for r in roles]
    )
    
    await collab.execute_task(task_id)
    
    return collab.get_collaboration_report()
