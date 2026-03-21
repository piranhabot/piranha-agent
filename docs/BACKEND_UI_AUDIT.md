# Backend Features vs UI Coverage Audit

**Date:** March 2026  
**Version:** 0.4.0

---

## 📊 Complete Feature Matrix

| Backend Feature | File | API Endpoint | UI Page | Status |
|----------------|------|--------------|---------|--------|
| **Agent Monitoring** | realtime.py | `/api/agents` | Dashboard (/) | ✅ Complete |
| **Task Tracking** | realtime.py | `/api/tasks` | Dashboard (/) | ✅ Complete |
| **Metrics** | realtime.py | `/api/metrics` | Dashboard (/) | ✅ Complete |
| **Events** | realtime.py | `/api/events` | Dashboard (/) | ✅ Complete |
| **Memory Search** | realtime.py | `/api/memory*` | Memory (/memory) | ✅ Complete |
| **Wasm Tracking** | realtime.py | `/api/wasm*` | Wasm (/wasm) | ✅ Complete |
| **WebSocket** | realtime.py | `/api/ws` | All pages | ✅ Complete |
| **Skills List** | skill_registry.rs | ❌ Missing | ❌ Missing | ❌ **MISSING** |
| **Guardrails** | guardrails.rs | ❌ Missing | ❌ Missing | ❌ **MISSING** |
| **Semantic Cache** | semantic_cache.rs | ❌ Missing | ❌ Missing | ❌ **MISSING** |
| **Event Store** | event_store.rs | ❌ Missing | ❌ Missing | ❌ **MISSING** |
| **Cost Reports** | event_store.rs | ❌ Missing | ❌ Missing | ❌ **MISSING** |
| **Trace Export** | session.rs | ❌ Missing | ❌ Missing | ❌ **MISSING** |
| **Rollback** | event_store.rs | ❌ Missing | ❌ Missing | ❌ **MISSING** |
| **Distributed Agents** | distributed_agents.rs | ❌ Missing | ❌ Missing | ❌ **MISSING** |
| **Embeddings** | embeddings.py | ❌ Missing | ❌ Missing | ❌ **MISSING** |
| **Collaboration** | collaboration.py | ❌ Missing | ❌ Missing | ❌ **MISSING** |

---

## ❌ Critical Missing UIs

### 1. Skills Management UI 🔴 HIGH PRIORITY

**Backend:** `rust_core/src/skill_registry.rs`  
**Missing:**
- ❌ API endpoints for skills
- ❌ Skills list page
- ❌ Skill installation UI
- ❌ Skill usage statistics
- ❌ Custom skill creation UI

**Why Important:**
- 46+ Claude Skills available
- Users need to browse/install skills
- No visibility into skill usage

**Priority:** 🔴 **HIGH**

---

### 2. Guardrails Configuration UI 🟡 MEDIUM PRIORITY

**Backend:** `rust_core/src/guardrails.rs`  
**Missing:**
- ❌ Guardrail configuration API
- ❌ Token budget settings
- ❌ Permission management
- ❌ Safety settings UI

**Why Important:**
- Security configuration
- Token budget enforcement
- Permission control

**Priority:** 🟡 **MEDIUM**

---

### 3. Semantic Cache Dashboard 🟡 MEDIUM PRIORITY

**Backend:** `rust_core/src/semantic_cache.rs`  
**Missing:**
- ❌ Cache statistics API
- ❌ Hit/miss ratio display
- ❌ Cache entries viewer
- ❌ Cache clearing UI
- ❌ Savings tracker

**Why Important:**
- 30-50% cost reduction feature
- Users want to see savings
- Cache optimization insights

**Priority:** 🟡 **MEDIUM**

---

### 4. Event Store / Trace Viewer 🟢 LOW PRIORITY

**Backend:** `rust_core/src/event_store.rs`  
**Missing:**
- ❌ Event timeline API
- ❌ Trace viewer UI
- ❌ Event filtering
- ❌ Trace export UI

**Why Important:**
- Debugging aid
- Audit trail
- Compliance

**Priority:** 🟢 **LOW** (Gradio debugger exists)

---

### 5. Cost Analytics Dashboard 🟡 MEDIUM PRIORITY

**Backend:** `event_store.rs` (cost reports)  
**Missing:**
- ❌ Cost breakdown API
- ❌ Spending trends
- ❌ Budget alerts
- ❌ Cost per agent/task

**Why Important:**
- Cost optimization
- Budget management
- ROI tracking

**Priority:** 🟡 **MEDIUM**

---

### 6. Distributed Agents Monitor 🟢 LOW PRIORITY

**Backend:** `distributed_agents.rs`  
**Missing:**
- ❌ Cluster status API
- ❌ Worker management UI
- ❌ Task distribution view
- ❌ Load balancing stats

**Why Important:**
- Multi-agent deployments
- Cluster monitoring

**Priority:** 🟢 **LOW** (niche feature)

