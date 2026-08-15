"""Tests for HTTP authentication enforcement on the RealtimeMonitor's API.

authenticate_http_request() (JWT Bearer or X-API-Key, with a dev-mode
bypass) was fully implemented in security.py but never actually called by
any of realtime.py's 35 HTTP routes - only the WebSocket path enforced it.
Every REST endpoint, including mutating/sensitive ones (wasm/execute,
guardrails PUT, memory delete/clear, skills install/uninstall, llm
providers CRUD), had no authentication at all, only rate limiting.

security.py's module-level SECRET_KEY/API_KEYS/_env are resolved once at
import time from the environment, so tests here monkeypatch those
attributes directly rather than os.environ (which wouldn't retroactively
affect an already-imported module).
"""

import piranha_agent.security as security_module
from fastapi.testclient import TestClient
from piranha_agent.realtime import RealtimeMonitor


def _client() -> TestClient:
    monitor = RealtimeMonitor(host="127.0.0.1", port=0)
    return TestClient(monitor.app)


def test_health_check_always_public(monkeypatch):
    monkeypatch.setattr(security_module, "API_KEYS", ["a-real-configured-api-key-value-1234"])
    monkeypatch.setattr(security_module, "_env", "production")
    client = _client()

    response = client.get("/api/health")
    assert response.status_code == 200


def test_dev_mode_with_no_api_keys_allows_unauthenticated_requests(monkeypatch):
    monkeypatch.setattr(security_module, "API_KEYS", [])
    monkeypatch.setattr(security_module, "_env", "development")
    client = _client()

    response = client.get("/api/agents")
    assert response.status_code == 200


def test_production_with_api_keys_configured_rejects_unauthenticated(monkeypatch):
    monkeypatch.setattr(security_module, "API_KEYS", ["a-real-configured-api-key-value-1234"])
    monkeypatch.setattr(security_module, "_env", "production")
    client = _client()

    response = client.get("/api/agents")
    assert response.status_code == 401


def test_production_with_valid_api_key_succeeds(monkeypatch):
    monkeypatch.setattr(security_module, "API_KEYS", ["a-real-configured-api-key-value-1234"])
    monkeypatch.setattr(security_module, "_env", "production")
    client = _client()

    response = client.get("/api/agents", headers={"X-API-Key": "a-real-configured-api-key-value-1234"})
    assert response.status_code == 200


def test_production_with_invalid_api_key_rejected(monkeypatch):
    monkeypatch.setattr(security_module, "API_KEYS", ["a-real-configured-api-key-value-1234"])
    monkeypatch.setattr(security_module, "_env", "production")
    client = _client()

    response = client.get("/api/agents", headers={"X-API-Key": "totally-wrong-key-value-here-1234"})
    assert response.status_code == 401


def test_mutating_endpoints_require_auth_in_production(monkeypatch):
    """Regression test: these were the highest-risk unauthenticated
    routes - code execution and security-config mutation."""
    monkeypatch.setattr(security_module, "API_KEYS", ["a-real-configured-api-key-value-1234"])
    monkeypatch.setattr(security_module, "_env", "production")
    client = _client()

    assert client.post("/api/wasm/execute", json={"code": "x"}).status_code == 401
    assert client.put("/api/guardrails", json={}).status_code == 401
    assert client.delete("/api/memory/clear").status_code == 401
    assert client.delete("/api/cache/clear").status_code == 401


def test_dev_mode_still_rejects_wrong_api_key(monkeypatch):
    """Dev-mode bypass only applies when NO credentials are sent at all -
    an explicitly wrong key must still be rejected even in development."""
    monkeypatch.setattr(security_module, "API_KEYS", ["a-real-configured-api-key-value-1234"])
    monkeypatch.setattr(security_module, "_env", "development")
    client = _client()

    response = client.get("/api/agents", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401
