// rust_core/src/python_bindings.rs

use pyo3::exceptions::{PyPermissionError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use std::sync::Arc;
use uuid::Uuid;

use crate::event_store::{EventStore, SqliteEventStore};
use crate::guardrails::{default_guardrails, GuardrailContext, GuardrailEngine};
use crate::semantic_cache::SemanticCache;
use crate::skill_registry::SkillRegistry;
use crate::wasm_runner::{DynamicSkillCompiler, WasmRunner};
use crate::postgres_store::PostgresEventStore as PgEventStore;
use crate::distributed_agents::{AgentOrchestrator as DistOrchestrator, DistributedAgent as DistAgent};
use crate::types::{
    Event, EventPayload, EventType, LlmCallPayload,
    SkillDefinition, SkillType, Permission,
};

use chrono::Utc;
use pyo3::Bound;

// ---------------------------------------------------------------------------
// PyEventStore
// ---------------------------------------------------------------------------

#[pyclass(name = "EventStore")]
pub struct PyEventStore {
    inner: Arc<dyn EventStore>,
}

#[pymethods]
impl PyEventStore {
    #[new]
    #[pyo3(signature = (db_path=None))]
    fn new(db_path: Option<&str>) -> PyResult<Self> {
        let inner: Arc<dyn EventStore> = match db_path {
            Some(path) => Arc::new(
                SqliteEventStore::new(path)
                    .map_err(|e| PyRuntimeError::new_err(e.to_string()))?,
            ),
            None => Arc::new(
                SqliteEventStore::in_memory()
                    .map_err(|e| PyRuntimeError::new_err(e.to_string()))?,
            ),
        };
        Ok(PyEventStore { inner })
    }

    fn export_trace(&self, session_id: &str) -> PyResult<String> {
        let sid = parse_uuid(session_id)?;
        self.inner
            .export_trace(sid)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    fn rollback_to_sequence(
        &self,
        session_id: &str,
        agent_id: &str,
        target_sequence: u64,
    ) -> PyResult<PyObject> {
        let sid = parse_uuid(session_id)?;
        let aid = parse_uuid(agent_id)?;

        let snapshot = self
            .inner
            .rollback_to_sequence(sid, aid, target_sequence)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        Python::with_gil(|py| {
            let json = serde_json::to_string(&snapshot)
                .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
            let json_module = py.import("json")?;
            json_module.call_method1("loads", (json,)).map(|obj| obj.into())
        })
    }

    fn record_llm_call(
        &self,
        session_id: &str,
        agent_id: &str,
        model: &str,
        prompt_tokens: u32,
        completion_tokens: u32,
        cost_usd: f64,
        cache_hit: bool,
        context_event_count: usize,
    ) -> PyResult<String> {
        let sid = parse_uuid(session_id)?;
        let aid = parse_uuid(agent_id)?;

        let sequence = self
            .inner
            .get_next_sequence(sid)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        let prev_cumulative = if sequence > 0 {
            let events = self
                .inner
                .get_events_for_agent(sid, aid)
                .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
            events.last().map(|e| e.cumulative_tokens).unwrap_or(0)
        } else {
            0
        };

        let new_tokens = if cache_hit {
            0
        } else {
            prompt_tokens as u64 + completion_tokens as u64
        };

        let event = Event {
            id: Uuid::new_v4(),
            session_id: sid,
            agent_id: aid,
            parent_event_id: None,
            sequence,
            timestamp: Utc::now(),
            event_type: if cache_hit {
                EventType::CacheHit
            } else {
                EventType::LlmCall
            },
            payload: EventPayload::LlmCall(LlmCallPayload {
                model: model.to_string(),
                prompt_tokens,
                completion_tokens,
                cost_usd,
                context_event_count,
                cache_hit,
                cache_key_hash: None,
            }),
            cumulative_tokens: prev_cumulative + new_tokens,
            metadata: HashMap::new(),
        };

        let event_id = event.id.to_string();
        self.inner
            .append(event)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        Ok(event_id)
    }

    fn get_cost_report(&self, session_id: &str) -> PyResult<PyObject> {
        let sid = parse_uuid(session_id)?;
        let report = self
            .inner
            .build_cost_report(sid)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        Python::with_gil(|py| {
            let json = serde_json::to_string(&report)
                .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
            let json_module = py.import("json")?;
            json_module.call_method1("loads", (json,)).map(|obj| obj.into())
        })
    }
}

// ---------------------------------------------------------------------------
// PySkillRegistry
// ---------------------------------------------------------------------------

#[pyclass(name = "SkillRegistry")]
pub struct PySkillRegistry {
    inner: Arc<SkillRegistry>,
}

#[pymethods]
impl PySkillRegistry {
    #[new]
    fn new() -> Self {
        PySkillRegistry {
            inner: Arc::new(SkillRegistry::new()),
        }
    }

    fn register_skill(
        &self,
        skill_id: &str,
        name: &str,
        description: &str,
        parameters_schema: Bound<'_, PyAny>,
        permissions: Vec<String>,
        inheritable: bool,
    ) -> PyResult<()> {
        let schema = py_to_json(parameters_schema)?;
        let perms = permissions
            .iter()
            .map(|p| parse_permission(p))
            .collect::<PyResult<Vec<_>>>()?;

        let skill = SkillDefinition {
            id: skill_id.to_string(),
            name: name.to_string(),
            description: description.to_string(),
            parameters_schema: schema,
            required_permissions: perms,
            skill_type: SkillType::Static,
            inheritable,
            is_privileged: false,
        };

        self.inner
            .register(skill)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    fn register_dynamic_skill(
        &self,
        name: &str,
        description: &str,
        parameters_schema: Bound<'_, PyAny>,
        agent_id: &str,
    ) -> PyResult<String> {
        let schema = py_to_json(parameters_schema)?;
        let aid = parse_uuid(agent_id)?;
        self.inner
            .register_dynamic(name, description, schema, aid)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    fn grant_skills(&self, agent_id: &str, skill_ids: Vec<String>) -> PyResult<()> {
        let aid = parse_uuid(agent_id)?;
        self.inner
            .grant_skills_to_agent(aid, &skill_ids)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        Ok(())
    }

    fn delegate_to_child(
        &self,
        parent_id: &str,
        child_id: &str,
        skills: Vec<String>,
    ) -> PyResult<()> {
        let parent = parse_uuid(parent_id)?;
        let child = parse_uuid(child_id)?;
        self.inner
            .delegate_to_child(parent, child, &skills)
            .map_err(|e| PyPermissionError::new_err(e.to_string()))?;
        Ok(())
    }

    fn authorize(&self, agent_id: &str, skill_id: &str) -> PyResult<()> {
        let aid = parse_uuid(agent_id)?;
        self.inner
            .authorize_invocation(aid, &skill_id.to_string())
            .map_err(|e| PyPermissionError::new_err(e.to_string()))
    }

    fn get_schemas_for_agent(&self, agent_id: &str) -> PyResult<PyObject> {
        let aid = parse_uuid(agent_id)?;
        let schemas = self
            .inner
            .get_agent_skill_schemas(aid)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        Python::with_gil(|py| {
            let json = serde_json::to_string(&schemas)
                .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
            let json_module = py.import("json")?;
            json_module.call_method1("loads", (json,)).map(|obj| obj.into())
        })
    }
}

// ---------------------------------------------------------------------------
// PyGuardrailEngine
// ---------------------------------------------------------------------------

#[pyclass(name = "GuardrailEngine")]
pub struct PyGuardrailEngine {
    inner: GuardrailEngine,
}

#[pymethods]
impl PyGuardrailEngine {
    #[new]
    #[pyo3(signature = (token_budget=100000))]
    fn new(token_budget: u64) -> Self {
        PyGuardrailEngine {
            inner: GuardrailEngine::new(default_guardrails(token_budget)),
        }
    }

    fn check(
        &self,
        agent_id: &str,
        session_id: &str,
        tokens_used: u64,
        token_budget: Option<u64>,
        pending_action: Option<String>,
    ) -> PyResult<PyObject> {
        let ctx = GuardrailContext {
            agent_id: parse_uuid(agent_id)?,
            session_id: parse_uuid(session_id)?,
            tokens_used,
            token_budget,
            calls_last_minute: 0,
            pending_action,
        };

        let verdict = self
            .inner
            .check(&ctx)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        Python::with_gil(|py| {
            let d = PyDict::new(py);
            match verdict {
                crate::guardrails::GuardrailVerdict::Allow => {
                    d.set_item("verdict", "allow")?;
                    d.set_item("reason", py.None())?;
                }
                crate::guardrails::GuardrailVerdict::Warn(msg) => {
                    d.set_item("verdict", "warn")?;
                    d.set_item("reason", msg)?;
                }
                crate::guardrails::GuardrailVerdict::Block(msg) => {
                    d.set_item("verdict", "block")?;
                    d.set_item("reason", msg)?;
                }
            }
            Ok(d.into())
        })
    }
}

// ---------------------------------------------------------------------------
// PySemanticCache
// ---------------------------------------------------------------------------

#[pyclass(name = "SemanticCache")]
pub struct PySemanticCache {
    inner: SemanticCache,
}

#[pymethods]
impl PySemanticCache {
    #[new]
    #[pyo3(signature = (ttl_hours=24, max_entries=10000))]
    fn new(ttl_hours: i64, max_entries: usize) -> Self {
        PySemanticCache {
            inner: SemanticCache::new(ttl_hours, max_entries),
        }
    }

    fn compute_key(&self, model: &str, messages: Bound<'_, PyAny>) -> PyResult<String> {
        let messages_json = py_to_json(messages)?;
        Ok(self.inner.compute_key(model, &messages_json))
    }

    fn get(&self, key: &str) -> PyResult<Option<PyObject>> {
        match self.inner.get(key) {
            Some(entry) => Python::with_gil(|py| {
                let d = PyDict::new(py);
                d.set_item("response", &entry.response)?;
                d.set_item("model", &entry.model)?;
                d.set_item("prompt_tokens", entry.prompt_tokens)?;
                d.set_item("completion_tokens", entry.completion_tokens)?;
                d.set_item("cost_usd", entry.cost_usd)?;
                d.set_item("hits", entry.hits)?;
                Ok(Some(d.into()))
            }),
            None => Ok(None),
        }
    }

    /// Get with fuzzy matching - returns (entry, similarity_score) or None
    fn get_fuzzy(&self, query: &str, model: &str) -> PyResult<Option<PyObject>> {
        match self.inner.get_fuzzy(query, model) {
            Some((entry, similarity)) => Python::with_gil(|py| {
                let d = PyDict::new(py);
                d.set_item("response", &entry.response)?;
                d.set_item("model", &entry.model)?;
                d.set_item("prompt_tokens", entry.prompt_tokens)?;
                d.set_item("completion_tokens", entry.completion_tokens)?;
                d.set_item("cost_usd", entry.cost_usd)?;
                d.set_item("hits", entry.hits)?;
                d.set_item("similarity", similarity)?;
                Ok(Some(d.into()))
            }),
            None => Ok(None),
        }
    }

    /// Put with embedding for fuzzy matching
    fn put_with_embedding(
        &self,
        key: String,
        prompt_text: String,
        response: String,
        model: String,
        prompt_tokens: u32,
        completion_tokens: u32,
        cost_usd: f64,
    ) {
        self.inner.put_with_embedding(
            key,
            prompt_text,
            response,
            model,
            prompt_tokens,
            completion_tokens,
            cost_usd,
        );
    }

    fn put(
        &self,
        key: String,
        response: String,
        model: String,
        prompt_tokens: u32,
        completion_tokens: u32,
        cost_usd: f64,
    ) {
        self.inner.put(key, response, model, prompt_tokens, completion_tokens, cost_usd);
    }

    /// Search for similar cached entries
    fn search_similar(&self, query: &str, top_k: usize) -> PyResult<Vec<PyObject>> {
        let query_embedding = self.inner.compute_embedding(query);
        let results = self.inner.search_similar(&query_embedding, top_k);
        
        Python::with_gil(|py| {
            let mut py_results = Vec::new();
            for (key, entry, similarity) in results {
                let d = PyDict::new(py);
                d.set_item("key", &key)?;
                d.set_item("response", &entry.response)?;
                d.set_item("prompt_text", &entry.prompt_text)?;
                d.set_item("model", &entry.model)?;
                d.set_item("similarity", similarity)?;
                d.set_item("hits", entry.hits)?;
                py_results.push(d.into());
            }
            Ok(py_results)
        })
    }

    fn total_savings_usd(&self) -> f64 {
        self.inner.total_savings_usd()
    }

    fn entry_count(&self) -> usize {
        self.inner.entry_count()
    }
}

// ---------------------------------------------------------------------------
// PyWasmRunner
// ---------------------------------------------------------------------------

#[pyclass(name = "WasmRunner")]
pub struct PyWasmRunner {
    inner: WasmRunner,
}

#[pymethods]
impl PyWasmRunner {
    #[new]
    fn new() -> PyResult<Self> {
        let inner = WasmRunner::new()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        Ok(PyWasmRunner { inner })
    }

    fn validate(&self, wasm_bytes: &[u8]) -> PyResult<bool> {
        self.inner.validate(wasm_bytes)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    fn execute(&self, wasm_bytes: &[u8], function_name: &str, input: &str) -> PyResult<PyObject> {
        let result = self.inner.execute(wasm_bytes, input)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("success", result.success)?;
            dict.set_item("output", result.output)?;
            dict.set_item("error", result.error)?;
            dict.set_item("execution_time_ms", result.execution_time_ms)?;
            dict.set_item("function_name", function_name)?;
            Ok(dict.into())
        })
    }

    fn execute_with_io(&self, wasm_bytes: &[u8], input: &str) -> PyResult<PyObject> {
        let result = self.inner.execute(wasm_bytes, input)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("success", result.success)?;
            dict.set_item("output", result.output)?;
            dict.set_item("error", result.error)?;
            dict.set_item("execution_time_ms", result.execution_time_ms)?;
            Ok(dict.into())
        })
    }
}

// ---------------------------------------------------------------------------
// PyDynamicSkillCompiler
// ---------------------------------------------------------------------------

#[pyclass(name = "DynamicSkillCompiler")]
pub struct PyDynamicSkillCompiler {
    inner: DynamicSkillCompiler,
}

#[pymethods]
impl PyDynamicSkillCompiler {
    #[new]
    fn new() -> PyResult<Self> {
        let inner = DynamicSkillCompiler::new()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        Ok(PyDynamicSkillCompiler { inner })
    }

    fn register_wasm_skill(&self, skill_id: &str, wasm_bytes: &[u8]) -> PyResult<bool> {
        self.inner.register_wasm_skill(skill_id, wasm_bytes)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    fn compile_and_execute(&self, skill_code: &str, input: &str) -> PyResult<PyObject> {
        let result = self.inner.compile_and_execute(skill_code, input)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("success", result.success)?;
            dict.set_item("output", result.output)?;
            dict.set_item("error", result.error)?;
            dict.set_item("execution_time_ms", result.execution_time_ms)?;
            Ok(dict.into())
        })
    }
}

