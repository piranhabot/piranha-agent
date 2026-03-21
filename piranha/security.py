#!/usr/bin/env python3
"""Security Configuration for Piranha Studio.

This module provides security utilities:
- JWT authentication for WebSocket
- Rate limiting
- CORS configuration
- API key management
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import WebSocket, HTTPException, status
from fastapi.security import HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
import secrets

# Historical default development secret key retained only for detection.
# This value SHOULD NOT be used for any new deployments.
DEFAULT_DEV_SECRET_KEY = "dev-secret-key-change-me"

# Security configuration from environment
_env_secret_key = os.getenv("SECRET_KEY")
_env = os.getenv("ENV") or os.getenv("PYTHON_ENV") or "production"
if not _env_secret_key:
    import warnings
    if _env.lower() in ("dev", "development", "local"):
        # In development, auto-generate a strong random key if none is provided.
        # Fall back to the historical default only for explicit development envs.
        warnings.warn(
            "SECRET_KEY not set! Generating a random development key. "
            "Set a strong, random SECRET_KEY in .env for non-development environments.",
            UserWarning,
        )
        SECRET_KEY = secrets.token_urlsafe(32)
    else:
        # In non-development environments, refuse to start without an explicit SECRET_KEY
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Refusing to start in non-development environment without a secure SECRET_KEY."
        )
else:
    SECRET_KEY = _env_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
).split(",")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
API_KEYS = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []

# Initialize rate limiter.
# Use this `limiter` instance to protect FastAPI routes, for example:
#     @app.get("/items")
#     @limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
#     async def list_items():
#         ...
limiter = Limiter(key_func=get_remote_address)

# Security bearer token
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def verify_websocket_token(websocket: WebSocket) -> Optional[dict]:
    """Verify WebSocket connection token."""
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token in query parameters")
            return None

        payload = verify_token(token)
        return payload
    except HTTPException as exc:
        # Preserve specific authentication error details from token verification
        await websocket.close(code=4002, reason=str(exc.detail))
        return None
    except Exception:
        # Fallback for unexpected errors during authentication
        await websocket.close(code=4002, reason="Authentication error")
        return None


def verify_api_key(api_key: str) -> bool:
    """Verify API key.
    
    If no API keys are configured (API_KEYS is empty), API key authentication is
    treated as disabled and this function returns True. When API keys are
    configured, the provided api_key must be one of the configured keys.
    """
    if not API_KEYS:
        # When no API keys are configured, treat API key authentication as disabled.
        # This aligns with the security check, which only warns in this case.
        return True
    
    return api_key in API_KEYS


def get_cors_origins() -> list[str]:
    """Get allowed CORS origins."""
    return ALLOWED_ORIGINS


def get_rate_limit() -> int:
    """Get rate limit per minute."""
    return RATE_LIMIT_PER_MINUTE


def run_security_check() -> dict:
    """Run comprehensive security check."""
    issues = []
    warnings = []
    recommendations = []

    # Check SECRET_KEY and report if it appears too weak
    if len(SECRET_KEY) < 32:
        issues.append("CRITICAL: SECRET_KEY is too short!")
        recommendations.append("Set a strong SECRET_KEY (min 32 chars) in .env file")
    elif SECRET_KEY == DEFAULT_DEV_SECRET_KEY:
        issues.append("CRITICAL: DEFAULT_DEV_SECRET_KEY is in use!")
        recommendations.append(
            "Generate and set a strong, random SECRET_KEY in the environment; "
            "do not use the built-in development key in production."
        )

    # Check ALLOWED_ORIGINS
    if "*" in ALLOWED_ORIGINS:
        issues.append("CRITICAL: CORS allows all origins (*)!")
        recommendations.append("Restrict ALLOWED_ORIGINS to specific domains")
    elif any("http://localhost" in origin for origin in ALLOWED_ORIGINS):
        warnings.append("Development origins detected (localhost)")

    # Check API_KEYS
    if not API_KEYS:
        warnings.append("No API_KEYS configured")
        recommendations.append("Configure API_KEYS for production use")

    # Check rate limit
    if RATE_LIMIT_PER_MINUTE > 100:
        warnings.append(f"Rate limit is high ({RATE_LIMIT_PER_MINUTE}/min)")
        recommendations.append("Consider lowering RATE_LIMIT_PER_MINUTE for production")

    # Check JWT expiration
    if ACCESS_TOKEN_EXPIRE_MINUTES > 1440:
        warnings.append(f"Token expiration is long ({ACCESS_TOKEN_EXPIRE_MINUTES} minutes)")
        recommendations.append("Consider shorter token expiration for security")

    # A secret key is considered properly configured if it is present, sufficiently long,
    # and not equal to the built-in development key.
    secret_key_configured = bool(SECRET_KEY) and len(SECRET_KEY) >= 32 and SECRET_KEY != DEFAULT_DEV_SECRET_KEY

    return {
        "status": "secure" if not issues else "issues_found",
        "issues": issues,
        "warnings": warnings,
        "recommendations": recommendations,
        "config": {
            "secret_key_configured": secret_key_configured,
            "cors_origins": ALLOWED_ORIGINS,
            "api_keys_configured": len(API_KEYS) > 0,
            "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE,
            "token_expiration_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
        }
    }
