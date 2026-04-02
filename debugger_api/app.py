#!/usr/bin/env python3
"""Piranha Time-Travel Debugger API.

FastAPI backend for the React + React Flow debugger UI.
"""

import json
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from piranha_core import EventStore
from pydantic import BaseModel

app = FastAPI(
    title="Piranha Time-Travel Debugger API",
    description="API for loading traces, visualizing events, and rolling back agent states",
    version="0.1.0",
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request/Response Models
# =============================================================================

class LoadTraceRequest(BaseModel):
    session_id: str
    db_path: str | None = ":memory:"


class LoadTraceResponse(BaseModel):
    trace: dict[str, Any]
    event_count: int
    status: str


class RollbackRequest(BaseModel):
    session_id: str
    agent_id: str
    target_sequence: int
    db_path: str | None = ":memory:"


class RollbackResponse(BaseModel):
    snapshot: dict[str, Any]
    status: str


class EventNode(BaseModel):
    id: str
    sequence: int
    event_type: str
    timestamp: str
    agent_id: str
    parent_event_id: str | None
    payload: dict[str, Any]
    cost_usd: float
    tokens: int


class CostDataPoint(BaseModel):
    sequence: int
    cumulative_cost: float
    event_type: str


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Health check."""
    return {
        "name": "Piranha Time-Travel Debugger API",
        "version": "0.1.0",
        "status": "running",
    }


@app.post("/api/trace/load", response_model=LoadTraceResponse)
async def load_trace(request: LoadTraceRequest):
    """Load trace from event store.
    
    Args:
        session_id: Session UUID
        db_path: Database path (default: in-memory)
        
    Returns:
        Trace data with events and metadata
    """
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    
    try:
        store = EventStore(request.db_path) if request.db_path != ":memory:" else EventStore()
        trace_json = store.export_trace(request.session_id)
        trace = json.loads(trace_json)

        return LoadTraceResponse(
            trace=trace,
            event_count=trace.get("event_count", 0),
            status=f"Loaded {trace.get('event_count', 0)} events",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/api/trace/load")
async def load_trace_get(session_id: str, db_path: str = ":memory:"):
    """Load trace via GET (for browser testing)."""
    return await load_trace(LoadTraceRequest(session_id=session_id, db_path=db_path))


@app.get("/api/trace/{session_id}/events")
async def get_events(session_id: str, db_path: str | None = ":memory:"):
    """Get events for a session as React Flow nodes.
    
    Args:
        session_id: Session UUID
        db_path: Database path
        
    Returns:
        List of nodes and edges for React Flow
    """
    try:
        store = EventStore(db_path) if db_path != ":memory:" else EventStore()
        trace_json = store.export_trace(session_id)
        trace = json.loads(trace_json)
        events = trace.get("events", [])
        
        # Convert to React Flow nodes
        nodes = []
        edges = []
        
        for i, event in enumerate(events):
            node_id = f"event-{event.get('sequence', i)}"
            event_type = event.get("event_type", "Unknown")
            
            # Get payload data for display
            payload = event.get("payload", {})
            cost = payload.get("cost_usd", 0)
            tokens = payload.get("prompt_tokens", 0) + payload.get("completion_tokens", 0)
            
            node = {
                "id": node_id,
                "type": "eventNode",
                "position": {"x": 50, "y": i * 100},
                "data": {
                    "label": f"#{event.get('sequence', i)} {event_type}",
                    "event_type": event_type,
                    "sequence": event.get("sequence", i),
                    "timestamp": event.get("timestamp", ""),
                    "agent_id": event.get("agent_id", "")[:8],
                    "event_id": event.get("id", "")[:8],
                    "payload": payload,
                    "cost_usd": cost,
                    "tokens": tokens,
                },
                "style": get_node_style(event_type),
            }
            nodes.append(node)
            
            # Create edge from parent
            parent_id = event.get("parent_event_id")
            if parent_id:
                edges.append({
                    "id": f"edge-{parent_id[:8]}-{node_id}",
                    "source": f"event-{parent_id}",
                    "target": node_id,
                    "type": "smoothstep",
                    "animated": False,
                    "style": {"stroke": "#666", "strokeWidth": 2},
                })

        return {"nodes": nodes, "edges": edges}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/api/trace/{session_id}/costs")
async def get_costs(session_id: str, db_path: str | None = ":memory:"):
    """Get cost data for timeline chart.
    
    Args:
        session_id: Session UUID
        db_path: Database path
        
    Returns:
        Cost data points for Recharts
    """
    try:
        store = EventStore(db_path) if db_path != ":memory:" else EventStore()
        trace_json = store.export_trace(session_id)
        trace = json.loads(trace_json)
        events = trace.get("events", [])
        
        cost_data = []
        cumulative_cost = 0.0
        
        for event in events:
            payload = event.get("payload", {})
            event_type = event.get("event_type", "")
            cost = payload.get("cost_usd", 0)
            
            if event_type in ["LlmCall", "CacheHit"]:
                cumulative_cost += cost
                
                cost_data.append({
                    "sequence": event.get("sequence", 0),
                    "cost": cost,
                    "cumulative_cost": round(cumulative_cost, 6),
                    "event_type": event_type,
                    "model": payload.get("model", "unknown"),
                })
        
        # Summary
        summary = {
            "total_cost": round(cumulative_cost, 6),
            "llm_calls": sum(1 for e in cost_data if e["event_type"] == "LlmCall"),
            "cache_hits": sum(1 for e in cost_data if e["event_type"] == "CacheHit"),
            "estimated_savings": round(sum(e["cost"] for e in cost_data if e["event_type"] == "CacheHit"), 6),
        }

        return {"data": cost_data, "summary": summary}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/trace/rollback", response_model=RollbackResponse)
async def rollback_trace(request: RollbackRequest):
    """Rollback session to a specific sequence.
    
    Args:
        session_id: Session UUID
        agent_id: Agent UUID
        target_sequence: Sequence number to rollback to
        db_path: Database path
        
    Returns:
        State snapshot at target sequence
    """
    try:
        store = EventStore(request.db_path) if request.db_path != ":memory:" else EventStore()
        snapshot_json = store.rollback_to_sequence(
            request.session_id,
            request.agent_id,
            request.target_sequence,
        )
        # snapshot_json is already a string from Rust, parse it
        if isinstance(snapshot_json, str):
            snapshot = json.loads(snapshot_json)
        else:
            snapshot = snapshot_json

        return RollbackResponse(
            snapshot=snapshot,
            status=f"Rolled back to sequence {request.target_sequence}",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/api/sessions")
async def list_sessions(db_path: str | None = ":memory:"):
    """List all sessions in the database.
    
    Note: This is a simplified implementation.
    In production, you'd query the sessions table.
    """
    return {"sessions": [], "note": "Provide session_id to load traces"}


# =============================================================================
# Helpers
# =============================================================================

def get_node_style(event_type: str) -> dict[str, Any]:
    """Get CSS style for event node based on type."""
    styles = {
        "LlmCall": {
            "background": "#dbeafe",
            "border": "2px solid #3b82f6",
            "color": "#1e40af",
        },
        "CacheHit": {
            "background": "#dcfce7",
            "border": "2px solid #22c55e",
            "color": "#166534",
        },
        "SkillInvoked": {
            "background": "#fef3c7",
            "border": "2px solid #f59e0b",
            "color": "#92400e",
        },
        "SkillCompleted": {
            "background": "#dcfce7",
            "border": "2px solid #22c55e",
            "color": "#166534",
        },
        "GuardrailCheck": {
            "background": "#f3e8ff",
            "border": "2px solid #a855f7",
            "color": "#6b21a8",
        },
        "GuardrailBlocked": {
            "background": "#fee2e2",
            "border": "2px solid #ef4444",
            "color": "#991b1b",
        },
        "AgentSpawn": {
            "background": "#ffe4e6",
            "border": "2px solid #fb7185",
            "color": "#9f1239",
        },
        "AgentCompleted": {
            "background": "#e0e7ff",
            "border": "2px solid #6366f1",
            "color": "#3730a3",
        },
        "AgentFailed": {
            "background": "#fee2e2",
            "border": "2px solid #dc2626",
            "color": "#991b1b",
        },
        "BudgetAlert": {
            "background": "#ffedd5",
            "border": "2px solid #f97316",
            "color": "#9a3412",
        },
    }
    return styles.get(event_type, {
        "background": "#f1f5f9",
        "border": "2px solid #64748b",
        "color": "#334155",
    })


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
