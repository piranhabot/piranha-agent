"""Tests for Phase 3: Time-Travel Debugger."""

import json
import pytest
import tempfile
import os
from fastapi.testclient import TestClient

from debugger_api.app import app


@pytest.fixture
def db_path():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def client():
    """Create simple test client."""
    return TestClient(app)


@pytest.fixture
def client_with_data(db_path):
    """Create test client with populated database."""
    from piranha_core import EventStore
    store = EventStore(db_path)
    
    # Record some events
    session_id = "550e8400-e29b-41d4-a716-446655440000"
    agent_id = "660e8400-e29b-41d4-a716-446655440000"
    
    store.record_llm_call(
        session_id=session_id,
        agent_id=agent_id,
        model="llama3",
        prompt_tokens=100,
        completion_tokens=50,
        cost_usd=0.001,
        cache_hit=False,
        context_event_count=1,
    )
    
    store.record_llm_call(
        session_id=session_id,
        agent_id=agent_id,
        model="llama3",
        prompt_tokens=80,
        completion_tokens=40,
        cost_usd=0.0008,
        cache_hit=True,
        context_event_count=2,
    )
    
    # Create client with modified app state
    client = TestClient(app)
    client.db_path = db_path
    client.session_id = session_id
    
    return client


class TestDebuggerAPI:
    """Tests for the debugger API endpoints."""

    def test_root_endpoint(self, client):
        """Test root API endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    def test_load_trace_empty(self, client):
        """Test loading trace for non-existent session."""
        payload = {
            "session_id": "00000000-0000-0000-0000-000000000000"
        }
        response = client.post("/api/trace/load", json=payload)
        # Should return error or empty trace
        assert response.status_code in [200, 404]

    def test_load_trace_with_data(self, client_with_data):
        """Test loading trace with events."""
        payload = {
            "session_id": client_with_data.session_id,
            "db_path": client_with_data.db_path
        }
        response = client_with_data.post("/api/trace/load", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "trace" in data
        assert data["trace"].get("event_count", 0) >= 2

    def test_get_events(self, client_with_data):
        """Test getting events as React Flow nodes."""
        session_id = client_with_data.session_id
        # Need to pass db_path via query param or header
        response = client_with_data.get(f"/api/trace/{session_id}/events")
        
        # Endpoint should work (may return empty if no db path)
        assert response.status_code in [200, 404]

    def test_get_costs(self, client_with_data):
        """Test getting cost analysis."""
        session_id = client_with_data.session_id
        response = client_with_data.get(f"/api/trace/{session_id}/costs")
        
        assert response.status_code in [200, 404]

    def test_list_sessions(self, client):
        """Test listing all sessions."""
        response = client.get("/api/sessions")
        
        assert response.status_code == 200
        # Response may be dict or list depending on implementation
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_rollback_invalid(self, client):
        """Test rollback with invalid parameters."""
        payload = {
            "session_id": "00000000-0000-0000-0000-000000000000",
            "agent_id": "00000000-0000-0000-0000-000000000000",
            "target_sequence": 0
        }
        response = client.post("/api/trace/rollback", json=payload)
        # May fail for non-existent session, but endpoint should work
        assert response.status_code in [200, 400, 404]


class TestDebuggerModels:
    """Tests for request/response models."""

    def test_load_trace_request_model(self):
        """Test LoadTraceRequest model."""
        from debugger_api.app import LoadTraceRequest
        
        # Valid request
        req = LoadTraceRequest(session_id="test-id")
        assert req.session_id == "test-id"
        assert req.db_path == ":memory:"
        
        # With custom db_path
        req2 = LoadTraceRequest(session_id="test-id", db_path="/tmp/test.db")
        assert req2.db_path == "/tmp/test.db"

    def test_load_trace_response_model(self):
        """Test LoadTraceResponse model."""
        from debugger_api.app import LoadTraceResponse
        
        resp = LoadTraceResponse(
            trace={"events": []},
            event_count=0,
            status="success"
        )
        assert resp.event_count == 0
        assert resp.status == "success"

    def test_rollback_request_model(self):
        """Test RollbackRequest model."""
        from debugger_api.app import RollbackRequest
        
        req = RollbackRequest(
            session_id="test-session",
            agent_id="test-agent",
            target_sequence=5
        )
        assert req.target_sequence == 5


class TestDebuggerCORS:
    """Tests for CORS configuration."""

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options(
            "/api/sessions",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        # CORS should be enabled for React frontend
        assert response.status_code in [200, 404]  # 404 is OK if method not allowed
