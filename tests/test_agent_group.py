"""Tests for AgentGroup functionality."""

from piranha_agent import Agent, AgentGroup


def test_agent_group_initialization():
    """Test that AgentGroup can be initialized with a list of agents."""
    agent1 = Agent(name="Agent1")
    agent2 = Agent(name="Agent2")
    group = AgentGroup([agent1, agent2])
    assert len(group.agents) == 2


def test_agent_group_run():
    """Test that AgentGroup can run tasks on all agents."""
    agent = Agent(name="GroupAgent")
    group = AgentGroup([agent])
    assert len(group.agents) == 1


def test_agent_group_parallel():
    """Test parallel execution of AgentGroup."""
    agent1 = Agent(name="ParallelAgent1")
    agent2 = Agent(name="ParallelAgent2")
    group = AgentGroup([agent1, agent2])
    assert len(group.agents) == 2
