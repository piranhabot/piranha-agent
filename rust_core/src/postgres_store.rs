// rust_core/src/postgres_store.rs
//
// Phase 5: PostgreSQL Event Store for Production
//
// Real, connected implementation of the EventStore trait backed by a
// deadpool-postgres connection pool. The EventStore trait's methods are
// synchronous (to match SqliteEventStore and PyO3's sync bindings), so each
// method bridges into async deadpool-postgres/tokio-postgres work via an
// internally-owned Tokio runtime.

use anyhow::{Context, Result};
use chrono::Utc;
use deadpool_postgres::{Config as PoolConfig, Pool, Runtime as PoolRuntime};
use std::env;
use tokio_postgres::NoTls;
use tracing::{debug, info};
use uuid::Uuid;

use crate::event_store::{apply_event_to_snapshot, infer_event_type, EventStore};
use crate::types::{
    AgentId, AgentStateSnapshot, AgentStatus, CostReport, Event, EventPayload, SessionId,
};

/// PostgreSQL-based event store configuration
#[derive(Debug, Clone)]
pub struct PostgresConfig {
    pub host: String,
    pub port: u16,
    pub database: String,
    pub user: String,
    pub password: String,
}

impl Default for PostgresConfig {
    fn default() -> Self {
        Self {
            host: env::var("PGHOST").unwrap_or_else(|_| "localhost".to_string()),
            port: env::var("PGPORT")
                .ok()
                .and_then(|p| p.parse().ok())
                .unwrap_or(5432),
            database: env::var("PGDATABASE").unwrap_or_else(|_| "piranha".to_string()),
            user: env::var("PGUSER").unwrap_or_else(|_| "postgres".to_string()),
            password: env::var("PGPASSWORD").unwrap_or_else(|_| "postgres".to_string()),
        }
    }
}

impl PostgresConfig {
    /// Parse a `postgresql://user:password@host:port/database` connection string.
    fn parse(conn_str: &str) -> Result<Self> {
        let defaults = PostgresConfig::default();

        let rest = conn_str
            .strip_prefix("postgresql://")
            .or_else(|| conn_str.strip_prefix("postgres://"))
            .with_context(|| format!("Invalid PostgreSQL connection string: {conn_str}"))?;

        let (userinfo, hostpart) = match rest.split_once('@') {
            Some((userinfo, hostpart)) => (Some(userinfo), hostpart),
            None => (None, rest),
        };

        let (user, password) = match userinfo {
            Some(userinfo) => match userinfo.split_once(':') {
                Some((u, p)) => (u.to_string(), p.to_string()),
                None => (userinfo.to_string(), defaults.password.clone()),
            },
            None => (defaults.user.clone(), defaults.password.clone()),
        };

        let (hostport, database) = match hostpart.split_once('/') {
            Some((hostport, db)) => (hostport, db.to_string()),
            None => (hostpart, defaults.database.clone()),
        };

        let (host, port) = match hostport.split_once(':') {
            Some((h, p)) => (
                h.to_string(),
                p.parse::<u16>()
                    .with_context(|| format!("Invalid port in connection string: {p}"))?,
            ),
            None => (hostport.to_string(), defaults.port),
        };

        let host = if host.is_empty() { defaults.host } else { host };
        let database = if database.is_empty() {
            defaults.database
        } else {
            database
        };

        Ok(PostgresConfig {
            host,
            port,
            database,
            user,
            password,
        })
    }
}

/// PostgreSQL Event Store (Phase 5) - real connection pool + schema-backed
/// implementation of the EventStore trait.
pub struct PostgresEventStore {
    config: PostgresConfig,
    pool: Pool,
    runtime: tokio::runtime::Runtime,
}

impl PostgresEventStore {
    /// Create and connect a new PostgreSQL event store.
    ///
    /// Accepts either a full `postgresql://user:pass@host:port/db` connection
    /// string, or `None` to fall back to PGHOST/PGPORT/PGDATABASE/PGUSER/
    /// PGPASSWORD environment variables (matching PostgresConfig::default()).
    pub fn new(connection_string: Option<String>) -> Result<Self> {
        let config = match connection_string {
            Some(conn_str) => PostgresConfig::parse(&conn_str)?,
            None => PostgresConfig::default(),
        };

        let runtime = tokio::runtime::Runtime::new()
            .context("Failed to create Tokio runtime for PostgresEventStore")?;

        let mut pool_config = PoolConfig::new();
        pool_config.host = Some(config.host.clone());
        pool_config.port = Some(config.port);
        pool_config.dbname = Some(config.database.clone());
        pool_config.user = Some(config.user.clone());
        pool_config.password = Some(config.password.clone());

        let pool = pool_config
            .create_pool(Some(PoolRuntime::Tokio1), NoTls)
            .context("Failed to create PostgreSQL connection pool")?;

        let store = PostgresEventStore {
            config,
            pool,
            runtime,
        };
        store.initialize_schema()?;

        info!(
            host = %store.config.host,
            database = %store.config.database,
            "PostgreSQL Event Store connected (Phase 5)"
        );

        Ok(store)
    }

