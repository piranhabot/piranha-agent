#!/usr/bin/env python3
"""Tests for Claude Code Explorer skill."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Test that the module can be imported
def test_import_module():
    """Test that claude_code_explorer can be imported."""
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer, ExplorerConfig
    assert ClaudeCodeExplorer is not None
    assert ExplorerConfig is not None


def test_import_create_skill_function():
    """Test that create_claude_explorer_skill can be imported."""
    from piranha_agent.claude_code_explorer import create_claude_explorer_skill
    assert create_claude_explorer_skill is not None


def test_explorer_config_default():
    """Test ExplorerConfig default values."""
    from piranha_agent.claude_code_explorer import ExplorerConfig
    
    config = ExplorerConfig()
    assert config.src_root == "../src"
    assert config.mcp_server_command == "npx"
    assert config.timeout_seconds == 30
    assert config.mcp_server_args == ["-y", "claude-code-explorer-mcp"]


def test_explorer_config_custom():
    """Test ExplorerConfig with custom values."""
    from piranha_agent.claude_code_explorer import ExplorerConfig
    
    config = ExplorerConfig(
        src_root="/custom/src",
        mcp_server_command="node",
        mcp_server_args=["/path/to/server"],
        timeout_seconds=60,
    )
    assert config.src_root == "/custom/src"
    assert config.mcp_server_command == "node"
    assert config.mcp_server_args == ["/path/to/server"]
    assert config.timeout_seconds == 60


def test_explorer_initialization():
    """Test ClaudeCodeExplorer initialization."""
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer
    
    explorer = ClaudeCodeExplorer()
    assert explorer is not None
    assert explorer.config is not None
    assert explorer._session is None


def test_explorer_initialization_with_config():
    """Test ClaudeCodeExplorer with custom config."""
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer, ExplorerConfig
    
    config = ExplorerConfig(timeout_seconds=120)
    explorer = ClaudeCodeExplorer(config)
    assert explorer.config.timeout_seconds == 120


@pytest.mark.asyncio
async def test_explorer_without_mcp_installed():
    """Test that explorer raises error when MCP not installed."""
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer
    
    explorer = ClaudeCodeExplorer()
    
    # Mock MCP_AVAILABLE to False
    with patch('piranha_agent.claude_code_explorer.MCP_AVAILABLE', False):
        with pytest.raises(RuntimeError, match="MCP not installed"):
            await explorer._get_session()


@pytest.mark.asyncio
async def test_explorer_context_manager():
    """Test async context manager."""
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer
    
    explorer = ClaudeCodeExplorer()
    
    # Mock the session methods
    with patch.object(explorer, '_get_session', new_callable=AsyncMock) as mock_get:
        with patch.object(explorer, 'close', new_callable=AsyncMock) as mock_close:
            async with explorer:
                mock_get.assert_called_once()
            
            mock_close.assert_called_once()


def test_create_claude_explorer_skill():
    """Test create_claude_explorer_skill returns list of skills."""
    from piranha_agent.claude_code_explorer import create_claude_explorer_skill
    
    skills = create_claude_explorer_skill()
    
    assert isinstance(skills, list)
    assert len(skills) == 5  # Should return 5 skills
    
    # Check skill names
    skill_names = [skill.name for skill in skills]
    assert "claude_code.list_tools" in skill_names
    assert "claude_code.list_commands" in skill_names
    assert "claude_code.get_tool_source" in skill_names
    assert "claude_code.search_source" in skill_names
    assert "claude_code.get_architecture" in skill_names


def test_skill_has_auto_monitor():
    """Test that skills have auto_monitor enabled."""
    from piranha_agent.claude_code_explorer import create_claude_explorer_skill
    
    skills = create_claude_explorer_skill()
    
    for skill in skills:
        assert skill.auto_monitor is True
        assert skill.name.startswith("claude_code.")


def test_skill_parameters():
    """Test skill parameter schemas."""
    from piranha_agent.claude_code_explorer import create_claude_explorer_skill
    
    skills = create_claude_explorer_skill()
    
    # Find get_tool_source skill
    get_tool_skill = next(s for s in skills if s.name == "claude_code.get_tool_source")
    
    assert "parameters_schema" in dir(get_tool_skill)
    assert get_tool_skill.parameters_schema.get("type") == "object"
    assert "tool_name" in str(get_tool_skill.parameters_schema)


def test_skill_descriptions():
    """Test that skills have descriptions."""
    from piranha_agent.claude_code_explorer import create_claude_explorer_skill
    
    skills = create_claude_explorer_skill()
    
    for skill in skills:
        assert skill.description is not None
        assert len(skill.description) > 0


# Integration tests (skip if MCP not available)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_list_tools():
    """Integration test: List Claude Code tools."""
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer
    
    pytest.skip("Integration test requires MCP and Claude Code server")
    
    explorer = ClaudeCodeExplorer()
    try:
        tools = await explorer.list_tools()
        assert "tools" in tools
        assert len(tools["tools"]) > 0
    finally:
        await explorer.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_list_commands():
    """Integration test: List Claude Code commands."""
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer
    
    pytest.skip("Integration test requires MCP and Claude Code server")
    
    explorer = ClaudeCodeExplorer()
    try:
        commands = await explorer.list_commands()
        assert "commands" in commands
        assert len(commands["commands"]) > 0
    finally:
        await explorer.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_get_architecture():
    """Integration test: Get architecture overview."""
    from piranha_agent.claude_code_explorer import ClaudeCodeExplorer
    
    pytest.skip("Integration test requires MCP and Claude Code server")
    
    explorer = ClaudeCodeExplorer()
    try:
        arch = await explorer.get_architecture()
        assert arch is not None
    finally:
        await explorer.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
