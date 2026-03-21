#!/usr/bin/env python3
"""Security Configuration for Piranha Studio.

This module provides security utilities:
- JWT authentication for WebSocket
- Rate limiting
- CORS configuration
- API key management
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address

# Security configuration from environment
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
).split(",")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
API_KEYS = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Security bearer token
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
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
            await websocket.close(code=4001, reason="Missing authentication token")
            return None
        
        payload = verify_token(token)
        return payload
    except Exception:
        await websocket.close(code=4002, reason="Invalid authentication token")
        return None


def verify_api_key(api_key: str) -> bool:
    """Verify API key."""
    if not API_KEYS:
        return True  # No API keys configured, allow all
    
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
    
    # Check SECRET_KEY
    if SECRET_KEY == "your-secret-key-change-in-production":
        issues.append("CRITICAL: SECRET_KEY is set to default value!")
        recommendations.append("Set a strong SECRET_KEY in .env file")
    
    # Check ALLOWED_ORIGINS
    if "*" in ALLOWED_ORIGINS:
        issues.append("CRITICAL: CORS allows all origins (*)!")
        recommendations.append("Restrict ALLOWED_ORIGINS to specific domains")
    elif "http://localhost" in str(ALLOWED_ORIGINS):
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
    
    return {
        "status": "secure" if not issues else "issues_found",
        "issues": issues,
        "warnings": warnings,
        "recommendations": recommendations,
        "config": {
            "secret_key_configured": SECRET_KEY != "your-secret-key-change-in-production",
            "cors_origins": ALLOWED_ORIGINS,
            "api_keys_configured": len(API_KEYS) > 0,
            "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE,
            "token_expiration_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
        }
    }
