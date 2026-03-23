"""Session management for Piranha agents."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from piranha_core import EventStore


@dataclass
class Session:
    """A session represents a single conversation/interaction flow.
    
    Sessions group related agent interactions and maintain the event history.
    
    Attributes:
        id: Unique session identifier (UUID)
        created_at: Session creation timestamp
        metadata: Optional session metadata
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
    _event_store: EventStore | None = field(default=None, repr=False)
    
    def __post_init__(self) -> None:
        """Initialize event store if not provided."""
        if self._event_store is None:
            self._event_store = EventStore()
    
    @classmethod
    def create(cls, event_store: EventStore | None = None) -> Session:
        """Create a new session.
        
        Args:
            event_store: Optional event store to use
            
        Returns:
            New Session instance
        """
        session = cls(_event_store=event_store)
        return session
    
    def record_event(
        self,
        agent_id: str,
        event_type: str,
        payload: dict[str, Any],
        parent_event_id: str | None = None,
    ) -> str:
        """Record an event in the session.
        
        Args:
            agent_id: ID of the agent generating the event
            event_type: Type of event
            payload: Event payload data
            parent_event_id: Optional parent event ID
            
        Returns:
            Event ID
        """
        # Use the Rust core EventStore
        event_id = self._event_store.record_llm_call(
            session_id=self.id,
            agent_id=agent_id,
            model="unknown",
            prompt_tokens=0,
            completion_tokens=0,
            cost_usd=0.0,
            cache_hit=False,
            context_event_count=0,
        )
        return event_id
    
    def get_events(self) -> list[dict[str, Any]]:
        """Get all events in the session.
        
        Returns:
            List of event dictionaries
        """
        # Would need to add a method to Rust core for this
        return []
    
    def export_trace(self) -> str:
        """Export the session trace.
        
        Returns:
            JSON trace export
        """
        return self._event_store.export_trace(self.id)
    
    def __str__(self) -> str:
        return f"Session(id={self.id[:8]}..., created={self.created_at.isoformat()})"
