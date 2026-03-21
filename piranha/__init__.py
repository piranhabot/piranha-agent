"""Piranha Agent - Next-generation autonomous agent framework."""

from piranha_core import (
    EventStore,
    GuardrailEngine,
    SemanticCache,
    SkillRegistry,
    WasmRunner,
    DynamicSkillCompiler,
    __version__ as _rust_version,
    # Phase 5
    PostgresEventStore,
    # Phase 6
    AgentOrchestrator,
    DistributedAgent,
)

from piranha.agent import Agent
from piranha.task import Task
from piranha.session import Session
from piranha.skill import Skill, skill

# New features
from piranha.async_agent import AsyncAgent, AgentGroup
from piranha.llm_provider import LLMProvider, LLMMessage, LLMResponse, create_provider
from piranha.memory import MemoryManager, ContextManager, Memory, EmbeddingModel as MemoryEmbeddingModel
from piranha.debugger import create_ui as create_debugger_ui
from piranha.claude_skills import register_claude_skills, get_all_claude_skills
from piranha.official_claude_skills import (
    register_official_claude_skills,
    get_all_official_claude_skills,
)
from piranha.complete_claude_skills import (
    register_additional_claude_skills,
    get_all_additional_claude_skills,
    register_complete_claude_skills,
    get_complete_claude_skills,
)
from piranha.embeddings import EmbeddingModel, get_embedding_model, list_supported_providers
from piranha.realtime import (
    RealtimeMonitor,
    start_monitoring,
    monitor_agent,
    get_monitor,
)
from piranha.collaboration import (
    MultiAgentCollaboration,
    AgentRole,
    create_collaboration,
    run_collaboration,
)
from piranha.observability import (
    ObservabilityManager,
    MetricsCollector,
    AlertManager,
    CostAnomalyDetector,
    get_observability,
    init_observability,
)
from piranha.nocode_builder import create_builder_ui as create_nocode_ui

__version__ = "0.3.0"
__all__ = [
    # Core classes
    "Agent",
    "Task",
    "Session",
    "Skill",
    "skill",
    # Rust core
    "EventStore",
    "GuardrailEngine",
    "SemanticCache",
    "SkillRegistry",
    "WasmRunner",
    "DynamicSkillCompiler",
    # Phase 5: PostgreSQL
    "PostgresEventStore",
    # Phase 6: Distributed
    "AgentOrchestrator",
    "DistributedAgent",
    # Async support
    "AsyncAgent",
    "AgentGroup",
    # LLM Provider
    "LLMProvider",
    "LLMMessage",
    "LLMResponse",
    "create_provider",
    # Memory
    "MemoryManager",
    "ContextManager",
    "Memory",
    "EmbeddingModel",
    # Embeddings
    "get_embedding_model",
    "list_supported_providers",
    # Real-Time Monitoring
    "RealtimeMonitor",
    "start_monitoring",
    "monitor_agent",
    "get_monitor",
    # Debugger
    "create_debugger_ui",
    # Claude Skills - Basic
    "register_claude_skills",
    "get_all_claude_skills",
    # Claude Skills - Official (Anthropic)
    "register_official_claude_skills",
    "get_all_official_claude_skills",
    # Claude Skills - Complete (All 100+)
    "register_additional_claude_skills",
    "get_all_additional_claude_skills",
    "register_complete_claude_skills",
    "get_complete_claude_skills",
    # Observability
    "ObservabilityManager",
    "MetricsCollector",
    "AlertManager",
    "CostAnomalyDetector",
    "get_observability",
    "init_observability",
    # No-Code Builder
    "create_nocode_ui",
]
