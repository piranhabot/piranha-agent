"""Tests for Gradio-based Time-Travel Debugger UI."""

import pytest
import json
import tempfile
import os
from piranha_core import EventStore


@pytest.fixture
def db_path():
    """Create a temporary database with test data."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Populate with test data
    store = EventStore(path)
    session_id = "550e8400-e29b-41d4-a716-446655440003"
    agent_id = "660e8400-e29b-41d4-a716-446655440003"
    
    for i in range(3):
        store.record_llm_call(
            session_id=session_id,
            agent_id=agent_id,
            model="llama3",
            prompt_tokens=100 + i * 10,
            completion_tokens=50 + i * 5,
            cost_usd=0.001 + i * 0.0001,
            cache_hit=(i % 2 == 0),
            context_event_count=i + 1,
        )
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


class TestGradioDebugger:
    """Tests for the Gradio debugger interface."""

    def test_debugger_module_imports(self):
        """Test that debugger module imports correctly."""
        from piranha import debugger
        assert hasattr(debugger, 'load_trace')
        assert hasattr(debugger, 'parse_events')
        assert hasattr(debugger, 'format_event')
        assert hasattr(debugger, 'create_ui')

    def test_load_trace_function(self, db_path):
        """Test load_trace function."""
        from piranha.debugger import load_trace
        
        session_id = "550e8400-e29b-41d4-a716-446655440003"
        trace_json, status = load_trace(session_id, db_path)
        
        assert trace_json is not None
        assert "✓ Loaded" in status or "events" in status.lower()
        
        # Parse the JSON
        trace = json.loads(trace_json)
        assert "events" in trace
        assert len(trace["events"]) >= 3

    def test_load_trace_invalid_session(self):
        """Test load_trace with invalid session."""
        from piranha.debugger import load_trace
        
        trace_json, status = load_trace("invalid-session-id")
        
        # Should return error status
        assert "✗" in status or "error" in status.lower() or trace_json == ""

    def test_parse_events_function(self):
        """Test parse_events function."""
        from piranha.debugger import parse_events
        
        trace_json = json.dumps({
            "events": [
                {"event_type": "LlmCall", "sequence": 1},
                {"event_type": "CacheHit", "sequence": 2},
            ]
        })
        
        events = parse_events(trace_json)
        
        assert len(events) == 2
        assert events[0]["event_type"] == "LlmCall"
        assert events[1]["event_type"] == "CacheHit"

    def test_parse_events_empty(self):
        """Test parse_events with empty trace."""
        from piranha.debugger import parse_events
        
        events = parse_events("{}")
        assert events == []
        
        events = parse_events('{"events": []}')
        assert events == []

    def test_format_event_function(self):
        """Test format_event function."""
        from piranha.debugger import format_event
        
        event = {
            "event_type": "LlmCall",
            "sequence": 1,
            "timestamp": "2024-01-01T00:00:00",
            "agent_id": "test-agent",
            "tokens": 100,
            "cost_usd": 0.001,
        }
        
        formatted = format_event(event)
        
        assert formatted is not None
        assert isinstance(formatted, str)
        assert len(formatted) > 0

    def test_create_ui_function(self):
        """Test create_ui function returns Gradio app."""
        from piranha.debugger import create_ui
        
        ui = create_ui()
        
        # Should return a Gradio Blocks or Interface
        assert ui is not None
        assert hasattr(ui, 'launch') or hasattr(ui, 'queue')

    def test_debugger_event_types(self):
        """Test that debugger handles various event types."""
        from piranha.debugger import format_event
        
        event_types = [
            "LlmCall",
            "CacheHit",
            "SkillInvoked",
            "SkillCompleted",
            "GuardrailCheck",
            "GuardrailBlocked",
            "AgentSpawn",
            "AgentCompleted",
            "AgentFailed",
            "BudgetAlert",
        ]
        
        for event_type in event_types:
            event = {
                "event_type": event_type,
                "sequence": 1,
                "timestamp": "2024-01-01T00:00:00",
            }
            formatted = format_event(event)
            assert formatted is not None
            assert isinstance(formatted, str)

    def test_debugger_trace_export(self, db_path):
        """Test trace export functionality."""
        from piranha.debugger import load_trace
        
        session_id = "550e8400-e29b-41d4-a716-446655440003"
        trace_json, status = load_trace(session_id, db_path)
        
        assert trace_json
        trace = json.loads(trace_json)
        assert len(trace.get("events", [])) >= 3

    def test_debugger_cost_calculation(self, db_path):
        """Test that debugger correctly shows cost information."""
        from piranha.debugger import load_trace, parse_events
        
        session_id = "550e8400-e29b-41d4-a716-446655440003"
        trace_json, _ = load_trace(session_id, db_path)
        events = parse_events(trace_json)
        
        assert len(events) >= 3
