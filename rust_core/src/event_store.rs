// rust_core/src/event_store.rs

use anyhow::{Context, Result};
use chrono::Utc;
use parking_lot::Mutex;
use rusqlite::{params, Connection};
use std::sync::Arc;
use tracing::{debug, info};
use uuid::Uuid;

use crate::types::{
    AgentId, AgentStateSnapshot, AgentStatus, CostReport, Event, EventPayload,
    EventType, SessionId,
};

const _SNAPSHOT_INTERVAL: u64 = 50;

pub trait EventStore: Send + Sync {
    fn append(&self, event: Event) -> Result<()>;
    fn get_events_for_session(&self, session_id: SessionId) -> Result<Vec<Event>>;
    fn get_events_for_agent(&self, session_id: SessionId, agent_id: AgentId) -> Result<Vec<Event>>;
    fn get_events_since(&self, session_id: SessionId, after_sequence: u64) -> Result<Vec<Event>>;
    fn get_latest_snapshot(&self, session_id: SessionId, agent_id: AgentId) -> Result<Option<AgentStateSnapshot>>;
    fn get_next_sequence(&self, session_id: SessionId) -> Result<u64>;
    fn build_cost_report(&self, session_id: SessionId) -> Result<CostReport>;
    fn rollback_to_sequence(&self, session_id: SessionId, agent_id: AgentId, target_sequence: u64) -> Result<AgentStateSnapshot>;
    fn export_trace(&self, session_id: SessionId) -> Result<String>;
}

pub struct SqliteEventStore {
    conn: Arc<Mutex<Connection>>,
}

impl SqliteEventStore {
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)
            .with_context(|| format!("Failed to open SQLite at {db_path}"))?;

        conn.execute_batch("PRAGMA journal_mode=WAL;")?;
        conn.execute_batch("PRAGMA foreign_keys=ON;")?;
        conn.execute_batch("PRAGMA cache_size=-8000;")?;

        let store = SqliteEventStore {
            conn: Arc::new(Mutex::new(conn)),
        };
        store.initialize_schema()?;
        Ok(store)
    }

    pub fn in_memory() -> Result<Self> {
        Self::new(":memory:")
    }

    fn initialize_schema(&self) -> Result<()> {
        let conn = self.conn.lock();
        conn.execute_batch(r#"
            CREATE TABLE IF NOT EXISTS events (
                id                TEXT PRIMARY KEY,
                session_id        TEXT NOT NULL,
                agent_id          TEXT NOT NULL,
                parent_event_id   TEXT,
                sequence          INTEGER NOT NULL,
                timestamp         TEXT NOT NULL,
                event_type        TEXT NOT NULL,
                payload_json      TEXT NOT NULL,
                cumulative_tokens INTEGER NOT NULL DEFAULT 0,
                metadata_json     TEXT NOT NULL DEFAULT '{}',
                UNIQUE(session_id, sequence)
            );

            CREATE INDEX IF NOT EXISTS idx_events_session
                ON events(session_id, sequence);

            CREATE INDEX IF NOT EXISTS idx_events_agent
                ON events(session_id, agent_id, sequence);

            CREATE INDEX IF NOT EXISTS idx_events_parent
                ON events(parent_event_id);

            CREATE TABLE IF NOT EXISTS snapshots (
                id            TEXT PRIMARY KEY,
                session_id    TEXT NOT NULL,
                agent_id      TEXT NOT NULL,
                sequence_at   INTEGER NOT NULL,
                created_at    TEXT NOT NULL,
                snapshot_json TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_snapshots_agent
                ON snapshots(session_id, agent_id, sequence_at DESC);

            CREATE TABLE IF NOT EXISTS sessions (
                id            TEXT PRIMARY KEY,
                created_at    TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}'
            );
        "#)?;
        Ok(())
    }
}