// ---------------------------------------------------------------------------
// PyPostgresEventStore (Phase 5)
// ---------------------------------------------------------------------------

#[pyclass(name = "PostgresEventStore")]
pub struct PyPostgresEventStore {
    inner: PgEventStore,
}

#[pymethods]
impl PyPostgresEventStore {
    #[new]
    #[pyo3(signature = (connection_string=None))]
    fn new(connection_string: Option<String>) -> Self {
        PyPostgresEventStore {
            inner: PgEventStore::new(connection_string),
        }
    }

    fn get_info(&self) -> PyResult<String> {
        Ok(format!(
            "PostgreSQL Event Store (Phase 5) - Connected: {}",
            self.inner.is_connected()
        ))
    }

    fn get_connection_info(&self) -> PyResult<String> {
        Ok(self.inner.get_connection_info())
    }
}

// ---------------------------------------------------------------------------
// PyAgentOrchestrator (Phase 6)
// ---------------------------------------------------------------------------

#[pyclass(name = "AgentOrchestrator")]
pub struct PyAgentOrchestrator {
    inner: Arc<DistOrchestrator>,
}

#[pymethods]
impl PyAgentOrchestrator {
    #[new]
    #[pyo3(signature = (queue_size=100))]
    fn new(queue_size: usize) -> Self {
        PyAgentOrchestrator {
            inner: Arc::new(DistOrchestrator::new(queue_size)),
        }
    }

