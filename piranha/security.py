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
import warnings

# Historical default development secret key retained only for detection.
# This value SHOULD NOT be used for any new deployments.
DEFAULT_DEV_SECRET_KEY = "dev-secret-key-change-me"

# Minimum length for API keys to be considered valid.
MIN_API_KEY_LENGTH = 32

# Security configuration from environment
_env_secret_key = os.getenv("SECRET_KEY")
_env = os.getenv("ENV") or os.getenv("PYTHON_ENV") or "production"
if not _env_secret_key:
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
        token = await websocket.receive_text()
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token in initial message")
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
    
    for valid_key in API_KEYS:
        if secrets.compare_digest(api_key, valid_key):
            return True
    return False


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

    def _is_secret_key_properly_configured() -> bool:
        """
        A secret key is considered properly configured if it is present, sufficiently long,
        and not equal to the built-in development key.
        """
        return bool(SECRET_KEY) and len(SECRET_KEY) >= 32 and SECRET_KEY != DEFAULT_DEV_SECRET_KEY

    # Check SECRET_KEY and report if it appears too weak
    if not _is_secret_key_properly_configured():
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
    secret_key_configured = _is_secret_key_properly_configured()

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