impl EventStore for SqliteEventStore {
    fn append(&self, event: Event) -> Result<()> {
        let conn = self.conn.lock();
        let payload_json = serde_json::to_string(&event.payload)?;
        let metadata_json = serde_json::to_string(&event.metadata)?;

        conn.execute(
            r#"INSERT INTO events
               (id, session_id, agent_id, parent_event_id, sequence, timestamp,
                event_type, payload_json, cumulative_tokens, metadata_json)
               VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)"#,
            params![
                event.id.to_string(),
                event.session_id.to_string(),
                event.agent_id.to_string(),
                event.parent_event_id.map(|id| id.to_string()),
                event.sequence,
                event.timestamp.to_rfc3339(),
                format!("{:?}", event.event_type),
                payload_json,
                event.cumulative_tokens,
                metadata_json,
            ],
        ).with_context(|| format!("Failed to append event {}", event.id))?;

        debug!(
            event_id = %event.id,
            sequence = event.sequence,
            "Event appended"
        );
        Ok(())
    }

    fn get_events_for_session(&self, session_id: SessionId) -> Result<Vec<Event>> {
        let conn = self.conn.lock();
        let mut stmt = conn.prepare(
            "SELECT id, session_id, agent_id, parent_event_id, sequence, timestamp,
                    event_type, payload_json, cumulative_tokens, metadata_json
             FROM events
             WHERE session_id = ?1
             ORDER BY sequence ASC",
        )?;

        let events = stmt
            .query_map(params![session_id.to_string()], row_to_event)?
            .collect::<Result<Vec<_>, _>>()
            .context("Failed to deserialize events")?;

        Ok(events)
    }

    fn get_events_for_agent(&self, session_id: SessionId, agent_id: AgentId) -> Result<Vec<Event>> {
        let conn = self.conn.lock();
        let mut stmt = conn.prepare(
            "SELECT id, session_id, agent_id, parent_event_id, sequence, timestamp,
                    event_type, payload_json, cumulative_tokens, metadata_json
             FROM events
             WHERE session_id = ?1 AND agent_id = ?2
             ORDER BY sequence ASC",
        )?;

        let events = stmt
            .query_map(params![session_id.to_string(), agent_id.to_string()], row_to_event)?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(events)
    }

    fn get_events_since(&self, session_id: SessionId, after_sequence: u64) -> Result<Vec<Event>> {
        let conn = self.conn.lock();
        let mut stmt = conn.prepare(
            "SELECT id, session_id, agent_id, parent_event_id, sequence, timestamp,
                    event_type, payload_json, cumulative_tokens, metadata_json
             FROM events
             WHERE session_id = ?1 AND sequence > ?2
             ORDER BY sequence ASC",
        )?;

        let events = stmt
            .query_map(params![session_id.to_string(), after_sequence], row_to_event)?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(events)
    }

    fn get_latest_snapshot(&self, session_id: SessionId, agent_id: AgentId) -> Result<Option<AgentStateSnapshot>> {
        let conn = self.conn.lock();
        let result = conn.query_row(
            "SELECT snapshot_json FROM snapshots
             WHERE session_id = ?1 AND agent_id = ?2
             ORDER BY sequence_at DESC LIMIT 1",
            params![session_id.to_string(), agent_id.to_string()],
            |row| row.get::<_, String>(0),
        );

        match result {
            Ok(json) => Ok(Some(serde_json::from_str(&json)?)),
            Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
            Err(e) => Err(e.into()),
        }
    }

    fn get_next_sequence(&self, session_id: SessionId) -> Result<u64> {
        let conn = self.conn.lock();
        let result: Option<u64> = conn.query_row(
            "SELECT MAX(sequence) FROM events WHERE session_id = ?1",
            params![session_id.to_string()],
            |row| row.get(0),
        )?;
        Ok(result.map(|s| s + 1).unwrap_or(0))
    }

    fn build_cost_report(&self, session_id: SessionId) -> Result<CostReport> {
        let events = self.get_events_for_session(session_id)?;
        let mut report = CostReport {
            session_id,
            ..Default::default()
        };

        for event in &events {
            if let EventPayload::LlmCall(ref llm) = event.payload {
                if llm.cache_hit {
                    report.cache_hits += 1;
                    report.cache_savings_usd += llm.cost_usd;
                } else {
                    report.llm_calls += 1;
                    report.prompt_tokens += llm.prompt_tokens as u64;
                    report.completion_tokens += llm.completion_tokens as u64;
                    report.total_cost_usd += llm.cost_usd;
                    report.total_tokens += llm.prompt_tokens as u64 + llm.completion_tokens as u64;

                    let entry = report.per_model_breakdown.entry(llm.model.clone()).or_default();
                    entry.calls += 1;
                    entry.tokens += llm.prompt_tokens as u64 + llm.completion_tokens as u64;
                    entry.cost_usd += llm.cost_usd;
                }
            }
        }

        Ok(report)
    }

    fn rollback_to_sequence(&self, session_id: SessionId, agent_id: AgentId, target_sequence: u64) -> Result<AgentStateSnapshot> {
        info!(%session_id, %agent_id, target_sequence, "Initiating time-travel rollback");

        let base_snapshot = {
            let conn = self.conn.lock();
            let result = conn.query_row(
                "SELECT snapshot_json FROM snapshots
                 WHERE session_id = ?1 AND agent_id = ?2 AND sequence_at <= ?3
                 ORDER BY sequence_at DESC LIMIT 1",
                params![session_id.to_string(), agent_id.to_string(), target_sequence],
                |row| row.get::<_, String>(0),
            );
            match result {
                Ok(json) => Some(serde_json::from_str::<AgentStateSnapshot>(&json)?),
                Err(rusqlite::Error::QueryReturnedNoRows) => None,
                Err(e) => return Err(e.into()),
            }
        };

        let start_sequence = base_snapshot.as_ref().map(|s| s.sequence_at_snapshot).unwrap_or(0);

        let replay_events = {
            let conn = self.conn.lock();
            let mut stmt = conn.prepare(
                "SELECT id, session_id, agent_id, parent_event_id, sequence, timestamp,
                        event_type, payload_json, cumulative_tokens, metadata_json
                 FROM events
                 WHERE session_id = ?1 AND agent_id = ?2
                   AND sequence > ?3 AND sequence <= ?4
                 ORDER BY sequence ASC",
            )?;
            let rows = stmt.query_map(
                params![session_id.to_string(), agent_id.to_string(), start_sequence, target_sequence],
                row_to_event,
            )?;
            rows.collect::<Result<Vec<_>, _>>()?
        };

        let mut state = base_snapshot.unwrap_or_else(|| AgentStateSnapshot {
            agent_id,
            session_id,
            sequence_at_snapshot: 0,
            memory: vec![],
            tokens_used: 0,
            active_skills: vec![],
            status: AgentStatus::Initializing,
        });

        for event in replay_events {
            apply_event_to_snapshot(&mut state, &event);
        }

        state.sequence_at_snapshot = target_sequence;
        state.status = AgentStatus::RolledBack;

        Ok(state)
    }

    fn export_trace(&self, session_id: SessionId) -> Result<String> {
        let events = self.get_events_for_session(session_id)?;
        let cost_report = self.build_cost_report(session_id)?;

        let trace = serde_json::json!({
            "schema_version": "1.0",
            "session_id": session_id,
            "exported_at": Utc::now().to_rfc3339(),
            "events": events,
            "cost_report": cost_report,
            "event_count": events.len(),
        });

        Ok(serde_json::to_string_pretty(&trace)?)
    }
}

