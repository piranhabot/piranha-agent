"""Tests for SkillRegistry functionality."""

import pytest
from piranha_agent import Agent
from piranha_agent.skill import skill


@skill(name="test_skill", description="A test skill")
def test_skill():
    return "Test skill result"


def test_skill_registry():
    """Test that skills can be registered with an agent."""
    agent = Agent(name="RegistryAgent")
    agent.add_skill(test_skill)
    assert len(agent.skills) == 1
