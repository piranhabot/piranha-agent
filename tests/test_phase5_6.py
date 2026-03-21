"""Tests for Phase 5: PostgreSQL Backend and Phase 6: Distributed Agents."""

import pytest
from piranha import PostgresEventStore, AgentOrchestrator, DistributedAgent


class TestPhase5PostgresStore:
    """Tests for PostgreSQL Event Store (Phase 5)."""

    def test_postgres_store_creation(self):
        """Test creating PostgreSQL event store."""
        store = PostgresEventStore()
        assert store is not None

    def test_postgres_store_with_connection_string(self):
        """Test creating PostgreSQL store with connection string."""
        store = PostgresEventStore(connection_string="postgresql://localhost/test")
        assert store is not None

    def test_postgres_store_info(self):
        """Test PostgreSQL store info method."""
        store = PostgresEventStore()
        info = store.get_info()
        assert "PostgreSQL" in info
        assert "Phase 5" in info


class TestPhase6DistributedAgents:
    """Tests for Distributed Agents (Phase 6)."""

    def test_orchestrator_creation(self):
        """Test creating agent orchestrator."""
        orchestrator = AgentOrchestrator()
        assert orchestrator is not None

    def test_orchestrator_with_queue_size(self):
        """Test creating orchestrator with custom queue size."""
        orchestrator = AgentOrchestrator(queue_size=50)
        assert orchestrator is not None

    def test_distributed_agent_creation(self):
        """Test creating distributed agent."""
        agent = DistributedAgent("agent-1")
        assert agent is not None
        assert agent.get_id() == "agent-1"

    def test_distributed_agent_info(self):
        """Test distributed agent info method."""
        agent = DistributedAgent("test-agent")
        info = agent.get_info()
        assert "Distributed Agent" in info
        assert "Phase 6" in info

    def test_orchestrator_submit_task(self):
        """Test submitting task to orchestrator."""
        orchestrator = AgentOrchestrator()
        task_id = orchestrator.submit_task("Test task description", 5)
        assert task_id is not None
        assert "task-pending" in task_id

    def test_orchestrator_cluster_status(self):
        """Test getting cluster status."""
        orchestrator = AgentOrchestrator()
        status = orchestrator.get_cluster_status()
        assert isinstance(status, str)

    def test_distributed_agent_with_unique_id(self):
        """Test creating multiple agents with unique IDs."""
        agent1 = DistributedAgent("worker-1")
        agent2 = DistributedAgent("worker-2")
        agent3 = DistributedAgent("worker-3")
        
        assert agent1.get_id() == "worker-1"
        assert agent2.get_id() == "worker-2"
        assert agent3.get_id() == "worker-3"
        assert agent1.get_id() != agent2.get_id()

    def test_orchestrator_task_priority(self):
        """Test task submission with different priorities."""
        orchestrator = AgentOrchestrator()
        
        task1 = orchestrator.submit_task("Low priority", 1)
        task2 = orchestrator.submit_task("High priority", 10)
        
        assert task1 is not None
        assert task2 is not None

    def test_multiple_agents_with_orchestrator(self):
        """Test multiple agents with single orchestrator."""
        orchestrator = AgentOrchestrator(queue_size=10)
        
        agents = []
        for i in range(5):
            agent = DistributedAgent(f"agent-{i}")
            agents.append(agent)
        
        assert len(agents) == 5
        ids = [a.get_id() for a in agents]
        assert len(set(ids)) == 5  # All unique


class TestPhase5Phase6Integration:
    """Integration tests for Phase 5 and Phase 6."""

    def test_postgres_and_distributed_agents(self):
        """Test using PostgreSQL store with distributed agents."""
        # Phase 5
        store = PostgresEventStore()
        assert store is not None
        
        # Phase 6
        orchestrator = AgentOrchestrator()
        agent = DistributedAgent("integration-agent")
        assert orchestrator is not None
        assert agent is not None

    def test_system_info(self):
        """Test system information for both phases."""
        store = PostgresEventStore()
        agent = DistributedAgent("info-agent")
        
        store_info = store.get_info()
        agent_info = agent.get_info()
        
        assert "Phase 5" in store_info
        assert "Phase 6" in agent_info