fn apply_event_to_snapshot(state: &mut AgentStateSnapshot, event: &Event) {
    state.tokens_used = event.cumulative_tokens;
    state.sequence_at_snapshot = event.sequence;

    match &event.payload {
        EventPayload::AgentSpawn(spawn) => {
            state.active_skills.extend(spawn.inherited_skills.clone());
        }
        EventPayload::Snapshot(snap) => {
            *state = snap.clone();
        }
        _ => {}
    }

    match event.event_type {
        EventType::AgentCompleted => state.status = AgentStatus::Completed,
        EventType::AgentFailed => state.status = AgentStatus::Failed,
        EventType::SkillInvoked => state.status = AgentStatus::WaitingForTool,
        EventType::SkillCompleted => state.status = AgentStatus::Running,
        EventType::SubAgentSpawned => state.status = AgentStatus::WaitingForSubAgent,
        _ => {}
    }
}

fn row_to_event(row: &rusqlite::Row) -> rusqlite::Result<Event> {
    let id: String = row.get(0)?;
    let session_id: String = row.get(1)?;
    let agent_id: String = row.get(2)?;
    let parent_event_id: Option<String> = row.get(3)?;
    let sequence: u64 = row.get(4)?;
    let timestamp_str: String = row.get(5)?;
    let _event_type_str: String = row.get(6)?;
    let payload_json: String = row.get(7)?;
    let cumulative_tokens: u64 = row.get(8)?;
    let metadata_json: String = row.get(9)?;

    let timestamp = chrono::DateTime::parse_from_rfc3339(&timestamp_str)
        .map(|dt| dt.with_timezone(&chrono::Utc))
        .map_err(|_| rusqlite::Error::InvalidColumnType(5, "timestamp".into(), rusqlite::types::Type::Text))?;

    let payload: EventPayload = serde_json::from_str(&payload_json).unwrap_or(EventPayload::Empty);
    let metadata = serde_json::from_str(&metadata_json).unwrap_or_default();
    let event_type = infer_event_type(&payload);

    Ok(Event {
        id: Uuid::parse_str(&id).unwrap_or_else(|_| Uuid::new_v4()),
        session_id: Uuid::parse_str(&session_id).unwrap_or_else(|_| Uuid::new_v4()),
        agent_id: Uuid::parse_str(&agent_id).unwrap_or_else(|_| Uuid::new_v4()),
        parent_event_id: parent_event_id.and_then(|s| Uuid::parse_str(&s).ok()),
        sequence,
        timestamp,
        event_type,
        payload,
        cumulative_tokens,
        metadata,
    })
}

