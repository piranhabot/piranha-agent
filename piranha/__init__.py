"""Piranha Agent - Next-generation autonomous agent framework."""

from piranha_core import (
    # Phase 6
    AgentOrchestrator,
    DistributedAgent,
    DynamicSkillCompiler,
    EventStore,
    GuardrailEngine,
    # Phase 5
    PostgresEventStore,
    SemanticCache,
    SkillRegistry,
    WasmRunner,
)

from piranha.agent import Agent

# New features
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
from piranha.llm_provider import LLMMessage, LLMProvider, LLMResponse, create_provider
from piranha.memory import ContextManager, Memory, MemoryManager
from piranha.nocode_builder import create_builder_ui as create_nocode_ui
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

__version__ = "0.4.0"
__all__ = [
    # Core classes
    "Agent",
    "Session",
    "Skill",
    "Task",
    "skill",
    # Rust core and caching
    "DynamicSkillCompiler",
    "EventStore",
    "GuardrailEngine",
    "SemanticCache",
    "SkillRegistry",
    "WasmRunner",
    # PostgreSQL integration
    "PostgresEventStore",
    # Distributed orchestration
    "AgentOrchestrator",
    "DistributedAgent",
    # Async support
    "AgentGroup",
    "AsyncAgent",
    # LLM Provider
    "LLMMessage",
    "LLMProvider",
    "LLMResponse",
    "create_provider",
    # Memory
    "ContextManager",
    "EmbeddingModel",
    "Memory",
    "MemoryManager",
    # Embeddings
    "get_embedding_model",
    "list_supported_providers",
    # Real-Time Monitoring
    "RealtimeMonitor",
    "get_monitor",
    "monitor_agent",
    "start_monitoring",
    # Debugger
    "create_debugger_ui",
    # Claude Skills - Basic
    "get_all_claude_skills",
    "register_claude_skills",
    # Claude Skills - Official (Anthropic)
    "get_all_official_claude_skills",
    "register_official_claude_skills",
    # Claude Skills - Complete (All 100+)
    "get_all_additional_claude_skills",
    "get_complete_claude_skills",
    "register_additional_claude_skills",
    "register_complete_claude_skills",
    # Observability
    "AlertManager",
    "CostAnomalyDetector",
    "MetricsCollector",
    "ObservabilityManager",
    "get_observability",
    "init_observability",
    # No-Code Builder
    "create_nocode_ui",
    # Collaboration
    "create_collaboration",
    "run_collaboration",
]
