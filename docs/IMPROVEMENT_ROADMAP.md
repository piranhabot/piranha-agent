# Piranha Agent - Improvement Roadmap

Analysis of improvement areas based on framework comparisons and competitive analysis.

---

## 📊 Current Standing

| Category | Score | Status | Priority |
|----------|-------|--------|----------|
| **Rust Performance** | 10/10 | ✅ **Complete** | - |
| **Wasm Sandboxing** | 10/10 | ✅ **Complete** | - |
| **Observability** | 10/10 | ✅ **Complete** | - |
| **Security Hardening**| 10/10 | ✅ **Complete** | - |
| **IDE Extensions** | 7/10 | 🟡 **Improved** | High |
| **Semantic Memory** | 9/10 | 🟢 **Semantic** | Medium |
| **Multi-Agent Teams** | 8/10 | 🟢 **Bus/State** | Medium |

---

## 🎯 Next Big Milestones (v0.5.0)

### 1. Advanced Ecosystem (High Priority)
- [ ] **Full IDE Marketplace Release**: Publish the VS Code and JetBrains extensions.
- [ ] **Cloud Sandbox Integration**: Native support for Modal/Runloop/Daytona network egress control from sandboxes.
- [ ] **Plugin Marketplace**: Centralized hub for sharing Claude Skills.

### 2. Intelligent Memory (Medium Priority)
- [ ] **FAISS/ChromaDB Integration**: Move from in-memory to persistent vector databases.
- [ ] **Automated Re-ranking**: Use Cross-Encoders to improve memory retrieval accuracy.

### 3. Distributed Orchestration (Medium Priority)
- [ ] **Shared Message Bus scaling**: Support Redis/RabbitMQ for multi-server agent teams.
- [ ] **Dynamic Load Balancing**: Automatically move tasks between agent workers.

---

## 🏁 Completed in v0.4.0

- [x] **Production-grade Wasmtime integration**: Secure, resource-capped code execution.
- [x] **Real Semantic Embeddings**: Native support for Ollama (nomic) and Sentence-Transformers.
- [x] **Visual Benchmarking Dashboard**: Real-time charts in Piranha Studio for regression tracking.
- [x] **Enterprise Hardening**: Egress whitelisting, automated secret masking, and context-aware permissions.
- [x] **Shared Message Bus**: Asynchronous communication for complex multi-agent workflows.

---

**Which improvements matter most to you?**
- IDE Integration?
- Better Visual Debugging?
- More Enterprise Integrations?
- Plugin Marketplace?
- Something else?

Let us know! 🐟

---

*Last updated: March 2026*  
*Version: 0.4.0*  
*Next Review: Q3 2026*
