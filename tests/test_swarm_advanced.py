import pytest
# import asyncio  # Not used directly
# import os  # Not used directly
# import shutil  # Not used directly
from unittest.mock import MagicMock, patch
from piranha_agent.orchestration import create_orchestrated_team
from piranha_agent.agent import Agent, LLMResponse


@pytest.mark.asyncio
async def test_isolated_parallel_swarm_logic(tmp_path):
    # Use pytest's tmp_path for cross-platform compatibility
    MOCK_WORKSPACE_PATH = str(tmp_path / "mock-workspace")
    
    # 1. Setup Team
    team = create_orchestrated_team(name="TestSwarm")
    coordinator = team.coordinator
    skills = {s.name: s for s in coordinator.skills}

    # 2. Mock Agent.run for sub-agents
    # We want to simulate two parallel tasks
    mock_responses = [
        LLMResponse(content="Coder result", model="mock"),
        LLMResponse(content="Tester result", model="mock")
    ]

    with patch.object(Agent, 'run') as mock_run:
        mock_run.side_effect = mock_responses

        # 3. Test Isolation (Mocking git subprocesses might be needed if not in a repo,
        # but we are in a repo, so let's mock the GitWorktreeManager)
        with patch('piranha_agent.skills.git.GitWorktreeManager.create_worktree') as mock_create:
            mock_create.return_value = MOCK_WORKSPACE_PATH

            workspace_msg = skills["git_create_isolated_workspace"](branch="main")
            assert MOCK_WORKSPACE_PATH in workspace_msg
            
            # Verify that the underlying GitWorktreeManager received the expected branch argument
            mock_create.assert_called_once()
            _, kwargs = mock_create.call_args
            assert kwargs.get("branch") == "main", "Expected branch='main' to be passed to create_worktree"

            # 4. Test Parallel Delegation
            assignments = [
                {"agent_name": "coder", "task_description": "Write code"},
                {"agent_name": "tester", "task_description": "Run tests"}
            ]

            launch_msg = skills["delegate_parallel_tasks"](assignments=assignments)
            assert "Launched 2 tasks" in launch_msg

            # Ensure active tasks are being tracked after delegation
            assert hasattr(team, "active_tasks"), "team.active_tasks should be defined after launching tasks"
            assert len(team.active_tasks) == 2, "Expected 2 active tasks after delegation"
            
            # Extract task IDs
            import re
            task_ids = re.findall(r"task-[a-f0-9]+", launch_msg)
            assert len(task_ids) == 2

            # 5. Test Wait and Synchronization
            # wait_for_tasks is a synchronous skill that internally handles async tasks
            # Call it directly (it handles async internally)
            results = skills["wait_for_tasks"](task_ids=task_ids)

            assert "Coder result" in results
            assert "Tester result" in results
            
            # Verify tasks were cleared after completion
            assert len(team.active_tasks) == 0, "Expected active_tasks to be cleared after completion"

            # 6. Verify sub-agent configuration via Agent.run calls
            # Ensure that Agent.run was invoked once per assignment with the expected task descriptions
            assert mock_run.call_count == 2
            call_args_list = mock_run.call_args_list
            called_with_write_code = any(
                any("Write code" in str(arg) for arg in call.args) or
                any("Write code" in str(v) for v in call.kwargs.values())
                for call in call_args_list
            )
            called_with_run_tests = any(
                any("Run tests" in str(arg) for arg in call.args) or
                any("Run tests" in str(v) for v in call.kwargs.values())
                for call in call_args_list
            )
            assert called_with_write_code, "Expected 'Write code' task to be delegated"
            assert called_with_run_tests, "Expected 'Run tests' task to be delegated"


@pytest.mark.asyncio
async def test_git_workspace_cleanup(tmp_path):
    # Use pytest's tmp_path for cross-platform compatibility
    MOCK_WORKSPACE_PATH = str(tmp_path / "mock-workspace")
    
    team = create_orchestrated_team(name="CleanupTeam")
    coordinator = team.coordinator
    skills = {s.name: s for s in coordinator.skills}

    with patch('piranha_agent.skills.git.GitWorktreeManager.remove_worktree') as mock_remove:
        cleanup_msg = skills["git_cleanup_workspace"](path=MOCK_WORKSPACE_PATH)
        assert "successfully removed" in cleanup_msg
        mock_remove.assert_called_once_with(MOCK_WORKSPACE_PATH)
