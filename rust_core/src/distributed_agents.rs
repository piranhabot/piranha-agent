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

/// A task submitted to the orchestrator's queue
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Task {
    pub id: String,
    pub description: String,
    pub priority: u8,
    pub status: TaskStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TaskStatus {
    Pending,
    Assigned,
    Completed,
}

/// Orchestrator for distributed agents
pub struct AgentOrchestrator {
    workers: Arc<RwLock<HashMap<String, WorkerAgent>>>,
    next_task_id: Arc<RwLock<u64>>,
    tasks: Arc<RwLock<HashMap<String, Task>>>,
    queue_size: usize,
}

impl AgentOrchestrator {
    /// Create a new agent orchestrator
    pub fn new(queue_size: usize) -> Self {
        Self {
            workers: Arc::new(RwLock::new(HashMap::new())),
            next_task_id: Arc::new(RwLock::new(0)),
            tasks: Arc::new(RwLock::new(HashMap::new())),
            queue_size,
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

    /// Submit a task to the queue. Returns the new task's ID, or an error if
    /// the queue is already at capacity.
    pub async fn submit_task(&self, description: String, priority: u8) -> Result<String, String> {
        let mut tasks = self.tasks.write().await;

        let pending_count = tasks
            .values()
            .filter(|t| t.status == TaskStatus::Pending)
            .count();
        if pending_count >= self.queue_size {
            return Err(format!(
                "Task queue is full ({}/{} pending tasks)",
                pending_count, self.queue_size
            ));
        }

        let task_id = self.get_next_task_id().await;
        let id = format!("task-{task_id}");
        tasks.insert(
            id.clone(),
            Task {
                id: id.clone(),
                description,
                priority,
                status: TaskStatus::Pending,
            },
        );
        info!("Task submitted: {}", id);
        Ok(id)
    }

    /// Get a task by ID.
    pub async fn get_task(&self, task_id: &str) -> Option<Task> {
        let tasks = self.tasks.read().await;
        tasks.get(task_id).cloned()
    }

    /// Get all tasks currently tracked by the orchestrator.
    pub async fn get_all_tasks(&self) -> Vec<Task> {
        let tasks = self.tasks.read().await;
        tasks.values().cloned().collect()
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
    async fn test_submit_task_returns_real_sequential_id() {
        let orchestrator = AgentOrchestrator::new(100);
        let id1 = orchestrator.submit_task("first".to_string(), 5).await.unwrap();
        let id2 = orchestrator.submit_task("second".to_string(), 5).await.unwrap();
        assert_ne!(id1, id2);

        let task1 = orchestrator.get_task(&id1).await.unwrap();
        assert_eq!(task1.description, "first");
        assert_eq!(task1.priority, 5);
        assert_eq!(task1.status, TaskStatus::Pending);
    }

    #[tokio::test]
    async fn test_submit_task_rejects_when_queue_full() {
        let orchestrator = AgentOrchestrator::new(2);
        orchestrator.submit_task("a".to_string(), 1).await.unwrap();
        orchestrator.submit_task("b".to_string(), 1).await.unwrap();
        let result = orchestrator.submit_task("c".to_string(), 1).await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_distributed_agent() {
        let agent = DistributedAgent::new("test-agent".to_string());
        assert_eq!(agent.id, "test-agent");
        assert!(agent.get_info().contains("Phase 6"));
    }
}
