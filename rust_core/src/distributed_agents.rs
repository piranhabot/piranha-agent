// rust_core/src/distributed_agents.rs
//
// Phase 6: Distributed Agents
//

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::info;

/// Agent status in distributed system
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AgentStatus {
    Idle,
    Busy,
    Offline,
}

/// Worker agent in distributed system
pub struct WorkerAgent {
    pub id: String,
    pub status: AgentStatus,
    pub tasks_completed: u64,
}

/// Orchestrator for distributed agents
pub struct AgentOrchestrator {
    workers: Arc<RwLock<HashMap<String, WorkerAgent>>>,
    next_task_id: Arc<RwLock<u64>>,
}

impl AgentOrchestrator {
    /// Create a new agent orchestrator
    pub fn new(_queue_size: usize) -> Self {
        Self {
            workers: Arc::new(RwLock::new(HashMap::new())),
            next_task_id: Arc::new(RwLock::new(0)),
        }
    }

    /// Register a worker agent
    pub async fn register_worker(&self, agent_id: String) {
        let mut workers = self.workers.write().await;
        workers.insert(
            agent_id.clone(),
            WorkerAgent {
                id: agent_id.clone(),
                status: AgentStatus::Idle,
                tasks_completed: 0,
            },
        );
        info!("Registered worker agent: {}", agent_id);
    }

    /// Get cluster status
    pub async fn get_cluster_status(&self) -> HashMap<String, AgentStatus> {
        let workers = self.workers.read().await;
        workers
            .iter()
            .map(|(id, worker)| (id.clone(), worker.status.clone()))
            .collect()
    }

    /// Get task ID
    pub async fn get_next_task_id(&self) -> u64 {
        let mut next_id = self.next_task_id.write().await;
        *next_id += 1;
        *next_id
    }
}

/// Distributed agent that can work across processes/machines
pub struct DistributedAgent {
    pub id: String,
}

impl DistributedAgent {
    /// Create a new distributed agent
    pub fn new(id: String) -> Self {
        Self { id }
    }

    /// Get agent info
    pub fn get_info(&self) -> String {
        format!("Distributed Agent {} (Phase 6)", self.id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_orchestrator_creation() {
        let orchestrator = AgentOrchestrator::new(100);
        let status = orchestrator.get_cluster_status().await;
        assert!(status.is_empty());
    }

    #[tokio::test]
    async fn test_worker_registration() {
        let orchestrator = AgentOrchestrator::new(100);
        orchestrator.register_worker("worker-1".to_string()).await;
        
        let status = orchestrator.get_cluster_status().await;
        assert_eq!(status.len(), 1);
    }

    #[tokio::test]
    async fn test_distributed_agent() {
        let agent = DistributedAgent::new("test-agent".to_string());
        assert_eq!(agent.id, "test-agent");
        assert!(agent.get_info().contains("Phase 6"));
    }
}