    fn register_worker(&self, _agent_id: String) -> PyResult<()> {
        Ok(())
    }

    fn submit_task(&self, description: String, _priority: u8) -> PyResult<String> {
        Ok(format!("task-pending-{}", description.chars().take(10).collect::<String>()))
    }

    fn get_cluster_status(&self) -> PyResult<String> {
        Ok("Cluster status available".to_string())
    }
}

// ---------------------------------------------------------------------------
// PyDistributedAgent (Phase 6)
// ---------------------------------------------------------------------------

#[pyclass(name = "DistributedAgent")]
pub struct PyDistributedAgent {
    id: String,
}

#[pymethods]
impl PyDistributedAgent {
    #[new]
    #[pyo3(signature = (agent_id))]
    fn new(agent_id: String) -> Self {
        PyDistributedAgent { id: agent_id }
    }

    fn get_id(&self) -> String {
        self.id.clone()
    }

    fn get_info(&self) -> String {
        "Distributed Agent (Phase 6) - Use with AgentOrchestrator".to_string()
    }
}

// ---------------------------------------------------------------------------
// Module Registration (Internal - called by lib.rs pymodule)
// ---------------------------------------------------------------------------

pub fn register_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let _ = tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_env("PIRANHA_RUST_LOG")
                .add_directive(tracing::Level::WARN.into()),
        )
        .with_target(false)
        .try_init();

    m.add_class::<PyEventStore>()?;
    m.add_class::<PySkillRegistry>()?;
    m.add_class::<PyGuardrailEngine>()?;
    m.add_class::<PySemanticCache>()?;
    m.add_class::<PyWasmRunner>()?;
    m.add_class::<PyDynamicSkillCompiler>()?;
    // Phase 5
    m.add_class::<PyPostgresEventStore>()?;
    // Phase 6
    m.add_class::<PyAgentOrchestrator>()?;
    m.add_class::<PyDistributedAgent>()?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    Ok(())
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn parse_uuid(s: &str) -> PyResult<Uuid> {
    Uuid::parse_str(s)
        .map_err(|_| PyValueError::new_err(format!("Invalid UUID: '{}'", s)))
}

fn py_to_json(obj: Bound<'_, PyAny>) -> PyResult<serde_json::Value> {
    Python::with_gil(|py| {
        let json_module = py.import("json")?;
        let json_str: String = json_module
            .call_method1("dumps", (obj,))?
            .extract()?;
        serde_json::from_str(&json_str)
            .map_err(|e| PyValueError::new_err(format!("JSON error: {}", e)))
    })
}

fn parse_permission(s: &str) -> PyResult<Permission> {
    match s {
        "network_read"    => Ok(Permission::NetworkRead),
        "network_write"   => Ok(Permission::NetworkWrite),
        "file_read"       => Ok(Permission::FileRead),
        "file_write"      => Ok(Permission::FileWrite),
        "code_execution"  => Ok(Permission::CodeExecution),
        "spawn_sub_agent" => Ok(Permission::SpawnSubAgent),
        "external_api"    => Ok(Permission::ExternalApi),
        "cache_access"    => Ok(Permission::CacheAccess),
        other => Err(PyValueError::new_err(format!(
            "Unknown permission '{}'. Valid: network_read, network_write, \
             file_read, file_write, code_execution, spawn_sub_agent, \
             external_api, cache_access",
            other
        ))),
    }
}