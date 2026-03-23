#!/usr/bin/env python3
"""Skill decorator and registry for Piranha agents.

Supports auto-monitoring for skill execution tracking.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
import contextvars
import logging

logger = logging.getLogger(__name__)

# Context variable to track current agent permissions
# This allows skills to verify if they are authorized to run by the calling agent
agent_permissions: contextvars.ContextVar[list[str]] = contextvars.ContextVar("agent_permissions", default=[])
agent_allowed_hosts: contextvars.ContextVar[list[str]] = contextvars.ContextVar("agent_allowed_hosts", default=[])


def validate_url(url: str) -> None:
    """Validate that a URL is allowed by the current agent's policy.
    
    Args:
        url: URL to validate
        
    Raises:
        PermissionError: If host is not in allowed_hosts
    """
    from urllib.parse import urlparse
    
    allowed = agent_allowed_hosts.get()
    if not allowed or "*" in allowed:
        return
        
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    
    if host not in [h.lower() for h in allowed]:
        error_msg = f"Security Error: Egress blocked. Host '{host}' is not in allowed_hosts: {allowed}"
        logger.error(error_msg)
        raise PermissionError(error_msg)


@dataclass
class Skill:
    """A skill that can be used by agents.

    Attributes:
        id: Unique identifier
        name: Skill name
        description: What the skill does
        function: The actual function to call
        parameters_schema: JSON schema for parameters
        required_permissions: Permissions needed
        inheritable: Whether skill can be inherited
        auto_monitor: Whether to automatically track execution
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    function: Callable | None = None
    parameters_schema: dict = field(default_factory=dict)
    required_permissions: list[str] = field(default_factory=list)
    inheritable: bool = True
    auto_monitor: bool = False

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the skill with permission enforcement."""
        if self.function is None:
            raise RuntimeError(f"Skill '{self.name}' has no function")
        
        # Permission Enforcement
        current_perms = agent_permissions.get()
        for perm in self.required_permissions:
            if perm not in current_perms and "*" not in current_perms:
                error_msg = f"Security Error: Skill '{self.name}' requires permission '{perm}', but agent only has {current_perms}"
                logger.error(error_msg)
                raise PermissionError(error_msg)
        
        # Auto-monitoring if enabled
        if self.auto_monitor:
            try:
                from piranha_agent.realtime import get_monitor
                monitor = get_monitor()
                
                # Record skill start
                monitor.record_event(
                    "skill.started",
                    {
                        "skill_id": self.id,
                        "skill_name": self.name,
                        "args": str(args)[:100],
                        "kwargs": str(kwargs)[:100]
                    }
                )
                
                # Execute function
                result = self.function(*args, **kwargs)
                
                # Record skill completion
                monitor.record_event(
                    "skill.completed",
                    {
                        "skill_id": self.id,
                        "skill_name": self.name,
                        "result": str(result)[:100] if result else None
                    }
                )
                
                return result
                
            except Exception as e:
                # Record skill failure
                try:
                    from piranha_agent.realtime import get_monitor
                    monitor = get_monitor()
                    monitor.record_event(
                        "skill.failed",
                        {
                            "skill_id": self.id,
                            "skill_name": self.name,
                            "error": str(e)
                        }
                    )
                except Exception as monitor_error:
                    # Silently fail if monitoring fails
                    logger.debug(f"Failed to record skill failure: {monitor_error}")
                
                raise
        else:
            # Normal execution without monitoring
            return self.function(*args, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Convert skill to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parameters_schema": self.parameters_schema,
            "required_permissions": self.required_permissions,
            "inheritable": self.inheritable,
            "auto_monitor": self.auto_monitor,
        }


def skill(
    name: str | None = None,
    description: str = "",
    parameters: dict | None = None,
    permissions: list[str] | None = None,
    inheritable: bool = True,
    auto_monitor: bool = False,
) -> Callable:
    """Decorator to create a skill from a function.

    Args:
        name: Skill name (defaults to function name)
        description: What the skill does
        parameters: JSON schema for parameters
        permissions: Required permissions
        inheritable: Whether skill can be inherited
        auto_monitor: Whether to automatically track execution

    Returns:
        Decorator function

    Example:
        @skill(
            name="calculate_tax",
            description="Calculate sales tax",
            auto_monitor=True  # Enable auto-monitoring
        )
        def calculate_tax(amount: float, rate: float) -> float:
            return amount * rate
    """

    def decorator(func: Callable) -> Skill:
        # Create skill instance
        skill_instance = Skill(
            name=name or func.__name__,
            description=description,
            function=func,
            parameters_schema=parameters or {},
            required_permissions=permissions or [],
            inheritable=inheritable,
            auto_monitor=auto_monitor,
        )

        return skill_instance

    return decorator
