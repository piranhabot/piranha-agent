// rust_core/src/types.rs

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

pub type AgentId = Uuid;
pub type SkillId = String;
pub type EventId = Uuid;
pub type SessionId = Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Event {
    pub id: EventId,
    pub session_id: SessionId,
    pub agent_id: AgentId,
    pub parent_event_id: Option<EventId>,
    pub sequence: u64,
    pub timestamp: DateTime<Utc>,
    pub event_type: EventType,
    pub payload: EventPayload,
    pub cumulative_tokens: u64,
    pub metadata: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum EventType {
    AgentSpawned,
    LlmCall,
    SkillInvoked,
    SkillCompleted,
    GuardrailCheck,
    GuardrailBlocked,
    SubAgentSpawned,
    BudgetAlert,
    AgentCompleted,
    AgentFailed,
    StateSnapshot,
    CacheHit,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(untagged)]
pub enum EventPayload {
    LlmCall(LlmCallPayload),
    SkillInvocation(SkillInvocationPayload),
    Guardrail(GuardrailPayload),
    AgentSpawn(AgentSpawnPayload),
    Budget(BudgetPayload),
    Text(String),
    Snapshot(AgentStateSnapshot),
    Empty,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct LlmCallPayload {
    pub model: String,
    pub prompt_tokens: u32,
    pub completion_tokens: u32,
    pub cost_usd: f64,
    pub context_event_count: usize,
    pub cache_hit: bool,
    pub cache_key_hash: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct SkillInvocationPayload {
    pub skill_id: SkillId,
    pub skill_name: String,
    pub args: serde_json::Value,
    pub result: Option<serde_json::Value>,
    pub duration_ms: Option<u64>,
    pub sandboxed: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct GuardrailPayload {
    pub rule_name: String,
    pub rule_type: GuardrailType,
    pub triggered: bool,
    pub action_blocked: Option<String>,
    pub reason: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum GuardrailType {
    TokenBudget,
    ContentFilter,
    SkillPermission,
    RateLimit,
    Custom,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct AgentSpawnPayload {
    pub child_agent_id: AgentId,
    pub child_agent_name: String,
    pub inherited_skills: Vec<SkillId>,
    pub token_budget: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct BudgetPayload {
    pub budget_total: u64,
    pub budget_used: u64,
    pub threshold_pct: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct AgentStateSnapshot {
    pub agent_id: AgentId,
    pub session_id: SessionId,
    pub sequence_at_snapshot: u64,
    pub memory: Vec<MemoryEntry>,
    pub tokens_used: u64,
    pub active_skills: Vec<SkillId>,
    pub status: AgentStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct MemoryEntry {
    pub role: String,
    pub content: String,
    pub event_id: EventId,
    pub relevance_score: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum AgentStatus {
    Initializing,
    Running,
    WaitingForTool,
    WaitingForSubAgent,
    Completed,
    Failed,
    RolledBack,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillDefinition {
    pub id: SkillId,
    pub name: String,
    pub description: String,
    pub parameters_schema: serde_json::Value,
    pub required_permissions: Vec<Permission>,
    pub skill_type: SkillType,
    pub inheritable: bool,
    pub is_privileged: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum SkillType {
    Static,
    Dynamic,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
pub enum Permission {
    NetworkRead,
    NetworkWrite,
    FileRead,
    FileWrite,
    CodeExecution,
    SpawnSubAgent,
    ExternalApi,
    CacheAccess,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GuardrailConfig {
    pub name: String,
    pub rule_type: GuardrailType,
    pub is_hard_limit: bool,
    pub params: GuardrailParams,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum GuardrailParams {
    TokenBudget { max_tokens: u64, warn_at_pct: u8 },
    RateLimit { max_calls_per_minute: u32 },
    ContentFilter { blocked_patterns: Vec<String> },
    Custom { config: serde_json::Value },
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct CostReport {
    pub session_id: SessionId,
    pub total_tokens: u64,
    pub prompt_tokens: u64,
    pub completion_tokens: u64,
    pub total_cost_usd: f64,
    pub cache_hits: u32,
    pub cache_savings_usd: f64,
    pub llm_calls: u32,
    pub per_model_breakdown: HashMap<String, ModelCost>,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ModelCost {
    pub calls: u32,
    pub tokens: u64,
    pub cost_usd: f64,
}