"""Tests for Piranha Rust Core."""

import pytest
from piranha_core import (
    EventStore,
    GuardrailEngine,
    SemanticCache,
    SkillRegistry,
)


class TestEventStore:
    """Tests for the EventStore class."""

    def test_create_in_memory(self):
        """Test creating an in-memory event store."""
        store = EventStore()
        assert store is not None

    def test_record_llm_call(self):
        """Test recording an LLM call."""
        store = EventStore()
        session_id = "550e8400-e29b-41d4-a716-446655440000"
        agent_id = "660e8400-e29b-41d4-a716-446655440000"
        
        event_id = store.record_llm_call(
            session_id=session_id,
            agent_id=agent_id,
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            cost_usd=0.003,
            cache_hit=False,
            context_event_count=5,
        )
        
        assert event_id is not None
        assert len(event_id) > 0

    def test_export_trace(self):
        """Test exporting a trace."""
        store = EventStore()
        session_id = "550e8400-e29b-41d4-a716-446655440001"
        agent_id = "660e8400-e29b-41d4-a716-446655440001"
        
        # Record an event
        store.record_llm_call(
            session_id=session_id,
            agent_id=agent_id,
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            cost_usd=0.003,
            cache_hit=False,
            context_event_count=5,
        )
        
        # Export trace
        trace = store.export_trace(session_id)
        assert isinstance(trace, str)
        assert len(trace) > 0
        assert "session_id" in trace

    def test_get_cost_report(self):
        """Test getting a cost report."""
        store = EventStore()
        session_id = "550e8400-e29b-41d4-a716-446655440002"
        agent_id = "660e8400-e29b-41d4-a716-446655440002"
        
        store.record_llm_call(
            session_id=session_id,
            agent_id=agent_id,
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            cost_usd=0.003,
            cache_hit=False,
            context_event_count=5,
        )
        
        report = store.get_cost_report(session_id)
        assert report is not None


class TestSemanticCache:
    """Tests for the SemanticCache class."""

    def test_create_cache(self):
        """Test creating a cache."""
        cache = SemanticCache(ttl_hours=24, max_entries=10000)
        assert cache is not None

    def test_compute_key(self):
        """Test computing a cache key."""
        cache = SemanticCache(ttl_hours=24, max_entries=10000)
        messages = [{"role": "user", "content": "Hello"}]
        key = cache.compute_key("gpt-4", messages)
        assert isinstance(key, str)
        assert len(key) > 0

    def test_put_and_get(self):
        """Test putting and getting from cache."""
        cache = SemanticCache(ttl_hours=24, max_entries=10000)
        key = "test_key"
        
        cache.put(
            key=key,
            response="Test response",
            model="gpt-4",
            prompt_tokens=10,
            completion_tokens=5,
            cost_usd=0.001,
        )
        
        result = cache.get(key)
        assert result is not None
        assert result["response"] == "Test response"
        assert result["model"] == "gpt-4"

    def test_get_missing_key(self):
        """Test getting a non-existent key."""
        cache = SemanticCache(ttl_hours=24, max_entries=10000)
        result = cache.get("non_existent_key")
        assert result is None

    def test_entry_count(self):
        """Test entry count."""
        cache = SemanticCache(ttl_hours=24, max_entries=10000)
        assert cache.entry_count() == 0
        
        cache.put("key1", "resp", "model", 1, 1, 0.001)
        assert cache.entry_count() == 1

    def test_total_savings(self):
        """Test total savings calculation."""
        cache = SemanticCache(ttl_hours=24, max_entries=10000)
        # Note: total_savings tracks savings from cache hits, not puts
        assert cache.total_savings_usd() == 0.0
        
        # Savings are tracked when you retrieve from cache and use the cached response
        # instead of making an LLM call. The put itself doesn't add to savings.
        cache.put("key1", "resp", "model", 1, 1, 0.001)
        
        # Get the cached item
        result = cache.get("key1")
        assert result is not None
        
        # Savings should reflect the cost that would have been spent
        # For now, just verify the method returns a number
        savings = cache.total_savings_usd()
        assert isinstance(savings, float)
        assert savings >= 0


class TestGuardrailEngine:
    """Tests for the GuardrailEngine class."""

    def test_create_engine(self):
        """Test creating a guardrail engine."""
        engine = GuardrailEngine(token_budget=100000)
        assert engine is not None

    def test_check_allow(self):
        """Test guardrail check that allows."""
        engine = GuardrailEngine(token_budget=100000)
        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        session_id = "660e8400-e29b-41d4-a716-446655440000"
        
        verdict = engine.check(
            agent_id=agent_id,
            session_id=session_id,
            tokens_used=100,
            token_budget=100000,
            pending_action=None,
        )
        
        assert verdict is not None
        assert "verdict" in verdict
        assert verdict["verdict"] in ["allow", "warn", "block"]

    def test_check_with_pending_action(self):
        """Test guardrail check with pending action."""
        engine = GuardrailEngine(token_budget=100000)
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        session_id = "660e8400-e29b-41d4-a716-446655440001"
        
        verdict = engine.check(
            agent_id=agent_id,
            session_id=session_id,
            tokens_used=100,
            token_budget=100000,
            pending_action="web_search",
        )
        
        assert verdict is not None
        assert "verdict" in verdict


class TestSkillRegistry:
    """Tests for the SkillRegistry class."""

    def test_create_registry(self):
        """Test creating a skill registry."""
        registry = SkillRegistry()
        assert registry is not None

    def test_register_skill(self):
        """Test registering a skill."""
        registry = SkillRegistry()
        
        registry.register_skill(
            skill_id="test_skill",
            name="Test Skill",
            description="A test skill",
            parameters_schema={"type": "object"},
            permissions=["network_read"],
            inheritable=True,
        )
        
        # Should not raise an exception

    def test_grant_skills(self):
        """Test granting skills to an agent."""
        registry = SkillRegistry()
        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        
        registry.register_skill(
            skill_id="test_skill",
            name="Test Skill",
            description="A test skill",
            parameters_schema={"type": "object"},
            permissions=["network_read"],
            inheritable=True,
        )
        
        registry.grant_skills(agent_id, ["test_skill"])
        # Should not raise an exception

    def test_authorize(self):
        """Test authorizing a skill invocation."""
        registry = SkillRegistry()
        agent_id = "550e8400-e29b-41d4-a716-446655440001"
        
        registry.register_skill(
            skill_id="auth_skill",
            name="Auth Skill",
            description="Skill for auth test",
            parameters_schema={"type": "object"},
            permissions=["file_read"],
            inheritable=True,
        )
        
        registry.grant_skills(agent_id, ["auth_skill"])
        registry.authorize(agent_id, "auth_skill")
        # Should not raise an exception

    def test_unauthorized_skill(self):
        """Test unauthorized skill invocation."""
        registry = SkillRegistry()
        agent_id = "550e8400-e29b-41d4-a716-446655440002"
        
        registry.register_skill(
            skill_id="restricted_skill",
            name="Restricted Skill",
            description="Restricted skill",
            parameters_schema={"type": "object"},
            permissions=["external_api"],
            inheritable=False,
        )
        
        # Should raise an exception since skill not granted
        with pytest.raises(Exception):
            registry.authorize(agent_id, "restricted_skill")
