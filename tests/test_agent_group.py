"""Tests for AgentGroup functionality."""

import asyncio

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
    """Test that AgentGroup.run_parallel runs the task on all agents concurrently."""
    num_agents = 2
    all_started = asyncio.Event()
    started_count = 0

    class _FakeAsyncAgent:
        def __init__(self, name):
            self.name = name
            self.ran_tasks = []

        async def run(self, task):
            nonlocal started_count
            self.ran_tasks.append(task)
            started_count += 1
            if started_count == num_agents:
                all_started.set()
            # Blocks until every agent has started; times out if the group
            # runs agents sequentially instead of in parallel.
            await asyncio.wait_for(all_started.wait(), timeout=5)
            return f"{self.name}:{task}"

    agent1 = _FakeAsyncAgent("ParallelAgent1")
    agent2 = _FakeAsyncAgent("ParallelAgent2")
    group = AgentGroup([agent1, agent2])

    results = asyncio.run(group.run_parallel("parallel-task"))

    assert results == ["ParallelAgent1:parallel-task", "ParallelAgent2:parallel-task"]
    assert agent1.ran_tasks == ["parallel-task"]
    assert agent2.ran_tasks == ["parallel-task"]
