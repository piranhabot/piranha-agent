#!/usr/bin/env python3
"""Security Configuration for Piranha Studio.

This module provides security utilities:
- JWT authentication for WebSocket
- Rate limiting
- CORS configuration
- API key management
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import WebSocket, HTTPException, Request, status
from fastapi.security import HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
import secrets
import warnings

# Minimum length for API keys to be considered valid.
MIN_API_KEY_LENGTH = 32

# Security configuration from environment
_env_secret_key = os.getenv("SECRET_KEY")
_env = os.getenv("ENV") or os.getenv("PYTHON_ENV") or "production"
if not _env_secret_key:
    if _env.lower() in ("dev", "development", "local"):
        # In development, auto-generate a strong random key if none is provided.
        # Keep it process-local to avoid writing secrets to disk in plaintext.
        warnings.warn(
            "SECRET_KEY not set! Using an ephemeral random development key. "
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
# Storage backend for rate limiting; can be overridden in production deployments.
# Common examples:
#   - "memory://" (default here, single-process in-memory)
#   - "redis://localhost:6379"
#   - "memcached://localhost:11211"
RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")
_env_api_keys = os.getenv("API_KEYS")
API_KEYS = []
if _env_api_keys:
    _invalid_api_keys = []
    for _raw_key in _env_api_keys.split(","):
        _key = _raw_key.strip()
        if not _key:
            continue
        if len(_key) < MIN_API_KEY_LENGTH:
            _invalid_api_keys.append(_key)
            continue
        API_KEYS.append(_key)
    if _invalid_api_keys:
        warnings.warn(
            f"Ignoring {len(_invalid_api_keys)} API key(s) from API_KEYS env var because they are "
            f"shorter than the minimum length of {MIN_API_KEY_LENGTH} characters.",
            UserWarning,
        )

# Initialize rate limiter.
# Use the `get_limiter()` accessor to obtain the Limiter instance, for example:
#     @app.get("/items")
#     @get_limiter().limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
#     async def list_items():
#         ...
_limiter: Optional[Limiter] = None


def is_development_environment() -> bool:
    """Return True when running in a local/development environment."""
    return _env.lower() in ("dev", "development", "local")


def get_limiter() -> Limiter:
    """Return the global Limiter instance, creating it lazily on first use."""
    global _limiter
    if _limiter is None:
        _limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"],
            storage_uri=RATE_LIMIT_STORAGE_URI,
        )
    return _limiter

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
    """Verify WebSocket connection token.

    The authentication token is expected to be provided as the first WebSocket
    message sent by the client, rather than via URL query parameters, to avoid
    exposing credentials in logs, browser history, or referrer headers.

    Args:
        websocket (WebSocket): The client WebSocket connection from which the
            authentication token is received and which is closed on
            authentication failure.

    Returns:
        Optional[dict]: The decoded JWT payload if the token is valid.
            Returns ``None`` if authentication fails or the connection is
            closed during verification.
    """
    try:
        # Receive the first message from the client, which should contain the token.
        token = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token in initial message")
            return None

        payload = verify_token(token)
        return payload
    except asyncio.TimeoutError:
        await websocket.close(code=4003, reason="Authentication token not received in time")
        return None
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
        # Fail closed outside development so a missing API_KEYS configuration
        # does not silently disable authentication in production.
        return is_development_environment()
    
    for valid_key in API_KEYS:
        if secrets.compare_digest(api_key, valid_key):
            return True
    return False


def authenticate_http_request(request: Request) -> dict:
    """Authenticate an HTTP request via Bearer token or X-API-Key.

    Bearer tokens are verified with JWT. API keys are accepted via the
    ``X-API-Key`` header. Outside development, authentication fails closed
    when API keys are not configured.
    """
    auth_header = request.headers.get("Authorization", "")
    api_key = request.headers.get("X-API-Key", "")

    if auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):].strip()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token",
            )
        return verify_token(token)

    if api_key:
        if verify_api_key(api_key):
            return {"auth_type": "api_key"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )


def get_cors_origins() -> list[str]:
    """Get allowed CORS origins."""
    return ALLOWED_ORIGINS


def get_rate_limit() -> int:
    """Get rate limit per minute."""
    return RATE_LIMIT_PER_MINUTE


def _is_secret_key_strong(secret_key: str) -> bool:
    """Heuristically validate SECRET_KEY strength without hardcoded bad values."""
    if not secret_key or len(secret_key) < MIN_API_KEY_LENGTH:
        return False

    if len(set(secret_key)) < 10:
        return False

    lowered = secret_key.lower()
    weak_markers = ("secret", "changeme", "default", "password", "test-key")
    return not any(marker in lowered for marker in weak_markers)


def run_security_check() -> dict:
    """Run comprehensive security check."""
    issues = []
    warnings = []
    recommendations = []

    # Check SECRET_KEY and report if it appears too weak
    if not _is_secret_key_strong(SECRET_KEY):
        if len(SECRET_KEY) < 32:
            issues.append("CRITICAL: SECRET_KEY is too short!")
            recommendations.append("Set a strong SECRET_KEY (min 32 chars) in .env file")
        else:
            issues.append("CRITICAL: SECRET_KEY appears weak or placeholder-like!")
            recommendations.append(
                "Generate and set a strong, random SECRET_KEY in the environment."
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

    secret_key_configured = _is_secret_key_strong(SECRET_KEY)

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
