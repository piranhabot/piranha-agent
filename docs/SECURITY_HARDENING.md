# Security Hardening

**Date:** March 2026 (original hardening pass), updated August 2026  
**Version:** 0.4.2

---

*Updated August 2026: this doc originally claimed a "10/10" score and
"Enterprise Ready" status based on the 8 items below. That claim was false
at the time - all 35 of Piranha Studio's HTTP REST routes
(`piranha_agent/realtime.py`) had **zero authentication**, despite the JWT
auth system existing and being fully wired up for WebSocket connections
(item 1). Any client could call `/api/agents`, `/api/wasm/execute`, etc.
with no credentials. This has now been fixed - see
["HTTP API Authentication"](#-http-api-authentication-added-august-2026)
below - but the scorecard and "Enterprise Ready" language have been
removed rather than re-asserted, since a single missing item like this
is exactly the kind of thing a static score tends to paper over.*

---

## 🎯 8 Security Hardening Tasks (March 2026)

### 1. ✅ WebSocket Authentication

- JWT token authentication for all WebSocket connections.
- Token-based connection validation and automatic rejection of unauthenticated users.

### 2. ✅ Restrict CORS Origins

- CORS restricted to specific origins via `ALLOWED_ORIGINS` environment variable.
- Defaults to local development hosts for safety.

### 3. ✅ Add Rate Limiting

- Uniform rate limiting on all API endpoints (30-60 req/min).
- Prevents abuse, brute-force, and resource exhaustion.

### 4. ✅ Secure Environment Template

- Created `.env.example` with production-ready security defaults and checklists.

### 5. ✅ Safety Check Engine

- Automated security auditor via `GET /api/security/check` to validate configuration.

### 6. ✅ Production-Grade Wasm Sandbox

- Replaced placeholder runner with a real **Wasmtime** engine.
- Strict resource isolation (Memory, CPU fuel, Timeouts) for agent-generated code.

### 7. ✅ Skill Permission Enforcement

- Context-aware permission model using Python `contextvars`.
- Skills verify agent authorization tags before execution to prevent tool-calling abuse.

### 8. ✅ Egress Hardening & Secret Masking

- **Egress Whitelisting**: Restrict agent communication to trusted domains via `allowed_hosts`.
- **Secret Masker**: Auto-redaction of API keys, tokens, and passwords from logs and dashboards.
- **Localhost Default**: RealtimeMonitor now binds to `127.0.0.1` by default.

---

## 📁 Hardened Files

| File | Security Enhancement |
|------|----------------------|
| `piranha_agent/security.py` | JWT auth, rate limiting, HTTP request authentication |
| `piranha_agent/realtime.py` | Localhost binding, event scrubbing, auth applied to all REST routes |
| `rust_core/src/wasm_runner.rs` | Wasmtime execution engine |
| `piranha_agent/skill.py` | Permission & URL validation |
| `piranha_agent/observability.py` | Regex-based secret masking |
| `piranha_agent/llm_provider.py` | Strict log verbosity control |

---

## 🔒 Security Comparison

| Feature | Before | After |
|---------|--------|-------|
| **Wasm Sandbox** | ❌ Placeholder | ✅ Wasmtime (Strict) |
| **Permissions** | ❌ Unchecked | ✅ Context-aware tags |
| **Egress Control** | ❌ Open access | ✅ Domain Whitelisting |
| **Secret Masking** | ❌ Plain text logs | ✅ Auto-Redaction |
| **Network Binding** | ❌ 0.0.0.0 (Public) | ✅ 127.0.0.1 (Local) |
| **WebSocket Auth** | ❌ None | ✅ JWT tokens |
| **HTTP REST API Auth** | ❌ None (until Aug 2026) | ✅ Enforced on all 34 non-health routes |

---

## 🔐 HTTP API Authentication (added August 2026)

`piranha_agent/security.py` defines `authenticate_http_request()`, a
FastAPI dependency that checks (in order) a bearer JWT via
`Authorization: Bearer <token>`, then a static key via `X-API-Key`, then
`X-Demo-Secret`. `piranha_agent/realtime.py` now applies it as a
`Depends()` on every `/api/*` route except `GET /api/health`.

**Development mode:** if no `API_KEYS` are configured in the environment
and the app is running in a detected development environment, requests
sent with **no** credentials at all are allowed through (`auth_type:
"dev_bypass"`) so local development doesn't require standing up a key
just to hit the dashboard. Requests that *do* send credentials, even in
dev mode, are still validated - sending a wrong key/token is always
rejected, dev mode or not.

**Production:** set `API_KEYS` (comma-separated) or configure JWT
issuance, and every request to a protected route must present valid
credentials or receives `401 Unauthorized`. See `.env.example` for the
relevant variables.

Covered by `tests/test_realtime_auth.py`.

---

## Status

The 8 items above (March 2026) plus the HTTP API auth fix (August 2026)
are the security-relevant changes made to date. This is not a claim of
completeness or a numeric score - treat it as a changelog, and check
`SECURITY.md` for how to report a vulnerability.