---

### 7. Embeddings Configuration 🟢 LOW PRIORITY

**Backend:** `embeddings.py`  
**Missing:**
- ❌ Embedding model selection
- ❌ Model configuration
- ❌ Embedding stats

**Why Important:**
- Model selection
- Performance tuning

**Priority:** 🟢 **LOW**

---

### 8. Collaboration Viewer 🟢 LOW PRIORITY

**Backend:** `collaboration.py`  
**Missing:**
- ❌ Conversation history API
- ❌ Multi-agent chat view
- ❌ Role assignment UI

**Why Important:**
- Multi-agent debugging
- Conversation analysis

**Priority:** 🟢 **LOW**

---

## ✅ What's Already Complete

| Feature | UI Page | Completion |
|---------|---------|------------|
| Agent Monitoring | Dashboard | 100% |
| Task Tracking | Dashboard | 100% |
| Metrics | Dashboard | 100% |
| Memory Search | Memory | 100% |
| Wasm Tracking | Wasm | 100% |
| Real-time Updates | All pages | 100% |
| Health Check | API | 100% |

---

## 🎯 Priority Implementation Plan

### Phase 1: Critical (Week 1-2)

1. **Skills Management UI**
   - Add API endpoints to realtime.py
   - Create `/skills` page
   - Skill browser
   - Installation UI

### Phase 2: Important (Week 3-4)

2. **Semantic Cache Dashboard**
   - Cache statistics API
   - `/cache` page
   - Hit/miss ratios
   - Savings tracker

3. **Guardrails Configuration**
   - Settings API
   - `/settings` page
   - Token budget UI
   - Permission management

### Phase 3: Nice-to-Have (Week 5-6)

4. **Cost Analytics**
   - Cost breakdown API
   - `/costs` page
   - Spending trends
   - Budget alerts

5. **Event Timeline**
   - Event viewer API
   - `/events` page
   - Trace export

### Phase 4: Future (Backlog)

6. **Distributed Agents Monitor**
7. **Embeddings Configuration**
8. **Collaboration Viewer**

---

## 📋 API Endpoints Needed

### Skills API

```python
@self.app.get("/api/skills")
async def get_skills():
    """Get all available skills."""
    pass

@self.app.get("/api/skills/{skill_id}")
async def get_skill(skill_id: str):
    """Get skill details."""
    pass

@self.app.post("/api/skills/{skill_id}/install")
async def install_skill(skill_id: str):
    """Install a skill."""
    pass

@self.app.delete("/api/skills/{skill_id}/uninstall")
async def uninstall_skill(skill_id: str):
    """Uninstall a skill."""
    pass

@self.app.get("/api/skills/stats")
async def get_skill_stats():
    """Get skill usage statistics."""
    pass
```

### Cache API

```python
@self.app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    pass

@self.app.get("/api/cache/entries")
async def get_cache_entries():
    """Get cache entries."""
    pass

@self.app.delete("/api/cache/clear")
async def clear_cache():
    """Clear cache."""
    pass

@self.app.get("/api/cache/savings")
async def get_cache_savings():
    """Get cost savings from cache."""
    pass
```

### Guardrails API

```python
@self.app.get("/api/guardrails")
async def get_guardrails():
    """Get guardrail configuration."""
    pass

@self.app.put("/api/guardrails")
async def update_guardrails(config: dict):
    """Update guardrail configuration."""
    pass

@self.app.get("/api/guardrails/token-budget")
async def get_token_budget():
    """Get token budget settings."""
    pass

@self.app.put("/api/guardrails/token-budget")
async def update_token_budget(budget: dict):
    """Update token budget."""
    pass
```

### Cost Analytics API

```python
@self.app.get("/api/costs/breakdown")
async def get_cost_breakdown():
    """Get cost breakdown by agent/task."""
    pass

@self.app.get("/api/costs/trends")
async def get_cost_trends():
    """Get cost trends over time."""
    pass

@self.app.get("/api/costs/budget")
async def get_budget_status():
    """Get budget status."""
    pass
```

---

## 📊 Current UI Coverage

```
Total Backend Features: 16
Features with UI: 7
Features without UI: 9

Coverage: 44% (7/16)

Critical Missing: 1 (Skills)
Medium Missing: 3 (Cache, Guardrails, Costs)
Low Missing: 5 (Events, Distributed, Embeddings, etc.)
```

---

## 🎯 Recommendation

**Focus on Skills Management UI first** - it's the most critical missing piece:

1. Users have 46+ skills with no way to browse/manage them
2. High visibility feature
3. Relatively easy to implement
4. Big impact on user experience

**Estimated Effort:**
- Skills UI: 2-3 days
- Cache Dashboard: 2 days
- Guardrails: 2 days
- Cost Analytics: 2 days

**Total:** ~1-2 weeks for complete coverage

---

*Last updated: March 2026*  
*Version: 0.4.0*  
*Status: 44% UI Coverage*