    /// Create with connection string.
    pub fn with_connection_string(conn_str: &str) -> Result<Self> {
        Self::new(Some(conn_str.to_string()))
    }

    fn initialize_schema(&self) -> Result<()> {
        self.runtime.block_on(async {
            let client = self.pool.get().await.context("Failed to get pool connection")?;
            client
                .batch_execute(
                    r#"
                    CREATE TABLE IF NOT EXISTS events (
                        id                TEXT PRIMARY KEY,
                        session_id        TEXT NOT NULL,
                        agent_id          TEXT NOT NULL,
                        parent_event_id   TEXT,
                        sequence          BIGINT NOT NULL,
                        timestamp         TEXT NOT NULL,
                        event_type        TEXT NOT NULL,
                        payload_json      TEXT NOT NULL,
                        cumulative_tokens BIGINT NOT NULL DEFAULT 0,
                        metadata_json     TEXT NOT NULL DEFAULT '{}',
                        UNIQUE(session_id, sequence)
                    );

                    CREATE INDEX IF NOT EXISTS idx_events_session
                        ON events(session_id, sequence);

                    CREATE INDEX IF NOT EXISTS idx_events_agent
                        ON events(session_id, agent_id, sequence);

                    CREATE TABLE IF NOT EXISTS snapshots (
                        id            TEXT PRIMARY KEY,
                        session_id    TEXT NOT NULL,
                        agent_id      TEXT NOT NULL,
                        sequence_at   BIGINT NOT NULL,
                        created_at    TEXT NOT NULL,
                        snapshot_json TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_snapshots_agent
                        ON snapshots(session_id, agent_id, sequence_at DESC);
                    "#,
                )
                .await
                .context("Failed to initialize PostgreSQL schema")?;
            Ok::<(), anyhow::Error>(())
        })
    }

    /// Get connection info (for testing/display) - never exposes the real password.
    pub fn get_connection_info(&self) -> String {
        format!(
            "postgresql://{}:{}@{}:{}/{}",
            self.config.user,
            "*".repeat(self.config.password.len()),
            self.config.host,
            self.config.port,
            self.config.database
        )
    }

    /// Check if the store has a live connection pool.
    pub fn is_connected(&self) -> bool {
        self.pool.status().available > 0 || self.pool.status().size > 0
    }

    /// Get config.
    pub fn get_config(&self) -> &PostgresConfig {
        &self.config
    }
}

impl EventStore for PostgresEventStore {
    fn append(&self, event: Event) -> Result<()> {
        self.runtime.block_on(async {
            let client = self.pool.get().await.context("Failed to get pool connection")?;
            let payload_json = serde_json::to_string(&event.payload)?;
            let metadata_json = serde_json::to_string(&event.metadata)?;

            client
                .execute(
                    r#"INSERT INTO events
                       (id, session_id, agent_id, parent_event_id, sequence, timestamp,
                        event_type, payload_json, cumulative_tokens, metadata_json)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)"#,
                    &[
                        &event.id.to_string(),
                        &event.session_id.to_string(),
                        &event.agent_id.to_string(),
                        &event.parent_event_id.map(|id| id.to_string()),
                        &(event.sequence as i64),
                        &event.timestamp.to_rfc3339(),
                        &format!("{:?}", event.event_type),
                        &payload_json,
                        &(event.cumulative_tokens as i64),
                        &metadata_json,
                    ],
                )
                .await
                .with_context(|| format!("Failed to append event {}", event.id))?;

            debug!(event_id = %event.id, sequence = event.sequence, "Event appended (Postgres)");
            Ok(())
        })
    }

