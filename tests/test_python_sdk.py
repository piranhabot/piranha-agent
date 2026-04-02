"""Tests for Piranha Python SDK."""

import pytest
from piranha_agent import Agent, Session, Skill, Task
from piranha_agent.skill import skill


class TestAgent:
    """Tests for the Agent class."""

    def test_create_agent(self):
        """Test creating an agent."""
        agent = Agent(name="test", model="gpt-4")
        assert agent.name == "test"
        assert agent.model == "gpt-4"
        assert agent.id is not None
        assert len(agent.id) > 0

    def test_agent_default_values(self):
        """Test agent default values."""
        agent = Agent(name="default")
        assert agent.model == "ollama/llama3:latest"
        assert agent.description == ""
        assert agent.system_prompt == ""
        assert agent.skills == []

    def test_agent_with_skills(self):
        """Test creating an agent with skills."""
        @skill(description="Test skill")
        def test_func():
            return "test"
        
        agent = Agent(name="skilled", skills=[test_func])
        assert len(agent.skills) == 1
        assert agent.skills[0].name == "test_func"

    def test_agent_add_skill(self):
        """Test adding a skill to an agent."""
        agent = Agent(name="learner")
        new_skill = Skill(name="new_skill", description="A new skill")
        agent.add_skill(new_skill)
        assert len(agent.skills) == 1
        assert agent.skills[0].name == "new_skill"

    def test_agent_run(self):
        """Test running a task with an agent."""
        agent = Agent(name="runner")
        response = agent.run("Test task")
        assert response.content is not None
        assert len(response.content) > 0
        assert response.model == "ollama/llama3:latest"

    def test_agent_chat(self):
        """Test chatting with an agent."""
        agent = Agent(name="chatbot")
        response = agent.chat("Hello")
        assert isinstance(response, str)

    def test_agent_session(self):
        """Test agent has a session."""
        agent = Agent(name="session_test")
        assert agent.session is not None
        assert agent.session.id is not None


class TestTask:
    """Tests for the Task class."""

    def test_create_task(self):
        """Test creating a task."""
        agent = Agent(name="test")
        task = Task(description="Test task", agent=agent)
        assert task.description == "Test task"
        assert task.agent == agent

    def test_task_run(self):
        """Test running a task."""
        agent = Agent(name="worker")
        task = Task(description="Do something", agent=agent)
        result = task.run()
        assert result.success is True
        assert result.result is not None

    def test_task_with_context(self):
        """Test task with context."""
        agent = Agent(name="contextual")
        task = Task(
            description="Process this",
            agent=agent,
            context="Some context",
            expected_output="Expected output",
        )
        result = task.run()
        assert result.success is True

    def test_task_with_subtasks(self):
        """Test task with subtasks."""
        agent = Agent(name="manager")
        parent = Task(description="Parent task", agent=agent)
        child = parent.add_subtask("Child task")
        assert len(parent._subtasks) == 1
        assert child.parent == parent

    def test_task_result_string(self):
        """Test task result string representation."""
        agent = Agent(name="test")
        task = Task(description="Test", agent=agent)
        result = task.run()
        result_str = str(result)
        assert result_str.startswith("[")


class TestSession:
    """Tests for the Session class."""

    def test_create_session(self):
        """Test creating a session."""
        session = Session.create()
        assert session.id is not None
        assert len(session.id) > 0

    def test_session_id_is_uuid(self):
        """Test session ID is a valid UUID format."""
        session = Session.create()
        # UUID format: 8-4-4-4-12 hex chars
        parts = session.id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8

    def test_session_export_trace(self):
        """Test exporting session trace."""
        session = Session.create()
        trace = session.export_trace()
        assert isinstance(trace, str)
        assert len(trace) > 0


class TestSkill:
    """Tests for the Skill class."""

    def test_create_skill(self):
        """Test creating a skill."""
        skill = Skill(name="test", description="A test skill")
        assert skill.name == "test"
        assert skill.description == "A test skill"
        assert skill.inheritable is True

    def test_skill_id_generation(self):
        """Test skill ID generation."""
        skill1 = Skill(name="unique", description="desc")
        skill2 = Skill(name="unique", description="desc")
        assert skill1.id != skill2.id  # IDs should be unique

    def test_skill_to_dict(self):
        """Test skill to_dict method."""
        skill = Skill(
            name="dict_test",
            description="Test",
            parameters_schema={"type": "object"},
            required_permissions=["read"],
            inheritable=False,
        )
        d = skill.to_dict()
        assert d["name"] == "dict_test"
        assert d["description"] == "Test"
        assert d["inheritable"] is False

    def test_skill_decorator(self):
        """Test skill decorator."""
        @skill(name="decorated", description="Decorated skill")
        def my_func():
            return "result"
        
        assert my_func.name == "decorated"
        assert my_func.description == "Decorated skill"
        assert my_func() == "result"

    def test_skill_call(self):
        """Test calling a skill."""
        def add(a, b):
            return a + b
        
        skill = Skill(name="adder", description="Adds numbers", function=add)
        result = skill(2, 3)
        assert result == 5

    def test_skill_without_function(self):
        """Test calling skill without function raises error."""
        skill = Skill(name="empty", description="No function")
        with pytest.raises(RuntimeError):
            skill()


class TestAgentResponse:
    """Tests for the AgentResponse class."""

    def test_response_creation(self):
        """Test creating a response."""
        from piranha_agent.agent import AgentResponse
        response = AgentResponse(result="test", model="gpt-4")
        assert response.result == "test"
        assert response.model == "gpt-4"
        assert response.cache_hit is False

    def test_response_string(self):
        """Test response string representation."""
        from piranha_agent.agent import AgentResponse
        response = AgentResponse(result="hello")
        assert str(response) == "hello"

    def test_response_cached_string(self):
        """Test cached response string representation."""
        from piranha_agent.agent import AgentResponse
        response = AgentResponse(result="cached", cache_hit=True)
        assert "(cached)" in str(response)
