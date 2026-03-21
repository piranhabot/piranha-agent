#!/usr/bin/env python3
"""Generate demo trace data for the Time-Travel Debugger."""

import json
import uuid
from piranha_core import EventStore


def create_demo_trace():
    """Create a demo trace with various event types."""
    
    # Create event store with file-based SQLite
    db_path = "/tmp/piranha_debug.db"
    store = EventStore(db_path)
    
    # Generate IDs
    session_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())
    
    print(f"Session ID: {session_id}")
    print(f"Agent ID: {agent_id}")
    print(f"Database: {db_path}")
    print()
    
    # Record some LLM calls
    print("Creating demo events...")
    
    event1 = store.record_llm_call(
        session_id=session_id,
        agent_id=agent_id,
        model="ollama/llama3:latest",
        prompt_tokens=150,
        completion_tokens=50,
        cost_usd=0.002,
        cache_hit=False,
        context_event_count=0,
    )
    print(f"  Event 1 (LLM Call): {event1[:8]}...")
    
    event2 = store.record_llm_call(
        session_id=session_id,
        agent_id=agent_id,
        model="ollama/llama3:latest",
        prompt_tokens=100,
        completion_tokens=30,
        cost_usd=0.0015,
        cache_hit=False,
        context_event_count=1,
    )
    print(f"  Event 2 (LLM Call): {event2[:8]}...")
    
    event3 = store.record_llm_call(
        session_id=session_id,
        agent_id=agent_id,
        model="ollama/llama3:latest",
        prompt_tokens=80,
        completion_tokens=20,
        cost_usd=0.001,
        cache_hit=True,
        context_event_count=2,
    )
    print(f"  Event 3 (Cache Hit): {event3[:8]}...")
    
    event4 = store.record_llm_call(
        session_id=session_id,
        agent_id=agent_id,
        model="ollama/llama3:latest",
        prompt_tokens=200,
        completion_tokens=100,
        cost_usd=0.003,
        cache_hit=False,
        context_event_count=3,
    )
    print(f"  Event 4 (LLM Call): {event4[:8]}...")
    
    # Export trace
    trace_json = store.export_trace(session_id)
    trace = json.loads(trace_json)
    
    print()
    print(f"✓ Created {trace['event_count']} events")
    print()
    print("To view in debugger:")
    print(f"  1. Start API: python debugger_api/app.py")
    print(f"  2. Start UI: cd debugger_ui && npm run dev")
    print(f"  3. Enter Session ID: {session_id}")
    print(f"  4. Enter Agent ID: {agent_id}")
    print(f"  5. Enter Database Path: {db_path}")
    print()
    
    return session_id, agent_id, db_path


if __name__ == "__main__":
    create_demo_trace()
