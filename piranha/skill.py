#!/usr/bin/env python3
"""Skill decorator and registry for Piranha agents.

Supports auto-monitoring for skill execution tracking.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
import functools


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
    function: Optional[Callable] = None
    parameters_schema: dict = field(default_factory=dict)
    required_permissions: list[str] = field(default_factory=list)
    inheritable: bool = True
    auto_monitor: bool = False

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the skill."""
        if self.function is None:
            raise RuntimeError(f"Skill '{self.name}' has no function")
        
        # Auto-monitoring if enabled
        if self.auto_monitor:
            try:
                from piranha.realtime import get_monitor
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
                    from piranha.realtime import get_monitor
                    monitor = get_monitor()
                    monitor.record_event(
                        "skill.failed",
                        {
                            "skill_id": self.id,
                            "skill_name": self.name,
                            "error": str(e)
                        }
                    )
                except Exception:
                    pass
                
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
    name: Optional[str] = None,
    description: str = "",
    parameters: Optional[dict] = None,
    permissions: Optional[list[str]] = None,
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
