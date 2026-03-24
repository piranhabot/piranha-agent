"""Piranha Agent - Next-generation autonomous agent framework.

This top-level package re-exports core Rust-backed primitives from the
separately distributed ``piranha_core`` module (typically installed as the
``piranha-core`` package). The underscore in ``piranha_core`` reflects the
standard Python import naming convention for packages whose distribution
name uses a dash.
"""

from piranha_core import (
    AgentOrchestrator,
    DistributedAgent,
    DynamicSkillCompiler,
    EventStore,
    GuardrailEngine,
    PostgresEventStore,
    SemanticCache,
    SkillRegistry,
    WasmRunner,
)

from piranha_agent.agent import Agent

from piranha_agent.async_agent import AgentGroup, AsyncAgent
from piranha_agent.claude_skills import get_all_claude_skills, register_claude_skills
from piranha_agent.collaboration import (
    create_collaboration,
    run_collaboration,
)
from piranha_agent.complete_claude_skills import (
    get_all_additional_claude_skills,
    get_complete_claude_skills,
    register_additional_claude_skills,
    register_complete_claude_skills,
)
from piranha_agent.debugger import create_ui as create_debugger_ui
from piranha_agent.nocode_builder_app import create_builder_ui as create_nocode_ui
from piranha_agent.embeddings import EmbeddingModel, get_embedding_model, list_supported_providers

# Backwards-compatible alias with a more specific name to avoid ambiguity.
# `list_supported_providers` here refers specifically to embedding providers.
list_supported_embedding_providers = list_supported_providers

from piranha_agent.llm_provider import LLMMessage, LLMProvider, LLMResponse, create_provider
from piranha_agent.memory import ContextManager, Memory, MemoryManager
from piranha_agent.observability import (
    AlertManager,
    CostAnomalyDetector,
    MetricsCollector,
    ObservabilityManager,
    get_observability,
    init_observability,
)
from piranha_agent.official_claude_skills import (
    get_all_official_claude_skills,
    register_official_claude_skills,
)
from piranha_agent.realtime import (
    RealtimeMonitor,
    get_monitor,
    monitor_agent,
    start_monitoring,
)
from piranha_agent.session import Session
from piranha_agent.skill import Skill, skill
from piranha_agent.task import Task

from piranha_agent.version import __version__
__all__ = [
    # Core Agent Framework
    "Agent",
    "AsyncAgent",
    "Task",
    "Session",
    "AgentGroup",
    # Skills
    "Skill",
    "skill",
    # Claude Skills (All 100+)
    "register_claude_skills",
    "get_all_claude_skills",
    "register_official_claude_skills",
    "get_all_official_claude_skills",
    "register_additional_claude_skills",
    "get_all_additional_claude_skills",
    "register_complete_claude_skills",
    "get_complete_claude_skills",
    # Rust Core Components
    "DynamicSkillCompiler",
    "EventStore",
    "GuardrailEngine",
    "SemanticCache",
    "SkillRegistry",
    "WasmRunner",
    # PostgreSQL Integration
    "PostgresEventStore",
    # Distributed Orchestration
    "AgentOrchestrator",
    "DistributedAgent",
    # LLM Provider
    "LLMProvider",
    "LLMMessage",
    "LLMResponse",
    "create_provider",
    # Memory & Embeddings
    "MemoryManager",
    "ContextManager",
    "Memory",
    "EmbeddingModel",
    "get_embedding_model",
    "list_supported_providers",
    "list_supported_embedding_providers",
    # Real-Time Monitoring
    "RealtimeMonitor",
    "start_monitoring",
    "monitor_agent",
    "get_monitor",
    # Observability
    "ObservabilityManager",
    "MetricsCollector",
    "AlertManager",
    "CostAnomalyDetector",
    "get_observability",
    "init_observability",
    # Developer Tools
    "create_debugger_ui",
    "create_nocode_ui",
    # Collaboration
    "create_collaboration",
    "run_collaboration",
        # Package Metadata
    "__version__",
]