    fn get_events_for_session(&self, session_id: SessionId) -> Result<Vec<Event>> {
        self.runtime.block_on(async {
            let client = self.pool.get().await.context("Failed to get pool connection")?;
            let rows = client
                .query(
                    "SELECT id, session_id, agent_id, parent_event_id, sequence, timestamp,
                            payload_json, cumulative_tokens, metadata_json
                     FROM events WHERE session_id = $1 ORDER BY sequence ASC",
                    &[&session_id.to_string()],
                )
                .await
                .context("Failed to query events for session")?;
            rows.iter().map(row_to_event).collect()
        })
    }

    fn get_events_for_agent(&self, session_id: SessionId, agent_id: AgentId) -> Result<Vec<Event>> {
        self.runtime.block_on(async {
            let client = self.pool.get().await.context("Failed to get pool connection")?;
            let rows = client
                .query(
                    "SELECT id, session_id, agent_id, parent_event_id, sequence, timestamp,
                            payload_json, cumulative_tokens, metadata_json
                     FROM events WHERE session_id = $1 AND agent_id = $2 ORDER BY sequence ASC",
                    &[&session_id.to_string(), &agent_id.to_string()],
                )
                .await
                .context("Failed to query events for agent")?;
            rows.iter().map(row_to_event).collect()
        })
    }

    fn get_events_since(&self, session_id: SessionId, after_sequence: u64) -> Result<Vec<Event>> {
        self.runtime.block_on(async {
            let client = self.pool.get().await.context("Failed to get pool connection")?;
            let rows = client
                .query(
                    "SELECT id, session_id, agent_id, parent_event_id, sequence, timestamp,
                            payload_json, cumulative_tokens, metadata_json
                     FROM events WHERE session_id = $1 AND sequence > $2 ORDER BY sequence ASC",
                    &[&session_id.to_string(), &(after_sequence as i64)],
                )
                .await
                .context("Failed to query events since sequence")?;
            rows.iter().map(row_to_event).collect()
        })
    }

    fn get_latest_snapshot(&self, session_id: SessionId, agent_id: AgentId) -> Result<Option<AgentStateSnapshot>> {
        self.runtime.block_on(async {
            let client = self.pool.get().await.context("Failed to get pool connection")?;
            let row = client
                .query_opt(
                    "SELECT snapshot_json FROM snapshots
                     WHERE session_id = $1 AND agent_id = $2
                     ORDER BY sequence_at DESC LIMIT 1",
                    &[&session_id.to_string(), &agent_id.to_string()],
                )
                .await
                .context("Failed to query latest snapshot")?;

            match row {
                Some(row) => {
                    let json: String = row.get(0);
                    Ok(Some(serde_json::from_str(&json)?))
                }
                None => Ok(None),
            }
        })
    }

