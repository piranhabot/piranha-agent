// rust_core/src/lib.rs
//
// Piranha Agent Rust Core — Module Root
//
// This crate is compiled to a Python extension module (.so / .pyd) via PyO3.
// It provides the safety-critical components that Python code cannot bypass:
//   - EventStore (append-only audit log)
//   - SkillRegistry (tool authorization)
//   - GuardrailEngine (hard limits)
//   - SemanticCache (cost reduction)
//   - WasmRunner (sandboxed code execution)
//   - PostgresEventStore (Phase 5: Production backend)
//   - DistributedAgents (Phase 6: Multi-process agents)

pub mod event_store;
pub mod guardrails;
pub mod postgres_store;
pub mod distributed_agents;
pub mod python_bindings;
pub mod semantic_cache;
pub mod skill_registry;
pub mod types;
pub mod wasm_runner;

use pyo3::prelude::*;
use pyo3::Bound;

#[pymodule]
fn piranha_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    python_bindings::register_module(m)
}
