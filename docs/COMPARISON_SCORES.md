# AI Agent Framework Comparison Scores

Scoring breakdown for frameworks compared against Piranha Agent in the
[README's fact-checked comparison](../README.md#-framework-comparison).

*Last fact-checked: August 2026. Feature marks below mirror the README table
exactly - see there for per-claim sourcing and citations. This document
does not repeat unverifiable numbers (fabricated throughput/memory/TCO
figures existed in an earlier version of this doc and have been removed
rather than "corrected", since there was never a real measurement behind
them to correct to).*

---

## 🏆 Overall Rankings

Composite score is Piranha's own weighted self-assessment (methodology
below) for the frameworks it has been directly compared against feature-
by-feature. LlamaIndex, Haystack, Agno, AgentScope, and Agency Swarm are
covered in the README's "Additional Frameworks" table but haven't been
run through this scoring - doing so honestly would require the same
weighted judgment calls as below, which we haven't made for them yet.

| Rank | Framework | Overall Score | Status |
|------|-----------|---------------|--------|
| 🥇 | **Piranha Agent** | **9.2/10** | |
| 🥈 | **Microsoft Agent Framework** | **8.8/10** | |
| 🥉 | **DeepAgents** | **8.6/10** | |
| 4 | **LangGraph** | **8.5/10** | |
| 5 | **Pydantic AI** | **8.3/10** | |
| 6 | **Semantic Kernel** | **8.0/10** | Maintenance mode - merged into MAF |
| 7 | **AutoGen** | **7.5/10** | Maintenance mode - merged into MAF |
| 8 | **CrewAI** | **7.0/10** | |

---

## 📊 Scoring Methodology

| Criterion | Weight | Description |
|-----------|--------|--------------|
| **Performance** | 20% | Relative to Piranha's own measured [benchmarks](../README.md#-performance-benchmarks) - not independently benchmarked against every competitor |
| **Security** | 15% | Sandboxing, permissions, guardrails |
| **Features** | 20% | Built-in capabilities, skills/tools ecosystem |
| **Ease of Use** | 15% | Learning curve, documentation, setup |
| **Ecosystem** | 15% | Community, integrations, support |
| **Cost** | 15% | Licensing, self-hosting vs. managed-cloud tiers |

This is Piranha's own self-assessment, not an independently audited
scoring system. We don't have real per-framework performance benchmarks,
memory usage, or cost-of-ownership figures for competitors, so those
aren't presented as data here - only the feature-support facts we
actually verified (see the README table) inform each score.

---

## 📊 Feature Matrix

See the [README's Framework Comparison](../README.md#-framework-comparison)
for the full, sourced feature-by-feature matrix across Wasm sandboxing,
time-travel debugging, semantic caching, skills ecosystems, local LLM
support, event sourcing, multi-cloud, no-code builders, OpenTelemetry,
pricing/licensing, streaming, orchestration style, and memory handling -
covering Piranha, DeepAgents, Microsoft Agent Framework, AutoGen,
LangGraph, CrewAI, Semantic Kernel, LlamaIndex, Haystack, Agno,
AgentScope, and Agency Swarm.

---

## 🎯 Use Case Guidance

This is editorial judgment, not a scored comparison:

| Use Case | Consider | Why |
|----------|----------|-----|
| **Production deployment with local LLMs** | Piranha Agent | Native Ollama, Wasm sandbox, no cloud lock-in |
| **Already on Azure / Microsoft 365** | Microsoft Agent Framework | Native Azure/M365 integration, actively developed successor to AutoGen+SK |
| **Visual, low-code debugging of agent graphs** | LangGraph | LangGraph Studio is a genuine, well-documented feature |
| **Research / rapid prototyping** | AutoGen | Easiest to start with, though now in maintenance mode |
| **Role-based multi-agent workflows** | CrewAI | Native OpenTelemetry and a real no-code builder (CrewAI Studio) as of 2026 |
| **RAG-heavy applications** | LlamaIndex | Purpose-built for retrieval-augmented generation |
| **Org-chart-style agent hierarchies** | Agency Swarm | Directional communication control between agents |

---

*Last updated: August 2026*