    fn get_next_sequence(&self, session_id: SessionId) -> Result<u64> {
        self.runtime.block_on(async {
            let client = self.pool.get().await.context("Failed to get pool connection")?;
            let row = client
                .query_one(
                    "SELECT MAX(sequence) FROM events WHERE session_id = $1",
                    &[&session_id.to_string()],
                )
                .await
                .context("Failed to query max sequence")?;
            let max: Option<i64> = row.get(0);
            Ok(max.map(|s| s as u64 + 1).unwrap_or(0))
        })
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
        info!(%session_id, %agent_id, target_sequence, "Initiating time-travel rollback (Postgres)");

        let base_snapshot = self.runtime.block_on(async {
            let client = self.pool.get().await.context("Failed to get pool connection")?;
            let row = client
                .query_opt(
                    "SELECT snapshot_json FROM snapshots
                     WHERE session_id = $1 AND agent_id = $2 AND sequence_at <= $3
                     ORDER BY sequence_at DESC LIMIT 1",
                    &[&session_id.to_string(), &agent_id.to_string(), &(target_sequence as i64)],
                )
                .await
                .context("Failed to query base snapshot")?;
            match row {
                Some(row) => {
                    let json: String = row.get(0);
                    Ok::<_, anyhow::Error>(Some(serde_json::from_str::<AgentStateSnapshot>(&json)?))
                }
                None => Ok(None),
            }
        })?;

        let start_sequence = base_snapshot.as_ref().map(|s| s.sequence_at_snapshot).unwrap_or(0);

        let replay_events = self.runtime.block_on(async {
            let client = self.pool.get().await.context("Failed to get pool connection")?;
            let rows = client
                .query(
                    "SELECT id, session_id, agent_id, parent_event_id, sequence, timestamp,
                            payload_json, cumulative_tokens, metadata_json
                     FROM events
                     WHERE session_id = $1 AND agent_id = $2
                       AND sequence > $3 AND sequence <= $4
                     ORDER BY sequence ASC",
                    &[
                        &session_id.to_string(),
                        &agent_id.to_string(),
                        &(start_sequence as i64),
                        &(target_sequence as i64),
                    ],
                )
                .await
                .context("Failed to query replay events")?;
            rows.iter().map(row_to_event).collect::<Result<Vec<_>>>()
        })?;

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

fn row_to_event(row: &tokio_postgres::Row) -> Result<Event> {
    let id: String = row.get(0);
    let session_id: String = row.get(1);
    let agent_id: String = row.get(2);
    let parent_event_id: Option<String> = row.get(3);
    let sequence: i64 = row.get(4);
    let timestamp_str: String = row.get(5);
    let payload_json: String = row.get(6);
    let cumulative_tokens: i64 = row.get(7);
    let metadata_json: String = row.get(8);

    let timestamp = chrono::DateTime::parse_from_rfc3339(&timestamp_str)
        .map(|dt| dt.with_timezone(&chrono::Utc))
        .with_context(|| format!("Invalid timestamp in row: {timestamp_str}"))?;

    let payload: EventPayload = serde_json::from_str(&payload_json).unwrap_or(EventPayload::Empty);
    let metadata = serde_json::from_str(&metadata_json).unwrap_or_default();
    let event_type = infer_event_type(&payload);

    Ok(Event {
        id: Uuid::parse_str(&id).unwrap_or_else(|_| Uuid::new_v4()),
        session_id: Uuid::parse_str(&session_id).unwrap_or_else(|_| Uuid::new_v4()),
        agent_id: Uuid::parse_str(&agent_id).unwrap_or_else(|_| Uuid::new_v4()),
        parent_event_id: parent_event_id.and_then(|s| Uuid::parse_str(&s).ok()),
        sequence: sequence as u64,
        timestamp,
        event_type,
        payload,
        cumulative_tokens: cumulative_tokens as u64,
        metadata,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_connection_string() -> String {
        env::var("PIRANHA_TEST_POSTGRES_URL")
            .unwrap_or_else(|_| "postgresql://localhost/piranha_test".to_string())
    }

    #[test]
    fn test_postgres_config_default() {
        let config = PostgresConfig::default();
        assert_eq!(config.port, 5432);
    }

    #[test]
    fn test_postgres_config_parse() {
        let config = PostgresConfig::parse("postgresql://myuser:mypass@myhost:5433/mydb").unwrap();
        assert_eq!(config.host, "myhost");
        assert_eq!(config.port, 5433);
        assert_eq!(config.database, "mydb");
        assert_eq!(config.user, "myuser");
        assert_eq!(config.password, "mypass");
    }

    #[test]
    fn test_connect_and_append_and_retrieve() {
        let store = PostgresEventStore::new(Some(test_connection_string())).unwrap();
        assert!(store.is_connected());

        let session_id = Uuid::new_v4();
        let agent_id = Uuid::new_v4();
        let event = Event {
            id: Uuid::new_v4(),
            session_id,
            agent_id,
            parent_event_id: None,
            sequence: 0,
            timestamp: Utc::now(),
            event_type: crate::types::EventType::LlmCall,
            payload: EventPayload::LlmCall(crate::types::LlmCallPayload {
                model: "llama3".to_string(),
                prompt_tokens: 100,
                completion_tokens: 50,
                cost_usd: 0.01,
                context_event_count: 5,
                cache_hit: false,
                cache_key_hash: None,
            }),
            cumulative_tokens: 150,
            metadata: Default::default(),
        };

        store.append(event.clone()).unwrap();
        let retrieved = store.get_events_for_session(session_id).unwrap();
        assert_eq!(retrieved.len(), 1);
        assert_eq!(retrieved[0].id, event.id);

        let next_seq = store.get_next_sequence(session_id).unwrap();
        assert_eq!(next_seq, 1);

        let report = store.build_cost_report(session_id).unwrap();
        assert_eq!(report.llm_calls, 1);
        assert_eq!(report.total_tokens, 150);
    }

    #[test]
    fn test_connection_string_actually_used() {
        // Regression test: new() used to silently ignore the connection
        // string and always connect to hardcoded defaults.
        let store = PostgresEventStore::new(Some(
            "postgresql://someuser:somepass@somehost:9999/somedb".to_string(),
        ));
        // Won't actually connect (host doesn't exist), but must fail *because*
        // it tried to reach somehost:9999, not silently succeed against
        // localhost:5432 like before.
        assert!(store.is_err());
    }
}
