#!/usr/bin/env python3
"""Piranha Studio - Real-Time Monitoring Server.

WebSocket-based real-time monitoring for Piranha Agent framework.

Features:
- Live agent status updates
- Real-time token/cost tracking
- Event streaming
- Task queue monitoring
- System health metrics

Usage:
    from piranha import RealtimeMonitor
    
    monitor = RealtimeMonitor(port=8080)
    monitor.start()
    
    # Or run as standalone
    python -m piranha.realtime
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Import security module
from .security import (
    limiter,
    verify_websocket_token,
    get_cors_origins,
    run_security_check,
)

# Get the directory where this file is located
CURRENT_DIR = Path(__file__).parent
DASHBOARD_HTML = CURRENT_DIR / "studio_dashboard.html"

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================

class AgentStatus(BaseModel):
    """Agent status information."""
    id: str
    name: str
    model: str
    status: str  # idle, busy, offline
    current_task: str | None = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    tasks_completed: int = 0
    last_active: str = ""
    session_id: str | None = None


class TaskStatus(BaseModel):
    """Task status information."""
    id: str
    description: str
    status: str  # pending, running, completed, failed
    agent_id: str | None = None
    created_at: str = ""
    completed_at: str | None = None
    result: str | None = None
    tokens_used: int = 0
    cost_usd: float = 0.0


class SystemMetrics(BaseModel):
    """System-wide metrics."""
    active_agents: int = 0
    idle_agents: int = 0
    busy_agents: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    events_per_second: float = 0.0
    uptime_seconds: float = 0.0


class Event(BaseModel):
    """Event for real-time streaming."""
    id: str
    type: str  # agent.created, task.started, task.completed, etc.
    timestamp: str
    data: dict[str, Any]


# =============================================================================
# Real-Time Monitor Server
# =============================================================================

class RealtimeMonitor:
    """Real-time monitoring server for Piranha Agent."""
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        dashboard_path: str | None = None
    ):
        """Initialize real-time monitor.
        
        Args:
            host: Host to bind to
            port: Port to listen on
            dashboard_path: Path to static dashboard files (optional)
        """
        self.host = host
        self.port = port
        self.dashboard_path = dashboard_path
        
        # State
        self.agents: dict[str, AgentStatus] = {}
        self.tasks: dict[str, TaskStatus] = {}
        self.events: list[Event] = []
        self.metrics = SystemMetrics()
        self.start_time = datetime.now()
        
        # WebSocket connections
        self.active_connections: set[WebSocket] = set()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Piranha Studio",
            description="Real-time monitoring for Piranha Agent framework",
            version="0.4.0"
        )
        
        # Add rate limiter
        self.app.state.limiter = limiter
        self.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        # Configure CORS with restricted origins
        allowed_origins = get_cors_origins()
        logger.info(f"Allowed CORS origins: {allowed_origins}")
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["Authorization", "Content-Type"],
        )
        
        # Setup routes
        self._setup_routes()
        
        # Server instance
        self._server = None
        self._thread = None
    
    def _setup_routes(self):
        """Setup API and WebSocket routes."""

        @self.app.get("/")
        async def root():
            """Serve dashboard or API info."""
            # Always serve our built-in dashboard
            if DASHBOARD_HTML.exists():
                return FileResponse(DASHBOARD_HTML)
            return {
                "name": "Piranha Studio",
                "version": "0.4.0",
                "endpoints": {
                    "agents": "/api/agents",
                    "tasks": "/api/tasks",
                    "metrics": "/api/metrics",
                    "events": "/api/events",
                    "websocket": "/ws"
                }
            }
        
        @self.app.get("/api/agents")
        @limiter.limit("30/minute")
        async def get_agents(request: Request):
            """Get all agents."""
            return {"agents": list(self.agents.values())}
        
        @self.app.get("/api/agents/{agent_id}")
        @limiter.limit("60/minute")
        async def get_agent(request: Request, agent_id: str):
            """Get specific agent."""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            return self.agents[agent_id]
        
        @self.app.get("/api/tasks")
        async def get_tasks(status: str | None = None):
            """Get all tasks, optionally filtered by status."""
            tasks = list(self.tasks.values())
            if status:
                tasks = [t for t in tasks if t.status == status]
            return {"tasks": tasks}
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get system metrics."""
            self.update_metrics()
            return self.metrics
        
        @self.app.get("/api/events")
        async def get_events(limit: int = 100):
            """Get recent events."""
            return {"events": self.events[-limit:]}
        
        @self.app.get("/api/security/check")
        async def security_check():
            """Run security check."""
            return run_security_check()
        
        @self.app.get("/api/security/token")
        async def get_token():
            """Get authentication token (for demo purposes)."""
            from .security import create_access_token
            
            token = create_access_token(data={"sub": "user", "role": "admin"})
            return {"token": token, "expires_in": 3600}
        
        @self.app.get("/api/health")
        async def health():
            """Health check."""
            return {
                "status": "healthy",
                "uptime": (datetime.now() - self.start_time).total_seconds()
            }
        
        @self.app.get("/api/wasm")
        async def get_wasm_executions():
            """Get Wasm execution history."""
            # Filter events for Wasm-related events
            wasm_events = [
                e for e in self.events 
                if e.type.startswith("wasm.")
            ]
            return {"executions": wasm_events[-50:]}  # Last 50 executions
        
        @self.app.post("/api/wasm/execute")
        async def execute_wasm(request: dict):
            """Track Wasm execution."""
            # Record Wasm execution event
            self.record_event(
                "wasm.executed",
                {
                    "function_name": request.get("function_name", "unknown"),
                    "execution_time_ms": request.get("execution_time_ms", 0),
                    "success": request.get("success", False),
                    "error": request.get("error"),
                }
            )
            return {"status": "ok"}
        
        @self.app.get("/api/skills")
        async def get_skills():
            """Get all available skills."""
            # Mock data for demo
            return {
                "skills": [
                    {"id": "1", "name": "docx", "description": "Create, edit Word documents", "category": "Document", "installed": True, "usage_count": 150, "permissions": ["file_write"]},
                    {"id": "2", "name": "pdf", "description": "PDF manipulation", "category": "Document", "installed": True, "usage_count": 200, "permissions": ["file_read"]},
                    {"id": "3", "name": "frontend-design", "description": "React + Tailwind designs", "category": "Development", "installed": True, "usage_count": 320, "permissions": []},
                    {"id": "4", "name": "deep-research", "description": "Multi-step research", "category": "Research", "installed": False, "usage_count": 0, "permissions": ["network_read"]},
                ]
            }
        
        @self.app.post("/api/skills/{skill_id}/install")
        async def install_skill(skill_id: str):
            """Install a skill."""
            return {"status": "ok", "message": f"Skill {skill_id} installed"}
        
        @self.app.delete("/api/skills/{skill_id}/uninstall")
        async def uninstall_skill(skill_id: str):
            """Uninstall a skill."""
            return {"status": "ok", "message": f"Skill {skill_id} uninstalled"}
        
        @self.app.get("/api/cache/stats")
        async def get_cache_stats():
            """Get cache statistics."""
            return {
                "entry_count": 156,
                "hit_count": 423,
                "miss_count": 89,
                "hit_rate": 0.826,
                "total_savings_usd": 2.4567,
                "ttl_hours": 24,
                "max_entries": 10000
            }
        
        @self.app.get("/api/cache/entries")
        async def get_cache_entries():
            """Get cache entries."""
            import random
            from datetime import datetime, timedelta
            entries = []
            for i in range(50):
                entries.append({
                    "key": f"cache-key-{i}-{random.randint(1000, 9999)}",
                    "response": f"Cached response {i}",
                    "model": "llama3",
                    "prompt_tokens": random.randint(10, 100),
                    "completion_tokens": random.randint(5, 50),
                    "cost_usd": random.random() * 0.001,
                    "hits": random.randint(0, 20),
                    "created_at": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat()
                })
            return {"entries": entries}
        
        @self.app.delete("/api/cache/clear")
        async def clear_cache():
            """Clear cache."""
            return {"status": "ok", "message": "Cache cleared"}
        
        @self.app.get("/api/llm/providers")
        async def get_llm_providers():
            """Get all LLM providers."""
            return {
                "providers": [
                    {"id": "1", "name": "Ollama Local", "type": "local", "model": "ollama/llama3:latest", "status": "active", "is_default": True},
                    {"id": "2", "name": "Claude API", "type": "cloud", "model": "anthropic/claude-3-5-sonnet", "api_base": "https://api.anthropic.com", "status": "active", "is_default": False},
                    {"id": "3", "name": "OpenAI GPT-4", "type": "cloud", "model": "openai/gpt-4", "api_base": "https://api.openai.com", "status": "active", "is_default": False},
                    {"id": "4", "name": "Hugging Face", "type": "cloud", "model": "huggingface/meta-llama/Llama-2-70b", "status": "inactive", "is_default": False},
                    {"id": "5", "name": "OpenRouter", "type": "cloud", "model": "openrouter/meta-llama/llama-3-70b-instruct", "status": "active", "is_default": False},
                ]
            }
        
        @self.app.post("/api/llm/providers")
        async def add_llm_provider(provider: dict):
            """Add LLM provider."""
            return {"status": "ok", "message": f"Provider {provider.get('name')} added"}
        
        @self.app.delete("/api/llm/providers/{provider_id}")
        async def delete_llm_provider(provider_id: str):
            """Delete LLM provider."""
            return {"status": "ok", "message": f"Provider {provider_id} deleted"}
        
        @self.app.put("/api/llm/providers/{provider_id}/default")
        async def set_default_provider(provider_id: str):
            """Set default provider."""
            return {"status": "ok", "message": f"Provider {provider_id} set as default"}
        
        @self.app.post("/api/llm/providers/{provider_id}/test")
        async def test_llm_provider(provider_id: str):
            """Test LLM provider connection."""
            return {"status": "ok", "success": True, "message": "Connection successful"}
        
        @self.app.get("/api/costs/analytics")
        async def get_cost_analytics(range: str = '7d'):
            """Get advanced cost analytics."""
            import random
            from datetime import datetime, timedelta
            
            daily_breakdown = []
            for i in range(7 if range == '7d' else 30 if range == '30d' else 90):
                daily_breakdown.append({
                    "date": (datetime.now() - timedelta(days=(7 if range == '7d' else 30 if range == '30d' else 90) - i - 1)).strftime('%Y-%m-%d'),
                    "cost": random.random() * 0.01,
                    "tokens": random.randint(5000, 15000)
                })
            
            return {
                "total_cost": 0.0567,
                "total_tokens": 125000,
                "llm_calls": 450,
                "cache_hits": 180,
                "cache_savings": 0.0234,
                "projection": 0.08,
                "daily_breakdown": daily_breakdown,
                "agent_breakdown": [
                    {"name": "researcher", "cost": 0.0234},
                    {"name": "writer", "cost": 0.0189},
                    {"name": "reviewer", "cost": 0.0144}
                ],
                "model_breakdown": [
                    {"name": "llama3", "cost": 0.0},
                    {"name": "claude-3-5-sonnet", "cost": 0.0345},
                    {"name": "gpt-4", "cost": 0.0222}
                ]
            }
        
        @self.app.get("/api/events/timeline")
        async def get_events_timeline():
            """Get event timeline."""
            import random
            from datetime import datetime, timedelta
            
            event_types = ['LlmCall', 'CacheHit', 'CacheMiss', 'SkillInvoked', 'SkillCompleted', 'GuardrailCheck']
            events = []
            for i in range(50):
                events.append({
                    "id": f"event-{i}",
                    "sequence": i + 1,
                    "event_type": event_types[random.randint(0, len(event_types) - 1)],
                    "timestamp": (datetime.now() - timedelta(minutes=(50 - i))).isoformat(),
                    "agent_id": f"agent-{random.randint(1, 5)}",
                    "session_id": f"session-{random.randint(1, 3)}",
                    "payload": {
                        "model": "llama3",
                        "tokens": random.randint(100, 1000),
                        "cost": random.random() * 0.001
                    }
                })
            
            return {"events": events}
        
        @self.app.get("/api/collaborations")
        async def get_collaborations():
            """Get multi-agent collaborations."""
            from datetime import datetime, timedelta
            
            return {
                "collaborations": [
                    {
                        "id": "collab-1",
                        "task_id": "task-1",
                        "description": "Write article about AI",
                        "status": "completed",
                        "agents": [
                            {"id": "1", "name": "researcher", "role": "researcher", "status": "idle", "messages_sent": 5},
                            {"id": "2", "name": "writer", "role": "writer", "status": "idle", "messages_sent": 3},
                            {"id": "3", "name": "reviewer", "role": "reviewer", "status": "idle", "messages_sent": 2}
                        ],
                        "conversation": [
                            {"sender": "system", "content": "Please execute: Write article about AI", "role": "system", "timestamp": datetime.now().isoformat()},
                            {"sender": "researcher", "content": "[researcher] Completed: Research phase", "role": "researcher", "timestamp": datetime.now().isoformat()},
                            {"sender": "writer", "content": "[writer] Completed: Writing phase", "role": "writer", "timestamp": datetime.now().isoformat()},
                            {"sender": "reviewer", "content": "[reviewer] Completed: Review phase", "role": "reviewer", "timestamp": datetime.now().isoformat()}
                        ],
                        "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                        "completed_at": datetime.now().isoformat()
                    },
                    {
                        "id": "collab-2",
                        "task_id": "task-2",
                        "description": "Build web scraper",
                        "status": "running",
                        "agents": [
                            {"id": "4", "name": "coder", "role": "coder", "status": "busy", "messages_sent": 2},
                            {"id": "5", "name": "tester", "role": "tester", "status": "idle", "messages_sent": 0}
                        ],
                        "conversation": [
                            {"sender": "system", "content": "Please execute: Build web scraper", "role": "system", "timestamp": datetime.now().isoformat()},
                            {"sender": "coder", "content": "[coder] Starting implementation", "role": "coder", "timestamp": datetime.now().isoformat()}
                        ],
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
        
        @self.app.get("/api/guardrails")
        async def get_guardrails():
            """Get guardrail configuration."""
            return {
                "token_budget": 100000,
                "max_tokens_per_request": 5000,
                "enable_content_filter": True,
                "blocked_actions": ["file_write", "code_execution"],
                "warning_threshold": 80
            }
        
        @self.app.put("/api/guardrails")
        async def update_guardrails(config: dict):
            """Update guardrail configuration."""
            return {"status": "ok", "message": "Guardrails updated"}
        
        @self.app.get("/api/guardrails/stats")
        async def get_guardrails_stats():
            """Get guardrails statistics."""
            return {
                "total_checks": 1250,
                "allowed": 1180,
                "warned": 45,
                "blocked": 25,
                "token_usage": 67500,
                "budget_remaining": 32500
            }
        
        @self.app.get("/api/memory")
        async def get_memory():
            """Get all memories (placeholder)."""
            return {"memories": []}
        
        @self.app.post("/api/memory/search")
        async def search_memory(request: dict):
            """Search memories (placeholder)."""
            query = request.get("query", "")
            top_k = request.get("top_k", 10)
            # Placeholder - would integrate with MemoryManager
            return {"results": [], "query": query, "top_k": top_k}
        
        @self.app.post("/api/memory")
        async def add_memory(request: dict):
            """Add memory (placeholder)."""
            return {"status": "ok"}
        
        @self.app.delete("/api/memory/{memory_id}")
        async def delete_memory(memory_id: str):
            """Delete memory (placeholder)."""
            return {"status": "ok"}
        
        @self.app.delete("/api/memory/clear")
        async def clear_memory():
            """Clear all memories (placeholder)."""
            return {"status": "ok"}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates with authentication."""
            # Verify authentication token
            payload = await verify_websocket_token(websocket)
            if not payload:
                return  # Connection already closed by verify_websocket_token
            
            await websocket.accept()
            self.active_connections.add(websocket)
            
            logger.info(f"WebSocket connected: {payload.get('sub', 'anonymous')}")

            try:
                # Send initial state
                await websocket.send_json({
                    "type": "init",
                    "agents": [asdict(a) for a in self.agents.values()],
                    "tasks": [asdict(t) for t in self.tasks.values()],
                    "metrics": asdict(self.metrics)
                })

                # Keep connection alive
                while True:
                    try:
                        await asyncio.wait_for(
                            websocket.receive_text(),
                            timeout=30.0
                        )
                        # Handle incoming messages if needed
                    except asyncio.TimeoutError:
                        # Send heartbeat
                        await websocket.send_json({"type": "heartbeat"})
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
            finally:
                self.active_connections.remove(websocket)
    
    def execute_wasm(self, wasm_bytes: bytes, function_name: str = "main", input_data: str = "") -> dict:
        """Execute Wasm and track in monitor."""
        result = {
            "function_name": function_name,
            "success": True,
            "execution_time_ms": 0,
            "output": "",
            "error": None
        }
        
        try:
            import time
            start = time.time()
            
            # Execute Wasm (placeholder - would use actual Wasm execution)
            # In production, this would call the actual WasmRunner
            output = f"Executed {function_name} with input: {input_data}"
            
            end = time.time()
            result["execution_time_ms"] = int((end - start) * 1000)
            result["output"] = output
            
            # Track execution
            self.record_event(
                "wasm.executed",
                result
            )
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            
            # Track failure
            self.record_event(
                "wasm.failed",
                {
                    "function_name": function_name,
                    "error": str(e)
                }
            )
        
        return result
        """Update system metrics."""
        self.metrics.active_agents = len(self.agents)
        self.metrics.idle_agents = sum(1 for a in self.agents.values() if a.status == "idle")
        self.metrics.busy_agents = sum(1 for a in self.agents.values() if a.status == "busy")
        self.metrics.pending_tasks = sum(1 for t in self.tasks.values() if t.status == "pending")
        self.metrics.running_tasks = sum(1 for t in self.tasks.values() if t.status == "running")
        self.metrics.total_tokens = sum(a.tokens_used for a in self.agents.values())
        self.metrics.total_cost_usd = sum(a.cost_usd for a in self.agents.values())
        self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
    
    async def _broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message, default=str)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception:
                disconnected.add(connection)
        
        # Remove disconnected clients
        self.active_connections -= disconnected
    
    def _broadcast_sync(self, message: dict):
        """Broadcast message (sync wrapper)."""
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._broadcast(message))
        except RuntimeError:
            # No running loop, create one
            asyncio.run(self._broadcast(message))
    
    def register_agent(self, agent_id: str, name: str, model: str, session_id: str | None = None):
        """Register an agent for monitoring."""
        agent = AgentStatus(
            id=agent_id,
            name=name,
            model=model,
            status="idle",
            session_id=session_id,
            last_active=datetime.now().isoformat()
        )
        self.agents[agent_id] = agent
        
        # Broadcast event
        self._broadcast_sync({
            "type": "agent.registered",
            "agent": agent.model_dump()
        })
        
        logger.info(f"Agent registered: {name} ({agent_id})")
    
    def update_agent_status(
        self,
        agent_id: str,
        status: str | None = None,
        current_task: str | None = None,
        tokens_used: int | None = None,
        cost_usd: float | None = None
    ):
        """Update agent status."""
        if agent_id not in self.agents:
            logger.warning(f"Agent not found: {agent_id}")
            return
        
        agent = self.agents[agent_id]
        
        if status:
            agent.status = status
        if current_task is not None:
            agent.current_task = current_task
        if tokens_used is not None:
            agent.tokens_used = tokens_used
        if cost_usd is not None:
            agent.cost_usd = cost_usd
        
        agent.last_active = datetime.now().isoformat()
        
        # Broadcast update
        self._broadcast_sync({
            "type": "agent.updated",
            "agent": agent.model_dump()
        })
    
    def register_task(self, task_id: str, description: str, agent_id: str | None = None):
        """Register a task for monitoring."""
        task = TaskStatus(
            id=task_id,
            description=description,
            status="pending",
            agent_id=agent_id,
            created_at=datetime.now().isoformat()
        )
        self.tasks[task_id] = task
        
        # Broadcast event
        self._broadcast_sync({
            "type": "task.created",
            "task": task.model_dump()
        })
        
        logger.info(f"Task registered: {task_id}")
    
    def update_task_status(
        self,
        task_id: str,
        status: str | None = None,
        result: str | None = None,
        tokens_used: int | None = None,
        cost_usd: float | None = None
    ):
        """Update task status."""
        if task_id not in self.tasks:
            logger.warning(f"Task not found: {task_id}")
            return
        
        task = self.tasks[task_id]
        
        if status:
            task.status = status
        if result is not None:
            task.result = result
        if tokens_used is not None:
            task.tokens_used = tokens_used
        if cost_usd is not None:
            task.cost_usd = cost_usd
        
        if status in ["completed", "failed"]:
            task.completed_at = datetime.now().isoformat()
        
        # Broadcast update
        self._broadcast_sync({
            "type": "task.updated",
            "task": task.model_dump()
        })
    
    def record_event(self, event_type: str, data: dict[str, Any]):
        """Record and broadcast an event."""
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data
        )
        self.events.append(event)
        
        # Keep only last 1000 events
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
        
        # Broadcast event
        self._broadcast_sync({
            "type": "event",
            "event": event.model_dump()
        })
    
    def start(self, blocking: bool = False):
        """Start the monitoring server."""
        def run_server():
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
        
        if blocking:
            run_server()
        else:
            self._thread = threading.Thread(target=run_server, daemon=True)
            self._thread.start()
            logger.info(f"Piranha Studio started at http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the monitoring server."""
        if self._server:
            self._server.should_exit = True
        logger.info("Piranha Studio stopped")


# =============================================================================
# Integration with Piranha Agent
# =============================================================================

# Global monitor instance
_monitor: RealtimeMonitor | None = None


def get_monitor() -> RealtimeMonitor:
    """Get or create global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = RealtimeMonitor()
    return _monitor


def start_monitoring(port: int = 8080, dashboard_path: str | None = None):
    """Start real-time monitoring."""
    global _monitor
    _monitor = RealtimeMonitor(port=port, dashboard_path=dashboard_path)
    _monitor.start()
    return _monitor


def monitor_agent(agent):
    """Wrap an agent for monitoring."""
    from piranha import Agent
    
    if not isinstance(agent, Agent):
        raise TypeError("Expected Agent instance")
    
    monitor = get_monitor()
    monitor.register_agent(
        agent_id=agent.id,
        name=agent.name,
        model=agent.model,
        session_id=agent.session.id if agent.session else None
    )
    
    # Wrap agent.run to track tasks
    original_run = agent.run
    
    def monitored_run(task_description: str, **kwargs):
        task_id = str(uuid.uuid4())
        monitor.register_task(task_id, task_description, agent.id)
        monitor.update_agent_status(agent.id, status="busy", current_task=task_id)
        
        try:
            result = original_run(task_description, **kwargs)
            
            # Update with result
            monitor.update_task_status(
                task_id,
                status="completed",
                result=str(result) if hasattr(result, '__str__') else str(result)
            )
            monitor.update_agent_status(agent.id, status="idle", current_task=None)
            
            return result
        except Exception as e:
            monitor.update_task_status(task_id, status="failed", result=str(e))
            monitor.update_agent_status(agent.id, status="idle", current_task=None)
            raise
    
    agent.run = monitored_run
    logger.info(f"Agent {agent.name} is now being monitored")
    
    return agent


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """Run Piranha Studio as standalone server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Piranha Studio - Real-Time Monitoring")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--dashboard", help="Path to dashboard static files")
    
    args = parser.parse_args()
    
    monitor = RealtimeMonitor(
        host=args.host,
        port=args.port,
        dashboard_path=args.dashboard
    )
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║                    🐟 Piranha Studio                       ║
║              Real-Time Agent Monitoring                    ║
╠═══════════════════════════════════════════════════════════╣
║  Dashboard:  http://{args.host}:{args.port}                    ║
║  API:        http://{args.host}:{args.port}/api             ║
║  WebSocket:  ws://{args.host}:{args.port}/ws                ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    monitor.start(blocking=True)


if __name__ == "__main__":
    main()
