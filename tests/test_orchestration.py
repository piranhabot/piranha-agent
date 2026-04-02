from unittest.mock import MagicMock

from piranha_agent.agent import Agent
from piranha_agent.orchestration import create_orchestrated_team


def test_orchestrated_team_creation():
    team = create_orchestrated_team("TestTeam")
    assert team.name == "TestTeam"
    assert team.coordinator.name == "coordinator"
    assert "delegate_task" in [s.name for s in team.coordinator.skills]
    assert "get_team_status" in [s.name for s in team.coordinator.skills]

def test_delegation_mock():
    team = create_orchestrated_team("TestTeam")
    coordinator = team.coordinator
    
    # Mock Agent.run to avoid actual LLM calls
    # We need to mock it on the Agent class or the instance
    with MagicMock() as mock_run:
        mock_run.return_value.content = "Sub-agent result"
        Agent.run = mock_run
        
        # Find the delegate_task skill
        delegate_skill = next(s for s in coordinator.skills if s.name == "delegate_task")
        
        # Call the skill
        result = delegate_skill(agent_name="researcher", task_description="Research AI", role="researcher")
        
        assert "researcher" in [a.name for a in team.members.values()]
        assert "Task completed by researcher" in result
        assert "Sub-agent result" in result

def test_team_status_skill():
    team = create_orchestrated_team("TestTeam")
    coordinator = team.coordinator
    
    # Add a member
    researcher = Agent(name="researcher")
    team.add_member(researcher, "researcher")
    
    # Find the skill
    status_skill = next(s for s in coordinator.skills if s.name == "get_team_status")
    status_report = status_skill()
    
    assert "TestTeam" in status_report
    assert "coordinator (Coordinator)" in status_report
    assert "researcher" in status_report

def test_message_bus_broadcasting():
    team = create_orchestrated_team("TestTeam")
    coordinator = team.coordinator
    
    # Find the broadcast skill
    broadcast_skill = next(s for s in coordinator.skills if s.name == "broadcast_message")
    
    # Track bus messages
    bus_messages = []
    team.message_bus.subscribe("broadcast", lambda e: bus_messages.append(e))
    
    broadcast_skill(message="Hello Team!")
    
    assert len(bus_messages) == 1
    assert bus_messages[0]["message"] == "Hello Team!"
    assert bus_messages[0]["sender"] == "coordinator"