fn infer_event_type(payload: &EventPayload) -> EventType {
    match payload {
        EventPayload::LlmCall(l) if l.cache_hit => EventType::CacheHit,
        EventPayload::LlmCall(_) => EventType::LlmCall,
        EventPayload::SkillInvocation(s) if s.result.is_some() => EventType::SkillCompleted,
        EventPayload::SkillInvocation(_) => EventType::SkillInvoked,
        EventPayload::Guardrail(g) if g.triggered => EventType::GuardrailBlocked,
        EventPayload::Guardrail(_) => EventType::GuardrailCheck,
        EventPayload::AgentSpawn(_) => EventType::SubAgentSpawned,
        EventPayload::Budget(_) => EventType::BudgetAlert,
        EventPayload::Snapshot(_) => EventType::StateSnapshot,
        _ => EventType::AgentCompleted,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    fn make_test_event(session_id: SessionId, agent_id: AgentId, sequence: u64) -> Event {
        Event {
            id: Uuid::new_v4(),
            session_id,
            agent_id,
            parent_event_id: None,
            sequence,
            timestamp: Utc::now(),
            event_type: EventType::LlmCall,
            payload: EventPayload::LlmCall(LlmCallPayload {
                model: "llama3".to_string(),
                prompt_tokens: 100,
                completion_tokens: 50,
                cost_usd: 0.0,
                context_event_count: 5,
                cache_hit: false,
                cache_key_hash: None,
            }),
            cumulative_tokens: sequence * 150,
            metadata: HashMap::new(),
        }
    }

    #[test]
    fn test_append_and_retrieve() {
        let store = SqliteEventStore::in_memory().unwrap();
        let session_id = Uuid::new_v4();
        let agent_id = Uuid::new_v4();
        let event = make_test_event(session_id, agent_id, 0);
        store.append(event.clone()).unwrap();
        let retrieved = store.get_events_for_session(session_id).unwrap();
        assert_eq!(retrieved.len(), 1);
        assert_eq!(retrieved[0].id, event.id);
    }

    #[test]
    fn test_rollback() {
        let store = SqliteEventStore::in_memory().unwrap();
        let session_id = Uuid::new_v4();
        let agent_id = Uuid::new_v4();
        for i in 0..10 {
            store.append(make_test_event(session_id, agent_id, i)).unwrap();
        }
        let state = store.rollback_to_sequence(session_id, agent_id, 5).unwrap();
        assert_eq!(state.sequence_at_snapshot, 5);
        assert_eq!(state.status, AgentStatus::RolledBack);
    }
}