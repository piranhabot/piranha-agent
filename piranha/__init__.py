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

from piranha.agent import Agent

from piranha.async_agent import AgentGroup, AsyncAgent
from piranha.claude_skills import get_all_claude_skills, register_claude_skills
from piranha.collaboration import (
    create_collaboration,
    run_collaboration,
)
from piranha.complete_claude_skills import (
    get_all_additional_claude_skills,
    get_complete_claude_skills,
    register_additional_claude_skills,
    register_complete_claude_skills,
)
from piranha.debugger import create_ui as create_debugger_ui
from piranha.embeddings import EmbeddingModel, get_embedding_model, list_supported_providers

# Backwards-compatible alias with a more specific name to avoid ambiguity.
# `list_supported_providers` here refers specifically to embedding providers.
list_supported_embedding_providers = list_supported_providers

from piranha.llm_provider import LLMMessage, LLMProvider, LLMResponse, create_provider
from piranha.memory import ContextManager, Memory, MemoryManager
# FIXME: nocode_builder has syntax errors - temporarily disabled
# from piranha.nocode_builder import create_builder_ui as create_nocode_ui
from piranha.observability import (
    AlertManager,
    CostAnomalyDetector,
    MetricsCollector,
    ObservabilityManager,
    get_observability,
    init_observability,
)
from piranha.official_claude_skills import (
    get_all_official_claude_skills,
    register_official_claude_skills,
)
from piranha.realtime import (
    RealtimeMonitor,
    get_monitor,
    monitor_agent,
    start_monitoring,
)
from piranha.session import Session
from piranha.skill import Skill, skill
from piranha.task import Task

from piranha.version import __version__
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
]
