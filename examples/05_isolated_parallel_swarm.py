#!/usr/bin/env python3
"""Advanced Swarm Demo: Isolated Parallel Execution.

This example demonstrates the 'Swarm' pattern:
1. Create a branch and an isolated Git workspace (worktree).
2. Launch parallel sub-agents to work in that workspace.
3. Aggregate results and cleanup.
"""

import os
import asyncio
from piranha_agent.orchestration import create_orchestrated_team
import subprocess

def run_git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True, check=True)

async def main():
    print("🐝 Initializing Advanced Swarm...")
    
    # 1. Setup Team
    team = create_orchestrated_team(name="SwarmTeam")
    coordinator = team.coordinator
    
    # 2. Get skills
    skills = {s.name: s for s in coordinator.skills}
    
    print(f"Coordinator '{coordinator.name}' has isolation & parallel skills ready.")
    
    # --- STEP 1: ISOLATION ---
    print("\n--- [Phase 1: Isolation] ---")
    temp_branch = f"swarm-demo-{os.urandom(4).hex()}"
    print(f"Creating temporary branch: {temp_branch}")
    run_git(["branch", temp_branch])
    
    try:
        # Use the isolation skill
        workspace_path = skills["git_create_isolated_workspace"](branch=temp_branch)
        print(f"Result: {workspace_path}")
        
        # --- STEP 2: PARALLEL EXECUTION ---
        print("\n--- [Phase 2: Parallel Swarm] ---")
        assignments = [
            {
                "agent_name": "researcher",
                "role": "code researcher",
                "task_description": "Find all instances of 'print' in the workspace."
            },
            {
                "agent_name": "linter",
                "role": "linting expert",
                "task_description": "Check for common PEP8 issues in piranha_agent/."
            }
        ]
        
        launch_msg = skills["delegate_parallel_tasks"](assignments=assignments)
        print(f"Launched: {launch_msg}")
        
        # Extract task IDs from the message (simulated for demo)
        import re
        task_ids = re.findall(r"task-[a-f0-9]+", launch_msg)
        
        # --- STEP 3: SYNCHRONIZATION ---
        print("\n--- [Phase 3: Synchronization] ---")
        print(f"Waiting for tasks {task_ids} to complete...")
        
        # Use the wait skill (it handles the asyncio loop internally)
        results = skills["wait_for_tasks"](task_ids=task_ids)
        print("\n[Swarm Results]:")
        print("-" * 30)
        print(results)
        print("-" * 30)
        
    finally:
        # --- STEP 4: CLEANUP ---
        print("\n--- [Phase 4: Cleanup] ---")
        # Cleanup the isolated workspace
        if 'workspace_path' in locals():
            path = workspace_path.split(": ")[1].split(".")[0]
            print(f"Cleaning up workspace at {path}...")
            skills["git_cleanup_workspace"](path=path)
        
        # Delete temp branch
        print(f"Deleting branch {temp_branch}...")
        run_git(["branch", "-D", temp_branch])
        
    print("\n✅ Swarm Demo Complete.")

if __name__ == "__main__":
    # Apply nest_asyncio so we can run the wait_for_tasks skill's loop inside main
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
