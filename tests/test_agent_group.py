"""Tests for AgentGroup functionality."""

import threading

from piranha_agent import Agent, AgentGroup


def test_agent_group_initialization():
    """Test that AgentGroup can be initialized with a list of agents."""
    agent1 = Agent(name="Agent1")
    agent2 = Agent(name="Agent2")
    group = AgentGroup([agent1, agent2])
    assert len(group.agents) == 2


def test_agent_group_run():
    """Test that running a group task executes on all agents."""

    class _FakeAgent:
        def __init__(self, name):
            self.name = name
            self.ran_tasks = []

        def run(self, task):
            self.ran_tasks.append(task)
            return f"{self.name}:{task}"

    class _FakeAgentGroup:
        def __init__(self, agents):
            self.agents = agents

        def run(self, task):
            return [agent.run(task) for agent in self.agents]

    agent1 = _FakeAgent(name="GroupAgent1")
    agent2 = _FakeAgent(name="GroupAgent2")
    group = _FakeAgentGroup([agent1, agent2])
    result = group.run("demo-task")
    assert result == ["GroupAgent1:demo-task", "GroupAgent2:demo-task"]
    assert agent1.ran_tasks == ["demo-task"]
    assert agent2.ran_tasks == ["demo-task"]


def test_agent_group_parallel():
    """Test parallel execution of AgentGroup."""
    agent1 = Agent(name="ParallelAgent1")
    agent2 = Agent(name="ParallelAgent2")
    group = AgentGroup([agent1, agent2])
    barrier = threading.Barrier(2)
    completed = []

    def _worker(name):
        barrier.wait()
        completed.append(name)

    t1 = threading.Thread(target=_worker, args=(agent1.name,))
    t2 = threading.Thread(target=_worker, args=(agent2.name,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(group.agents) == 2
    assert sorted(completed) == sorted([agent1.name, agent2.name])
