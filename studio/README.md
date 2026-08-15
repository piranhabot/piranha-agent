# Piranha Studio

Real-time monitoring and management dashboard for Piranha Agent framework.

## Features

- 🐟 **Real-Time Agent Monitoring** - Live agent status and metrics
- 📊 **Cost Tracking** - Token usage and cost visualization
- 📋 **Task Queue** - Monitor task progress and history
- ⚡ **Live Updates** - WebSocket-based real-time updates
- 📈 **Analytics** - Charts and graphs for insights

## Quick Start

### 1. Start Piranha Studio Backend

```bash
# From Piranha Agent root
python -m piranha_agent.realtime --port 8080
```

Or programmatically:

```python
from piranha_agent import start_monitoring

monitor = start_monitoring(port=8080)
```

### 2. Start Frontend Dashboard

```bash
cd studio
npm install
npm run dev
```

Open http://localhost:3000 in your browser.

## Usage

### Monitor Agents

```python
from piranha_agent import Agent, start_monitoring, monitor_agent

# Start monitoring server
start_monitoring(port=8080)

# Create and monitor agent
agent = Agent(name="my-agent", model="ollama/llama3:latest")
monitor_agent(agent)

# Run tasks - automatically tracked
task = Task(description="Explain quantum computing", agent=agent)
result = task.run()
```

### API Endpoints

A representative subset (see `piranha_agent/realtime.py` for the full
list - there are over 30 `/api/*` routes covering agents, tasks, events,
Wasm, security checks, and more):

| Endpoint | Description |
|----------|-------------|
| `GET /api/agents` | Get all agents |
| `GET /api/agents/{id}` | Get specific agent |
| `GET /api/tasks` | Get all tasks |
| `GET /api/metrics` | Get system metrics |
| `GET /api/events` | Get recent events |
| `GET /api/health` | Health check (no auth required) |
| `WS /ws` | WebSocket for real-time updates (requires a JWT token) |

**Authentication:** every `/api/*` route except `/api/health` requires
credentials - `Authorization: Bearer <jwt>`, `X-API-Key`, or
`X-Demo-Secret`. In a detected development environment with no
`API_KEYS` configured, unauthenticated requests are allowed through as a
convenience; sending a wrong key is always rejected. See
[docs/SECURITY_HARDENING.md](../docs/SECURITY_HARDENING.md) for details.
The dashboard frontend will need to send one of these headers once
`API_KEYS`/JWT is configured for anything beyond local dev.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Piranha Studio                          │
├─────────────────────────────────────────────────────────┤
│  Frontend (React/Next.js)    Backend (FastAPI)          │
│  - Dashboard UI              - REST API                 │
│  - Real-time charts          - WebSocket server         │
│  - Agent management          - State management         │
├─────────────────────────────────────────────────────────┤
│                    Piranha Agent Core                    │
│  - Agent execution                                       │
│  - Task processing                                       │
│  - Event sourcing                                        │
└─────────────────────────────────────────────────────────┘
```

## Development

### Backend

`RealtimeMonitor`'s FastAPI app (`self.app`) is a per-instance attribute,
not a module-level object, so `uvicorn piranha_agent.realtime:app` will
not find anything to import. Run the module's own CLI entry point
instead (it doesn't currently support `--reload`):

```bash
python -m piranha_agent.realtime --port 8080
```

### Frontend

```bash
cd studio
npm install
npm run dev
```

## Screenshots

### Dashboard
- Active agents count
- Task queue status
- Token usage metrics
- Cost tracking

### Agent Details
- Agent status (idle/busy/offline)
- Current task
- Token consumption
- Cost breakdown

### Task History
- Task status timeline
- Success/failure rates
- Performance metrics

## Configuration

### Environment Variables

```bash
# Backend
PIRANHA_HOST=0.0.0.0
PIRANHA_PORT=8080

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## API Reference

### Agent Object

```json
{
  "id": "uuid",
  "name": "my-agent",
  "model": "ollama/llama3:latest",
  "status": "idle",
  "tokens_used": 1234,
  "cost_usd": 0.0012,
  "tasks_completed": 5,
  "last_active": "2026-03-20T12:00:00Z"
}
```

### Task Object

```json
{
  "id": "uuid",
  "description": "Explain quantum computing",
  "status": "completed",
  "agent_id": "uuid",
  "created_at": "2026-03-20T12:00:00Z",
  "completed_at": "2026-03-20T12:01:00Z",
  "tokens_used": 500,
  "cost_usd": 0.0005
}
```

## Troubleshooting

### Can't connect to backend

Make sure the backend server is running:

```bash
python -m piranha_agent.realtime --port 8080
```

If it's running but requests fail with `401 Unauthorized`, the frontend
needs to send valid credentials - see Authentication above.

### Frontend shows no data

Check that agents are registered with the monitor:

```python
from piranha_agent import monitor_agent
monitor_agent(agent)
```

## License

MIT OR Apache-2.0

---

**Built with ❤️ using Next.js + FastAPI**
