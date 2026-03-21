#!/usr/bin/env python3
"""Rust Core example: Using the low-level Rust core directly.

This example demonstrates:
- EventStore for audit logging
- SemanticCache for cost reduction
- GuardrailEngine for safety
- SkillRegistry for permission management
"""

from piranha_core import (
    EventStore,
    SemanticCache,
    GuardrailEngine,
    SkillRegistry,
)


def main():
    print("=" * 60)
    print("PIRANHA RUST CORE - LOW LEVEL EXAMPLE")
    print("=" * 60)
    print()
    
    # -------------------------------------------------------------------------
    # EventStore - Append-only audit log
    # -------------------------------------------------------------------------
    print("1. EVENT STORE")
    print("-" * 40)
    
    store = EventStore()
    print(f"   Created in-memory event store")
    
    # Record some events
    session_id = "550e8400-e29b-41d4-a716-446655440000"
    agent_id = "660e8400-e29b-41d4-a716-446655440000"
    
    event_id = store.record_llm_call(
        session_id=session_id,
        agent_id=agent_id,
        model="anthropic/claude-3-5-sonnet",
        prompt_tokens=150,
        completion_tokens=50,
        cost_usd=0.002,
        cache_hit=False,
        context_event_count=5,
    )
    print(f"   Recorded LLM call event: {event_id[:8]}...")
    
    # Export trace
    trace = store.export_trace(session_id)
    print(f"   Exported trace: {len(trace)} bytes")
    print()
    
    # -------------------------------------------------------------------------
    # SemanticCache - Cost reduction via caching
    # -------------------------------------------------------------------------
    print("2. SEMANTIC CACHE")
    print("-" * 40)
    
    cache = SemanticCache(ttl_hours=24, max_entries=10000)
    print(f"   Created cache (TTL: 24h, Max entries: 10000)")
    
    # Compute a cache key
    messages = [{"role": "user", "content": "What is Python?"}]
    cache_key = cache.compute_key("gpt-4", messages)
    print(f"   Computed cache key: {cache_key[:20]}...")
    
    # Put a response in cache
    cache.put(
        key=cache_key,
        response="Python is a programming language.",
        model="gpt-4",
        prompt_tokens=10,
        completion_tokens=8,
        cost_usd=0.0003,
    )
    print(f"   Cached a response")
    
    # Get from cache
    cached = cache.get(cache_key)
    if cached:
        print(f"   Retrieved from cache: {cached['response'][:30]}...")
        print(f"   Savings: ${cached['cost_usd']:.4f}")
    
    print(f"   Total entries: {cache.entry_count()}")
    print(f"   Total savings: ${cache.total_savings_usd():.4f}")
    print()
    
    # -------------------------------------------------------------------------
    # GuardrailEngine - Safety checks
    # -------------------------------------------------------------------------
    print("3. GUARDRAIL ENGINE")
    print("-" * 40)
    
    guardrails = GuardrailEngine(token_budget=100000)
    print(f"   Created guardrail engine (budget: 100000 tokens)")
    
    # Check a request
    verdict = guardrails.check(
        agent_id=agent_id,
        session_id=session_id,
        tokens_used=500,
        token_budget=100000,
        pending_action=None,
    )
    print(f"   Guardrail verdict: {verdict['verdict']}")
    print()
    
    # -------------------------------------------------------------------------
    # SkillRegistry - Permission management
    # -------------------------------------------------------------------------
    print("4. SKILL REGISTRY")
    print("-" * 40)
    
    registry = SkillRegistry()
    print(f"   Created skill registry")
    
    # Register a skill
    registry.register_skill(
        skill_id="skill_web_search",
        name="web_search",
        description="Search the web",
        parameters_schema={"type": "object"},
        permissions=["network_read"],
        inheritable=True,
    )
    print(f"   Registered skill: web_search")
    
    # Grant skill to agent
    registry.grant_skills(agent_id, ["skill_web_search"])
    print(f"   Granted skill to agent")
    
    # Authorize invocation
    try:
        registry.authorize(agent_id, "skill_web_search")
        print(f"   Agent authorized to use web_search ✓")
    except Exception as e:
        print(f"   Authorization failed: {e}")
    
    print()
    print("=" * 60)
    print("ALL CORE COMPONENTS WORKING!")
    print("=" * 60)


if __name__ == "__main__":
    main()
