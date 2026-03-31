#!/usr/bin/env python3
"""Git Worktree isolation for Piranha sub-agents.

This module provides tools for creating and managing isolated 
Git worktrees, allowing multiple agents to work on the same 
repository without file system conflicts.
"""

import os
import shutil
import subprocess
import tempfile
import logging
from typing import Optional

from piranha_agent.skill import skill

logger = logging.getLogger(__name__)

class GitWorktreeManager:
    """Manages temporary Git worktrees."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.worktrees = {}

    def create_worktree(self, branch: str, name: Optional[str] = None) -> str:
        """Create a new temporary Git worktree.
        
        Args:
            branch: Branch to checkout
            name: Optional name for the worktree directory
            
        Returns:
            Path to the new worktree
        """
        if not name:
            name = f"piranha-wt-{branch}-{os.urandom(4).hex()}"
            
        target_path = os.path.join(tempfile.gettempdir(), name)
        
        try:
            # git worktree add <path> <branch>
            subprocess.run(
                ["git", "worktree", "add", target_path, branch],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            self.worktrees[target_path] = branch
            logger.info(f"Created worktree at {target_path} for branch {branch}")
            return target_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create worktree: {e.stderr}")
            raise RuntimeError(f"Git worktree creation failed: {e.stderr}")

    def remove_worktree(self, path: str):
        """Remove a Git worktree.
        
        Args:
            path: Path to the worktree to remove
        """
        try:
            # git worktree remove <path>
            subprocess.run(
                ["git", "worktree", "remove", "--force", path],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            if path in self.worktrees:
                del self.worktrees[path]
            
            # Cleanup directory if it still exists
            if os.path.exists(path):
                shutil.rmtree(path)
                
            logger.info(f"Removed worktree at {path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove worktree: {e.stderr}")
            raise RuntimeError(f"Git worktree removal failed: {e.stderr}")

@skill(
    name="git_create_isolated_workspace",
    description="Create an isolated Git workspace (worktree) for a specific branch.",
    parameters={
        "type": "object",
        "properties": {
            "branch": {"type": "string", "description": "Branch to checkout in the workspace"},
            "workspace_name": {"type": "string", "description": "Optional name for the workspace"}
        },
        "required": ["branch"]
    }
)
def git_create_isolated_workspace(branch: str, workspace_name: Optional[str] = None) -> str:
    """Skill to create an isolated Git workspace."""
    manager = GitWorktreeManager()
    path = manager.create_worktree(branch, workspace_name)
    return f"Isolated workspace created at: {path}. You can now perform operations in this directory."

@skill(
    name="git_cleanup_workspace",
    description="Remove an isolated Git workspace.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the workspace to remove"}
        },
        "required": ["path"]
    },
    requires_confirmation=True
)
def git_cleanup_workspace(path: str) -> str:
    """Skill to cleanup an isolated Git workspace."""
    manager = GitWorktreeManager()
    manager.remove_worktree(path)
    return f"Workspace at {path} has been successfully removed."
