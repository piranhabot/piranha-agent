# Piranha Agent - Security Guide

**Version:** 0.4.0  
**Last Updated:** March 2026

---

## 🔒 Security Features

### 1. WebSocket Authentication ✅

**Status:** Implemented

All WebSocket connections now require JWT authentication.

**Usage:**
```python
# Get token
import requests
response = requests.get("http://localhost:8080/api/security/token")
token = response.json()["token"]

# Connect to WebSocket with token
ws_url = f"ws://localhost:8080/ws?token={token}"
```

**Configuration:**
```bash
# .env file
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

### 2. CORS Restrictions ✅

**Status:** Implemented

CORS is now restricted to specific origins (no more `*`).

**Configuration:**
```bash
# .env file
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

**Default (Development):**
- `http://localhost:3000`
- `http://localhost:3001`

**Production:**
- Set to your actual domains only
- Never use `*` in production

---

### 3. Rate Limiting ✅

**Status:** Implemented

API endpoints are now rate-limited to prevent abuse.

**Default Limits:**
- General endpoints: 30 requests/minute
- Agent endpoints: 60 requests/minute
- WebSocket: 100 connections

**Configuration:**
```bash
# .env file
RATE_LIMIT_PER_MINUTE=60
```

**Rate Limit Response:**
```json
{
  "detail": "Rate limit exceeded. Try again in X seconds."
}
```

---

### 4. API Key Authentication (Optional) ✅

**Status:** Implemented

Optional API key authentication for additional security layer.

**Configuration:**
```bash
# .env file
API_KEYS=key1,key2,key3
```

**Usage:**
```python
headers = {"X-API-Key": "your-api-key"}
response = requests.get("http://localhost:8080/api/agents", headers=headers)
```

---

### 5. Environment Variables ✅

**Status:** `.env.example` created

**Setup:**
```bash
# Copy example
cp .env.example .env

# Edit .env with your values
nano .env
```

**Critical Variables:**
- `SECRET_KEY` - JWT signing key
- `ALLOWED_ORIGINS` - CORS origins
- `RATE_LIMIT_PER_MINUTE` - Rate limit
- `API_KEYS` - API authentication keys
- `DATABASE_URL` - Database connection
- `ENVIRONMENT` - Environment name

---

## 🔍 Security Checklist

### Before Production Deployment

- [ ] **SECRET_KEY** is set to strong random value
- [ ] **ALLOWED_ORIGINS** restricted to your domains
- [ ] **RATE_LIMIT_PER_MINUTE** set appropriately (30-60)
- [ ] **API_KEYS** configured (if using API auth)
- [ ] **DEBUG** set to `false`
- [ ] **ENVIRONMENT** set to `production`
- [ ] Database credentials are secure
- [ ] LLM API keys are set
- [ ] **LOG_LEVEL** set to `INFO` or `WARNING`

---

## 🛡️ Security Endpoints

### Get Authentication Token

```bash
GET /api/security/token
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

### Run Security Check

```bash
GET /api/security/check
```

**Response:**
```json
{
  "status": "secure",
  "issues": [],
  "warnings": ["Development origins detected"],
  "recommendations": ["Set strong SECRET_KEY"],
  "config": {
    "secret_key_configured": true,
    "cors_origins": ["http://localhost:3000"],
    "api_keys_configured": false,
    "rate_limit_per_minute": 60,
    "token_expiration_minutes": 60
  }
}
```

---

## 🔐 Best Practices

### 1. Secret Key Generation

```bash
# Generate strong secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. API Key Generation

```bash
# Generate API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. CORS Configuration

**Development:**
```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Production:**
```bash
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 4. Rate Limiting

**Development:**
```bash
RATE_LIMIT_PER_MINUTE=60
```

**Production:**
```bash
RATE_LIMIT_PER_MINUTE=30
```

---

## 🚨 Security Issues & Responses

### Issue: Weak SECRET_KEY

**Detection:**
```json
{
  "issues": ["CRITICAL: SECRET_KEY is set to default value!"]
}
```

**Fix:**
```bash
# .env file
SECRET_KEY=<strong-random-key>
```

---

### Issue: CORS Allows All Origins

**Detection:**
```json
{
  "issues": ["CRITICAL: CORS allows all origins (*)!"]
}
```

**Fix:**
```bash
# .env file
ALLOWED_ORIGINS=https://yourdomain.com
```

---

### Issue: Rate Limit Too High

**Detection:**
```json
{
  "warnings": ["Rate limit is high (100/min)"]
}
```

**Fix:**
```bash
# .env file
RATE_LIMIT_PER_MINUTE=30
```

---

## 📊 Security Status

| Feature | Status | Priority |
|---------|--------|----------|
| WebSocket Authentication | ✅ Implemented | Critical |
| CORS Restrictions | ✅ Implemented | Critical |
| Rate Limiting | ✅ Implemented | High |
| API Key Auth | ✅ Implemented | Medium |
| Environment Variables | ✅ `.env.example` | High |
| Security Check Endpoint | ✅ Implemented | High |

---

## 🔍 Running Security Check

### Via API

```bash
curl http://localhost:8080/api/security/check
```

### Via Python

```python
from piranha.security import run_security_check

result = run_security_check()
print(f"Status: {result['status']}")
print(f"Issues: {result['issues']}")
print(f"Warnings: {result['warnings']}")
```

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

---

*Last updated: March 2026*  
*Version: 0.4.0*
