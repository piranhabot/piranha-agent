import os

from piranha_agent.collaboration import PersistentMessageBus, PersistentSharedState
from piranha_agent.orchestration import create_orchestrated_team


def test_persistent_shared_state():
    db_name = "test_state.db"
    if os.path.exists(db_name):
        os.remove(db_name)
        
    # 1. Set values
    state = PersistentSharedState(db_path=db_name)
    state.set("goal", "build piranha")
    state.set("progress", 0.5)
    
    # 2. Re-instantiate and check
    state2 = PersistentSharedState(db_path=db_name)
    assert state2.get("goal") == "build piranha"
    assert state2.get("progress") == 0.5
    
    os.remove(db_name)

def test_persistent_message_bus():
    db_name = "test_bus.db"
    if os.path.exists(db_name):
        os.remove(db_name)
        
    # 1. Publish messages
    bus = PersistentMessageBus(db_path=db_name)
    bus.publish("news", "agent1", "Hello world")
    bus.publish("status", "agent2", {"status": "ok"})
    
    # 2. Re-instantiate and check history
    bus2 = PersistentMessageBus(db_path=db_name)
    assert len(bus2._history) == 2
    assert bus2._history[0]["sender"] == "agent1"
    assert bus2._history[1]["message"] == {"status": "ok"}
    
    os.remove(db_name)

def test_persistent_orchestrated_team():
    team_name = "PersistentTeam"
    state_db = f"{team_name}_state.db"
    msg_db = f"{team_name}_messages.db"
    
    for db in [state_db, msg_db]:
        if os.path.exists(db):
            os.remove(db)
            
    # 1. Create team and set state
    team = create_orchestrated_team(team_name, is_persistent=True)
    team.shared_state.set("key", "value")
    team.message_bus.publish("test", "coordinator", "ping")
    
    # 2. Re-create and verify
    team2 = create_orchestrated_team(team_name, is_persistent=True)
    assert team2.shared_state.get("key") == "value"
    assert len(team2.message_bus._history) == 1
    
    for db in [state_db, msg_db]:
        if os.path.exists(db):
            os.remove(db)
