# Piranha Studio - UI Components Guide

**Version:** 0.4.0  
**Last Updated:** March 2026

---

## 🎨 Complete UI Overview

Piranha Studio now has **multiple UI interfaces** for different purposes:

| UI | Technology | URL | Purpose | Status |
|----|------------|-----|---------|--------|
| **Dashboard** | React/Next.js | http://localhost:3000 | Real-time monitoring | ✅ Complete |
| **Memory Search** | React/Next.js | http://localhost:3000/memory | Semantic memory search | ✅ NEW |
| **Skills** | React/Next.js | http://localhost:3000/skills | Skill management | 🔄 Coming Soon |
| **Debugger** | Gradio | http://localhost:7860 | Time-travel debugging | ✅ Complete |
| **CLI** | Python CLI | Terminal | Command-line interface | ✅ Complete |

---

## 📊 Dashboard (Main Page)

**URL:** http://localhost:3000  
**File:** `studio/src/app/page.tsx`

### Features

- **Metric Cards**
  - Active agents count
  - Task queue status
  - Total tokens used
  - Total cost (USD)

- **Agents List**
  - Real-time status (idle/busy/offline)
  - Token usage per agent
  - Cost per agent
  - Tasks completed

- **Tasks List**
  - Task status (pending/running/completed/failed)
  - Creation time
  - Token usage
  - Cost tracking

- **Cost Chart**
  - Bar chart showing cost per agent
  - Interactive tooltips
  - Real-time updates

### Auto-Refresh

- Updates every 5 seconds automatically
- WebSocket connection for real-time events
- No manual refresh needed

---

## 🔍 Memory Search (NEW!)

**URL:** http://localhost:3000/memory  
**File:** `studio/src/app/memory/page.tsx`

### Features

#### Add Memory
- Text area for memory content
- Tag input (comma-separated)
- Add button to save memory
- Automatic embedding generation

#### Semantic Search
- Search box for natural language queries
- Top-K results (default: 10)
- Similarity score percentage
- Ranked results

#### Memory Management
- View all memories
- Delete individual memories
- Clear all memories
- Access count tracking
- Importance scoring
- Creation timestamp

### Example Usage

```python
from piranha_agent.memory import MemoryManager

# Create memory manager
memory = MemoryManager()

# Add memories
memory.add("Python uses dynamic typing", tags=["programming"])
memory.add("Rust is memory-safe", tags=["programming"])
memory.add("React uses virtual DOM", tags=["frontend"])

# Search
results = memory.search("What is Python?", top_k=3)

for mem, score in results:
    print(f"{mem.content} (score: {score:.2f})")
```

### UI Features

- **Search Results Card**
  - Ranked results (#1, #2, #3...)
  - Match percentage (e.g., "95% match")
  - Memory content
  - Tags
  - Access count
  - Importance score

- **All Memories Card**
  - Complete memory list
  - Creation timestamp
  - Quick delete button
  - Clear all option

---

## 🛠️ Skills Management (Coming Soon)

**URL:** http://localhost:3000/skills  
**Status:** 🔄 In Development

### Planned Features

- Browse 46+ Claude Skills
- Install/uninstall skills
- Community skills marketplace
- Skill usage statistics
- Create custom skills
- Skill performance metrics

---

## 🐛 Time-Travel Debugger (Gradio)

**URL:** http://localhost:7860  
**File:** `piranha/debugger.py`

### Features

- Load session traces
- Event timeline view
- Cost analysis charts
- Event inspection
- Rollback to any state
- Export trace

### Usage

```bash
# Launch debugger
piranha-agent debug

# Or programmatically
python -c "from piranha_agent import create_debugger_ui; create_debugger_ui().launch()"
```

---

## 💻 Command Line Interface (CLI)

**Command:** `piranha`  
**File:** `piranha/cli.py`

### Commands

```bash
# Launch debugger
piranha-agent debug

# Interactive agent
piranha-agent agent

# Version info
piranha version

# Help
piranha --help
```

---

## 🚀 Quick Start

### 1. Start Backend Server

```bash
cd /Users/lakshmana/Desktop/piranha-agent
source .venv/bin/activate
PYTHONPATH=/Users/lakshmana/Desktop/piranha-agent python -m piranha.realtime --port 8080
```

### 2. Start Frontend Dashboard

```bash
cd /Users/lakshmana/Desktop/piranha-agent/studio
npm install
npm run dev
```

### 3. Access UIs

| UI | URL |
|----|-----|
| Dashboard | http://localhost:3000 |
| Memory Search | http://localhost:3000/memory |
| Debugger | http://localhost:7860 |
| API | http://localhost:8080/api |

---

## 📁 File Structure

```
studio/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Main dashboard
│   │   ├── layout.tsx            # Root layout
│   │   └── memory/
│   │       └── page.tsx          # Memory search page
│   └── styles/
│       └── globals.css           # Global styles
├── package.json
├── next.config.js
├── tailwind.config.js
└── tsconfig.json
```

---

## 🎯 Navigation

### From Dashboard

Click navigation links in header:
- **Dashboard** → Main monitoring page
- **Memory Search** → Semantic memory search
- **Skills** → Skill management (coming soon)

### Direct URLs

- Dashboard: http://localhost:3000
- Memory: http://localhost:3000/memory
- API: http://localhost:8080/api/health

---

## 🔧 Customization

### Change Theme

Edit `studio/tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      piranha: {
        50: '#f0f9ff',
        // ... customize colors
      },
    },
  },
}
```

### Add New Page

1. Create `studio/src/app/<page>/page.tsx`
2. Add navigation link in `layout.tsx`
3. Restart dev server

---

## 📊 API Endpoints

### Memory API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/memory` | Get all memories |
| POST | `/api/memory/search` | Search memories |
| POST | `/api/memory` | Add memory |
| DELETE | `/api/memory/{id}` | Delete memory |
| DELETE | `/api/memory/clear` | Clear all |

### Monitoring API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents` | Get all agents |
| GET | `/api/tasks` | Get all tasks |
| GET | `/api/metrics` | Get system metrics |
| GET | `/api/events` | Get recent events |
| WS | `/api/ws` | WebSocket for real-time |

---

## ✅ Current Status

| Component | Status | Completion |
|-----------|--------|------------|
| **Dashboard** | ✅ Complete | 100% |
| **Memory Search** | ✅ Complete | 100% |
| **Skills Marketplace** | 🔄 In Progress | 0% |
| **Agent Configuration** | 🔄 In Progress | 0% |
| **Event Timeline** | ⚠️ Gradio Only | 50% |
| **Mobile App** | ❌ Not Started | 0% |

**Overall Frontend:** 8.5/10 ⬆️

---

## 🎉 Summary

**Piranha Studio is NOT fully CLI!** You now have:

✅ **React/Next.js Dashboard** - Full graphical UI  
✅ **Memory Search Interface** - Semantic search with rankings  
✅ **Gradio Debugger** - Time-travel debugging  
✅ **CLI Commands** - Terminal interface  
✅ **REST API** - Programmatic access  
✅ **WebSocket** - Real-time updates  

**Only missing:**
- Skills marketplace UI (coming soon)
- Agent configuration forms (coming soon)
- Mobile app (low priority)

---

*Last updated: March 2026*  
*Version: 0.4.0*
