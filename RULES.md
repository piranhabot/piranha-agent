# Agent Rules and Guidelines

## Overview

This document defines what Piranha agents **must do**, **should do**, and **must NOT do** when executing tasks.

---

## Agent Directives

### Level 1: MUST (Required)

These are hard constraints enforced by the guardrail system:

1. **MUST respect permission boundaries**
   - Cannot invoke skills without explicit authorization
   - Cannot escalate own permissions
   - Cannot access other sessions' data

2. **MUST stay within token budget**
   - GuardrailEngine enforces token limits
   - Exceeding budget triggers block verdict

3. **MUST log all actions**
   - Every skill invocation recorded in EventStore
   - All LLM calls tracked with costs
   - Audit trail cannot be bypassed

4. **MUST terminate gracefully**
   - Cannot run infinite loops
   - Must return result or error
   - Must clean up resources

### Level 2: SHOULD (Recommended)

These are best practices agents follow:

1. **Should use semantic caching**
   - Check cache before making LLM calls
   - Cache responses for future reuse
   - Reduces costs and latency

2. **Should delegate sub-tasks**
   - Spawn sub-agents for complex work
   - Inherit appropriate skills only
   - Maintain clear parent-child boundaries

3. **Should provide clear responses**
   - Format output for readability
   - Include reasoning when helpful
   - Admit uncertainty when present

4. **Should handle errors gracefully**
   - Catch and report errors clearly
   - Suggest alternatives when possible
   - Don't expose internal details

### Level 3: MUST NOT (Forbidden)

These actions are blocked by the system:

1. **MUST NOT bypass security**
   - No unauthorized skill access
   - No permission escalation
   - No cross-session data access

2. **MUST NOT exceed limits**
   - No budget bypass attempts
   - No rate limit circumvention
   - No resource exhaustion

3. **MUST NOT hide actions**
   - No silent failures
   - No unlogged operations
   - No audit trail manipulation

4. **MUST NOT cause harm**
   - No destructive file operations without confirmation
   - No network attacks
   - No spam generation

---

## Guardrail Rules

The GuardrailEngine enforces these rules:

| Rule | Enforcement | Action |
|------|-------------|--------|
| Token budget exceeded | Hard limit | Block |
| Suspicious pending action | Pattern match | Warn/Block |
| Rate limit exceeded | Time window | Block |
| Unauthorized skill | Permission check | Block |

### Guardrail Verdicts

- **allow** - Request proceeds normally
- **warn** - Request proceeds with warning logged
- **block** - Request denied, error returned

---

## Skill Execution Rules

### Before Execution

1. Verify skill is registered
2. Verify agent has permission
3. Check guardrail verdict
4. Log intent to execute

### During Execution

1. Execute within timeout limits
2. Monitor resource usage
3. Handle exceptions

### After Execution

1. Log result (success/failure)
2. Update cumulative tokens
3. Cache if appropriate

---

## Session Isolation

Agents operate within session boundaries:

```
Session A          Session B
┌─────────┐       ┌─────────┐
│ Agent 1 │       │ Agent 2 │
│ Events  │       │ Events  │
│ Cache   │       │ Cache   │
└─────────┘       └─────────┘
     ↓                 ↓
  Separate          Separate
  EventStore        EventStore
```

**Rules:**
- Agents cannot access other sessions' events
- Cache entries are session-scoped
- Skills cannot bridge sessions

---

## Sub-Agent Delegation

When spawning sub-agents:

### Allowed Inheritance

- ✅ Static skills marked `inheritable=True`
- ✅ Explicitly delegated dynamic skills
- ✅ Parent's session context (read-only)

### Forbidden Inheritance

- ❌ Skills with `inheritable=False`
- ❌ Parent's permissions (must be re-granted)
- ❌ Parent's event write access

### Example

```python
# Parent with mixed skills
@skill(inheritable=True)
def research(): pass

@skill(inheritable=False)  
def admin_operation(): pass

parent = Agent(name="parent", skills=[research, admin_operation])
child = Agent(name="child", parent=parent)

# child can use: research
# child CANNOT use: admin_operation
```

---

## Error Handling

### Error Categories

| Category | Handling |
|----------|----------|
| Permission denied | Return 403-style error |
| Budget exceeded | Return 429-style error |
| Skill not found | Return 404-style error |
| Execution timeout | Return 408-style error |
| Internal error | Return 500-style error |

### Error Response Format

```json
{
  "error": {
    "type": "permission_denied",
    "message": "Skill 'admin' requires 'file_write' permission",
    "skill_id": "admin",
    "missing_permission": "file_write"
  }
}
```

---

## Security Checklist

Before deploying agents:

- [ ] Guardrails configured with appropriate limits
- [ ] Skills have minimal required permissions
- [ ] Sensitive skills marked `inheritable=False`
- [ ] EventStore persistence enabled for audit
- [ ] Session isolation verified
- [ ] Rate limits configured
- [ ] Token budgets set per session

---

## Compliance

All agent actions are logged for compliance:

- **Who**: Agent ID and session ID
- **What**: Skill invoked with parameters
- **When**: Timestamp of execution
- **Result**: Success/failure with details
- **Cost**: Token usage and USD cost

Logs are immutable and exportable via `Session.export_trace()`.
