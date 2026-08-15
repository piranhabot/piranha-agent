# Piranha Agent vs Microsoft's Agent Frameworks

*Last fact-checked: August 2026. This document previously included
specific throughput/memory/TCO figures for every framework that were
never real measurements - they've been removed rather than "corrected",
since there was no real number to correct them to. For the sourced,
citation-backed feature comparison, see the
[README](../README.md#-framework-comparison).*

---

## 📊 Microsoft's Agent Framework Evolution

```
┌─────────────────────────────────────────────────────────────┐
│           Microsoft Agent Framework Evolution                │
├─────────────────────────────────────────────────────────────┤
│  AutoGen (2023-2025)  +  Semantic Kernel (2023-2025)        │
│         ↓                        ↓                          │
│  Multi-agent orchestration    Cognitive reasoning            │
│         ↓                        ↓                          │
│  ──────── MERGED ─────────────────────────────              │
│                    ↓                                        │
│         Microsoft Agent Framework (MAF)                     │
│              GA April 2, 2026                               │
└─────────────────────────────────────────────────────────────┘
```

**Verified fact**: Microsoft merged AutoGen and Semantic Kernel into
**Microsoft Agent Framework (MAF)**, which reached GA on April 2, 2026.
Both AutoGen and Semantic Kernel are now officially in **maintenance
mode** (bug/security fixes only) - comparing against them as current
"leading frameworks" is somewhat academic; MAF is the actively developed
successor.

Sources: [Microsoft Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/),
[MAF at BUILD 2026](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/),
[VS Magazine: SK+AutoGen merger](https://visualstudiomagazine.com/articles/2025/10/01/semantic-kernel-autogen--open-source-microsoft-agent-framework.aspx)

---

## 📊 Feature Matrix

See the [README's Framework Comparison](../README.md#-framework-comparison)
for the full, sourced feature-by-feature matrix across Piranha, MAF,
AutoGen, Semantic Kernel, LangGraph, and CrewAI.

Verified corrections from an earlier version of this doc: MAF's
**Multi-Cloud** support (Bedrock, Gemini, Azure, Ollama all natively
supported, not just Azure) and **OpenTelemetry** integration (native,
first-class - `configure_otel_providers()`) were both undersold
previously.

---

## 🏛️ Deep Dive

### AutoGen (2023-2025, now maintenance mode)

**Purpose**: Multi-agent orchestration and conversation management

| Aspect | Details |
|--------|---------|
| **Core Concept** | Agents exchange structured messages in an orchestrated "chatroom" |
| **Architecture** | Lightweight Python library, in-process execution |
| **Local LLM** | ✅ Documented Ollama support |
| **Status** | Maintenance mode - security/bug fixes only, no new features |

```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent("assistant")
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding"})

user_proxy.initiate_chat(assistant, message="Plot a chart of NVDA and TESLA stock price change YTD.")
```

---

### Semantic Kernel (now maintenance mode)

**Purpose**: Cognitive reasoning and planning for individual agents

| Aspect | Details |
|--------|---------|
| **Core Concept** | Planning, semantic memory, reasoning chains |
| **Architecture** | .NET + Python SDK |
| **Local LLM** | ✅ Documented Ollama support alongside Azure OpenAI/Anthropic |
| **Status** | Maintenance mode - security/bug fixes only, no new features |

```csharp
var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion("gpt-4", "endpoint", "key")
    .Build();

var result = await kernel.InvokeAsync("Summarize this document...", variables);
```

---

### Microsoft Agent Framework (MAF) - current production platform

**Purpose**: Unified SDK + runtime combining AutoGen + Semantic Kernel

| Aspect | Details |
|--------|---------|
| **Core Concept** | AutoGen's orchestration + Semantic Kernel's reasoning + Azure runtime |
| **Orchestration patterns** | Sequential, concurrent, handoff, group chat, Magentic-One - the most pattern-flexible of the frameworks compared |
| **Multi-Cloud** | ✅ Bedrock, Gemini, Azure OpenAI, OpenAI, Ollama, all natively supported |
| **OpenTelemetry** | ✅ Native, first-class (`configure_otel_providers()`) |
| **Wasm Sandbox** | ⚠️ Not a core feature; adjacent Microsoft tools (Wassette, Hyperlight Wasm) exist but aren't confirmed built into MAF itself |

Sources: [MAF Workflow Orchestration Patterns](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/),
[MAF Observability docs](https://learn.microsoft.com/en-us/agent-framework/agents/observability),
[Ollama provider docs](https://learn.microsoft.com/en-us/agent-framework/agents/providers/ollama)

---

## 🎯 Use Case Guidance

Editorial judgment, not a scored comparison:

### Consider Piranha Agent if:
- You want a Wasm-sandboxed code execution path
- You need native local-LLM support (Ollama) without extra setup
- You want to avoid Azure lock-in while still wanting multi-cloud model support
- You want built-in time-travel debugging (event replay/rollback)

### Consider Microsoft Agent Framework if:
- You're building on Azure and/or need Microsoft 365 integration
- You want the actively-developed successor to AutoGen/Semantic Kernel rather than either legacy framework
- You need enterprise compliance/governance features out of the box

### Consider AutoGen or Semantic Kernel if:
- You have an existing investment in either and don't need new features
- Otherwise, prefer MAF - both are in maintenance mode

---

## 📚 References

- [Microsoft Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/)
- [MAF at BUILD 2026](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/)
- [VS Magazine: SK+AutoGen merger](https://visualstudiomagazine.com/articles/2025/10/01/semantic-kernel-autogen--open-source-microsoft-agent-framework.aspx)
- [AutoGen Ollama docs](https://microsoft.github.io/autogen/0.2/docs/topics/non-openai-models/local-ollama/)

---

*Last updated: August 2026*
