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
    pub assigned_to: Option<String>,
    /// Submission order, used to break priority ties (earliest wins).
    pub sequence: u64,
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
                assigned_to: None,
                sequence: task_id,
            },
        );
        info!("Task submitted: {}", id);
        Ok(id)
    }

    /// Assign the highest-priority pending task (earliest submitted wins
    /// ties) to the given worker, if that worker is currently idle and a
    /// pending task exists. Returns Ok(None) if there's nothing to assign
    /// (worker busy/offline, or no pending tasks) - that's a normal outcome,
    /// not an error. Returns Err only if the worker doesn't exist.
    pub async fn assign_task_to_worker(&self, worker_id: &str) -> Result<Option<Task>, String> {
        {
            let workers = self.workers.read().await;
            match workers.get(worker_id) {
                None => return Err(format!("Worker '{worker_id}' not found")),
                Some(w) if w.status != AgentStatus::Idle => return Ok(None),
                _ => {}
            }
        }

        let assigned_task = {
            let mut tasks = self.tasks.write().await;
            let next_task_id = tasks
                .values()
                .filter(|t| t.status == TaskStatus::Pending)
                .max_by_key(|t| (t.priority, std::cmp::Reverse(t.sequence)))
                .map(|t| t.id.clone());

            let Some(task_id) = next_task_id else {
                return Ok(None);
            };

            let task = tasks
                .get_mut(&task_id)
                .expect("task_id came from this same map");
            task.status = TaskStatus::Assigned;
            task.assigned_to = Some(worker_id.to_string());
            task.clone()
        };

        let mut workers = self.workers.write().await;
        if let Some(w) = workers.get_mut(worker_id) {
            w.status = AgentStatus::Busy;
        }

        info!("Assigned task {} to worker {}", assigned_task.id, worker_id);
        Ok(Some(assigned_task))
    }

    /// Try to assign a pending task to every currently-idle worker.
    /// Returns (worker_id, task_id) pairs for everything actually assigned.
    pub async fn auto_assign(&self) -> Vec<(String, String)> {
        let idle_worker_ids: Vec<String> = {
            let workers = self.workers.read().await;
            workers
                .values()
                .filter(|w| w.status == AgentStatus::Idle)
                .map(|w| w.id.clone())
                .collect()
        };

        let mut assigned = Vec::new();
        for worker_id in idle_worker_ids {
            if let Ok(Some(task)) = self.assign_task_to_worker(&worker_id).await {
                assigned.push((worker_id, task.id));
            }
        }
        assigned
    }

    /// Mark an assigned task as completed, freeing its worker back to Idle
    /// and incrementing that worker's completed-task count.
    pub async fn complete_task(&self, task_id: &str) -> Result<(), String> {
        let worker_id = {
            let mut tasks = self.tasks.write().await;
            let task = tasks
                .get_mut(task_id)
                .ok_or_else(|| format!("Task '{task_id}' not found"))?;
            if task.status != TaskStatus::Assigned {
                return Err(format!(
                    "Task '{}' is not currently assigned (status: {:?})",
                    task_id, task.status
                ));
            }
            task.status = TaskStatus::Completed;
            task.assigned_to.clone()
        };

        if let Some(worker_id) = worker_id {
            let mut workers = self.workers.write().await;
            if let Some(w) = workers.get_mut(&worker_id) {
                w.status = AgentStatus::Idle;
                w.tasks_completed += 1;
            }
        }

        info!("Task {} completed", task_id);
        Ok(())
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
    async fn test_assign_task_to_idle_worker() {
        let orchestrator = AgentOrchestrator::new(100);
        orchestrator.register_worker("worker-1".to_string()).await;
        let task_id = orchestrator.submit_task("do a thing".to_string(), 5).await.unwrap();

        let assigned = orchestrator.assign_task_to_worker("worker-1").await.unwrap();
        let assigned = assigned.expect("should have assigned the pending task");
        assert_eq!(assigned.id, task_id);
        assert_eq!(assigned.status, TaskStatus::Assigned);
        assert_eq!(assigned.assigned_to, Some("worker-1".to_string()));

        let status = orchestrator.get_cluster_status().await;
        assert_eq!(status["worker-1"], AgentStatus::Busy);
    }

    #[tokio::test]
    async fn test_assign_task_prefers_higher_priority() {
        let orchestrator = AgentOrchestrator::new(100);
        orchestrator.register_worker("worker-1".to_string()).await;
        let low = orchestrator.submit_task("low".to_string(), 1).await.unwrap();
        let high = orchestrator.submit_task("high".to_string(), 9).await.unwrap();

        let assigned = orchestrator.assign_task_to_worker("worker-1").await.unwrap().unwrap();
        assert_eq!(assigned.id, high);

        // low priority task should still be pending
        let low_task = orchestrator.get_task(&low).await.unwrap();
        assert_eq!(low_task.status, TaskStatus::Pending);
    }

    #[tokio::test]
    async fn test_assign_task_ties_broken_by_submission_order() {
        let orchestrator = AgentOrchestrator::new(100);
        orchestrator.register_worker("worker-1".to_string()).await;
        let first = orchestrator.submit_task("first".to_string(), 5).await.unwrap();
        let _second = orchestrator.submit_task("second".to_string(), 5).await.unwrap();

        let assigned = orchestrator.assign_task_to_worker("worker-1").await.unwrap().unwrap();
        assert_eq!(assigned.id, first);
    }

    #[tokio::test]
    async fn test_assign_task_returns_none_when_worker_busy() {
        let orchestrator = AgentOrchestrator::new(100);
        orchestrator.register_worker("worker-1".to_string()).await;
        orchestrator.submit_task("a".to_string(), 1).await.unwrap();
        orchestrator.submit_task("b".to_string(), 1).await.unwrap();

        orchestrator.assign_task_to_worker("worker-1").await.unwrap(); // now busy
        let second_attempt = orchestrator.assign_task_to_worker("worker-1").await.unwrap();
        assert!(second_attempt.is_none());
    }

    #[tokio::test]
    async fn test_assign_task_unknown_worker_is_error() {
        let orchestrator = AgentOrchestrator::new(100);
        let result = orchestrator.assign_task_to_worker("nonexistent").await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_complete_task_frees_worker_and_increments_count() {
        let orchestrator = AgentOrchestrator::new(100);
        orchestrator.register_worker("worker-1".to_string()).await;
        let task_id = orchestrator.submit_task("do a thing".to_string(), 5).await.unwrap();
        orchestrator.assign_task_to_worker("worker-1").await.unwrap();

        orchestrator.complete_task(&task_id).await.unwrap();

        let task = orchestrator.get_task(&task_id).await.unwrap();
        assert_eq!(task.status, TaskStatus::Completed);

        let status = orchestrator.get_cluster_status().await;
        assert_eq!(status["worker-1"], AgentStatus::Idle);
    }

    #[tokio::test]
    async fn test_complete_task_rejects_unassigned_task() {
        let orchestrator = AgentOrchestrator::new(100);
        let task_id = orchestrator.submit_task("not assigned".to_string(), 5).await.unwrap();
        let result = orchestrator.complete_task(&task_id).await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_auto_assign_distributes_across_idle_workers() {
        let orchestrator = AgentOrchestrator::new(100);
        orchestrator.register_worker("worker-1".to_string()).await;
        orchestrator.register_worker("worker-2".to_string()).await;
        orchestrator.submit_task("a".to_string(), 1).await.unwrap();
        orchestrator.submit_task("b".to_string(), 1).await.unwrap();

        let assigned = orchestrator.auto_assign().await;
        assert_eq!(assigned.len(), 2);

        let status = orchestrator.get_cluster_status().await;
        assert_eq!(status["worker-1"], AgentStatus::Busy);
        assert_eq!(status["worker-2"], AgentStatus::Busy);
    }

    #[tokio::test]
    async fn test_auto_assign_no_idle_workers_assigns_nothing() {
        let orchestrator = AgentOrchestrator::new(100);
        orchestrator.submit_task("a".to_string(), 1).await.unwrap();
        let assigned = orchestrator.auto_assign().await;
        assert!(assigned.is_empty());
    }

    #[tokio::test]
    async fn test_distributed_agent() {
        let agent = DistributedAgent::new("test-agent".to_string());
        assert_eq!(agent.id, "test-agent");
        assert!(agent.get_info().contains("Phase 6"));
    }
}
