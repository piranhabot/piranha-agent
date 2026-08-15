"""Tests for Phase 5: PostgreSQL Backend and Phase 6: Distributed Agents."""

import os
import uuid

import pytest
from piranha_agent import AgentOrchestrator, DistributedAgent, PostgresEventStore

# PostgresEventStore now makes a real connection (it used to be a stub that
# never touched a database). These tests need a real, reachable Postgres -
# skip cleanly rather than fail on machines/CI without one.
_TEST_POSTGRES_URL = os.environ.get(
    "PIRANHA_TEST_POSTGRES_URL", "postgresql://localhost/piranha_test"
)


def _make_store() -> PostgresEventStore:
    try:
        return PostgresEventStore(connection_string=_TEST_POSTGRES_URL)
    except RuntimeError as e:
        pytest.skip(f"No reachable Postgres for integration tests: {e}")


class TestPhase5PostgresStore:
    """Tests for PostgreSQL Event Store (Phase 5)."""

    def test_postgres_store_creation(self):
        """Test creating PostgreSQL event store."""
        store = _make_store()
        assert store is not None

    def test_postgres_store_with_connection_string(self):
        """Test creating PostgreSQL store with connection string."""
        store = _make_store()
        assert store is not None

    def test_postgres_store_info(self):
        """Test PostgreSQL store info method."""
        store = _make_store()
        info = store.get_info()
        assert "PostgreSQL" in info
        assert "Phase 5" in info
        assert "Connected: true" in info

    def test_bad_connection_string_actually_fails(self):
        """Regression test: new() used to silently ignore the connection
        string and always report success against hardcoded defaults."""
        with pytest.raises(RuntimeError):
            PostgresEventStore(
                connection_string="postgresql://baduser:badpass@nonexistent-host-xyz:9999/db"
            )

    def test_record_llm_call_and_cost_report(self):
        """Test that events genuinely persist and aggregate, end-to-end."""
        store = _make_store()
        session_id = str(uuid.uuid4())
        agent_id = str(uuid.uuid4())

        event_id = store.record_llm_call(
            session_id, agent_id, "llama3", 100, 50, 0.01, False, 5
        )
        assert event_id

        report = store.get_cost_report(session_id)
        assert report["llm_calls"] == 1
        assert report["total_tokens"] == 150
        assert report["total_cost_usd"] == pytest.approx(0.01)

    def test_export_trace_contains_recorded_event(self):
        store = _make_store()
        session_id = str(uuid.uuid4())
        agent_id = str(uuid.uuid4())
        event_id = store.record_llm_call(
            session_id, agent_id, "llama3", 10, 5, 0.001, False, 1
        )

        trace = store.export_trace(session_id)
        assert event_id in trace
        assert session_id in trace


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
        """Test submitting task to orchestrator actually enqueues it."""
        orchestrator = AgentOrchestrator()
        task_id = orchestrator.submit_task("Test task description", 5)
        assert task_id is not None
        assert task_id.startswith("task-")

        task = orchestrator.get_task(task_id)
        assert task is not None
        assert task["description"] == "Test task description"
        assert task["priority"] == 5
        assert task["status"] == "Pending"

    def test_orchestrator_submit_task_rejects_when_queue_full(self):
        orchestrator = AgentOrchestrator(queue_size=1)
        orchestrator.submit_task("first", 1)
        with pytest.raises(RuntimeError):
            orchestrator.submit_task("second", 1)

    def test_orchestrator_cluster_status(self):
        """Test getting cluster status reflects real registered workers."""
        orchestrator = AgentOrchestrator()
        assert orchestrator.get_cluster_status() == {}

        orchestrator.register_worker("worker-1")
        orchestrator.register_worker("worker-2")
        status = orchestrator.get_cluster_status()
        assert isinstance(status, dict)
        assert set(status.keys()) == {"worker-1", "worker-2"}
        assert status["worker-1"] == "Idle"

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

        task1_id = orchestrator.submit_task("Low priority", 1)
        task2_id = orchestrator.submit_task("High priority", 10)

        assert task1_id is not None
        assert task2_id is not None
        assert task1_id != task2_id
        assert orchestrator.get_task(task1_id)["priority"] == 1
        assert orchestrator.get_task(task2_id)["priority"] == 10

    def test_multiple_agents_with_orchestrator(self):
        """Test multiple agents with single orchestrator."""
        orchestrator = AgentOrchestrator(queue_size=10)
        
        _agents = []
        for i in range(5):
            agent = DistributedAgent(f"agent-{i}")
            _agents.append(agent)
            orchestrator.register_worker(agent.get_id())
        
        assert len(_agents) == 5
        _ids = [a.get_id() for a in _agents]
        assert len(set(_ids)) == 5  # All unique


class TestPhase5Phase6Integration:
    """Integration tests for Phase 5 and Phase 6."""

    def test_postgres_and_distributed_agents(self):
        """Test using PostgreSQL store with distributed agents."""
        # Phase 5
        store = _make_store()
        assert store is not None

        # Phase 6
        orchestrator = AgentOrchestrator()
        agent = DistributedAgent("integration-agent")
        assert orchestrator is not None
        assert agent is not None

    def test_system_info(self):
        """Test system information for both phases."""
        store = _make_store()
        agent = DistributedAgent("info-agent")
        
        store_info = store.get_info()
        agent_info = agent.get_info()
        
        assert "Phase 5" in store_info
        assert "Phase 6" in agent_info
