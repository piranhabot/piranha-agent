"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_uuid():
    """Return a sample UUID for testing."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def event_store():
    """Create an in-memory event store."""
    from piranha_core import EventStore
    return EventStore()


@pytest.fixture
def semantic_cache():
    """Create a semantic cache."""
    from piranha_core import SemanticCache
    return SemanticCache(ttl_hours=24, max_entries=10000)


@pytest.fixture
def guardrail_engine():
    """Create a guardrail engine."""
    from piranha_core import GuardrailEngine
    return GuardrailEngine(token_budget=100000)


@pytest.fixture
def skill_registry():
    """Create a skill registry."""
    from piranha_core import SkillRegistry
    return SkillRegistry()


@pytest.fixture
def agent():
    """Create a test agent."""
    from piranha import Agent
    return Agent(name="test_agent", model="gpt-4-test")


@pytest.fixture
def session():
    """Create a test session."""
    from piranha import Session
    return Session.create()
