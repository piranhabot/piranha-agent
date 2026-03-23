#!/usr/bin/env python3
"""Piranha Studio Example.

Demonstrates real-time monitoring with Piranha Studio.

Usage:
    python examples/11_piranha_studio.py
"""

from piranha_agent import (
    Agent,
    Task,
    start_monitoring,
    monitor_agent,
)
import time


def main():
    print("=" * 70)
    print("PIRANHA STUDIO - REAL-TIME MONITORING DEMO")
    print("=" * 70)
    print()

    # Start monitoring server
    print("Starting Piranha Studio on http://localhost:8080...")
    monitor = start_monitoring(port=8080)
    print("✓ Studio started!")
    print()
    print("Open http://localhost:8080 in your browser to see the dashboard")
    print()

    # Create agents
    print("Creating agents...")
    agent1 = Agent(
        name="researcher",
        model="ollama/llama3:latest",
        description="Researches topics"
    )
    agent2 = Agent(
        name="writer",
        model="ollama/llama3:latest",
        description="Writes content"
    )

    # Monitor agents
    monitor_agent(agent1)
    monitor_agent(agent2)
    print(f"✓ Monitoring {agent1.name} ({agent1.id})")
    print(f"✓ Monitoring {agent2.name} ({agent2.id})")
    print()

    # Run tasks
    print("Running tasks (watch the dashboard for real-time updates)...")
    print()

    tasks = [
        ("What is Python?", agent1),
        ("Explain quantum computing", agent1),
        ("Write a haiku about AI", agent2),
        ("What are neural networks?", agent1),
        ("Explain machine learning", agent2),
    ]

    for i, (description, agent) in enumerate(tasks, 1):
        print(f"Task {i}: {description}")
        task = Task(description=description, agent=agent)
        _ = task.run()
        print(f"  ✓ Completed")
        
        # Small delay to see updates in dashboard
        time.sleep(1)

    print()
    print("=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print()
    print("Dashboard: http://localhost:8080")
    print()
    print("Metrics:")
    metrics = monitor.metrics
    monitor._update_metrics()
    print(f"  Active agents: {metrics.active_agents}")
    print(f"  Total tokens: {metrics.total_tokens}")
    print(f"  Total cost: ${metrics.total_cost_usd:.4f}")
    print(f"  Uptime: {monitor._update_metrics() or metrics.uptime_seconds:.0f} seconds")
    print()
    print("Press Ctrl+C to stop the monitoring server")
    print()
    
    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Piranha Studio...")
        monitor.stop()
        print("Studio stopped.")


if __name__ == "__main__":
    main()
