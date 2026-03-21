#!/usr/bin/env python3
"""Piranha Time-Travel Debugger with Gradio.

Features:
- Load and visualize agent traces
- Event timeline with color coding
- Rollback to any sequence
- Cost analysis
- Event inspection
"""

import json
from typing import Any

import gradio as gr
from piranha_core import EventStore

# =============================================================================
# Trace Loader
# =============================================================================

def load_trace(session_id: str, db_path: str = ":memory:") -> tuple[str, str]:
    """Load trace from event store.
    
    Args:
        session_id: Session UUID
        db_path: Database path
        
    Returns:
        Tuple of (trace JSON, status message)
    """
    try:
        store = EventStore(db_path) if db_path != ":memory:" else EventStore()
        trace_json = store.export_trace(session_id)
        trace = json.loads(trace_json)
        
        # Format for display
        formatted = json.dumps(trace, indent=2, default=str)
        return formatted, f"✓ Loaded {trace.get('event_count', 0)} events"
    except Exception as e:
        return "", f"✗ Error: {str(e)}"


def parse_events(trace_json: str) -> list[dict[str, Any]]:
    """Parse trace JSON to event list."""
    try:
        trace = json.loads(trace_json)
        return trace.get("events", [])
    except Exception:
        return []


def format_event(event: dict[str, Any]) -> str:
    """Format single event for display."""
    event_type = event.get("event_type", "Unknown")
    sequence = event.get("sequence", 0)
    timestamp = event.get("timestamp", "")
    agent_id = event.get("agent_id", "")[:8]
    
    lines = [
        f"Event #{sequence}",
        f"Type: {event_type}",
        f"Time: {timestamp}",
        f"Agent: {agent_id}...",
        f"ID: {event.get('id', '')[:8]}...",
    ]
    
    # Add payload info
    payload = event.get("payload", {})
    if payload:
        lines.append(f"Payload: {json.dumps(payload, indent=2, default=str)[:200]}...")
    
    return "\n".join(lines)


# =============================================================================
# Timeline Visualization
# =============================================================================

def build_timeline(trace_json: str) -> str:
    """Build ASCII timeline of events."""
    events = parse_events(trace_json)
    
    if not events:
        return "No events to display"
    
    lines = ["📊 Event Timeline", "=" * 50, ""]
    
    for event in events:
        event_type = event.get("event_type", "Unknown")
        sequence = event.get("sequence", 0)
        icon = get_event_icon(event_type)
        
        # Color coding
        color = get_event_color(event_type)
        
        lines.append(f"{icon} [{sequence:03d}] {event_type} {color}")
    
    lines.extend(["", "=" * 50, f"Total: {len(events)} events"])
    
    return "\n".join(lines)


def get_event_icon(event_type: str) -> str:
    """Get icon for event type."""
    icons = {
        "LlmCall": "🤖",
        "CacheHit": "💾",
        "SkillInvoked": "🛠️",
        "SkillCompleted": "✅",
        "GuardrailCheck": "🛡️",
        "GuardrailBlocked": "🚫",
        "AgentSpawn": "👶",
        "AgentCompleted": "🏁",
        "AgentFailed": "❌",
        "BudgetAlert": "⚠️",
    }
    return icons.get(event_type, "📝")


def get_event_color(event_type: str) -> str:
    """Get color indicator for event type."""
    colors = {
        "LlmCall": "[BLUE]",
        "CacheHit": "[GREEN]",
        "SkillInvoked": "[YELLOW]",
        "SkillCompleted": "[GREEN]",
        "GuardrailBlocked": "[RED]",
        "AgentFailed": "[RED]",
        "BudgetAlert": "[ORANGE]",
    }
    return colors.get(event_type, "")


# =============================================================================
# Cost Analysis
# =============================================================================

def analyze_costs(trace_json: str) -> str:
    """Analyze costs from trace."""
    try:
        trace = json.loads(trace_json)
        events = trace.get("events", [])
        
        total_tokens = 0
        total_cost = 0.0
        cache_hits = 0
        llm_calls = 0
        model_costs: dict[str, dict[str, Any]] = {}
        
        for event in events:
            payload = event.get("payload", {})
            event_type = event.get("event_type", "")
            
            if event_type == "CacheHit":
                cache_hits += 1
                if "cost_usd" in payload:
                    total_cost += payload.get("cost_usd", 0)
                    model = payload.get("model", "unknown")
                    if model not in model_costs:
                        model_costs[model] = {"calls": 0, "cost": 0.0}
                    model_costs[model]["calls"] += 1
                    model_costs[model]["cost"] += payload.get("cost_usd", 0)
            
            elif event_type == "LlmCall":
                llm_calls += 1
                prompt = payload.get("prompt_tokens", 0)
                completion = payload.get("completion_tokens", 0)
                cost = payload.get("cost_usd", 0)
                
                total_tokens += prompt + completion
                total_cost += cost
                
                model = payload.get("model", "unknown")
                if model not in model_costs:
                    model_costs[model] = {"calls": 0, "tokens": 0, "cost": 0.0}
                model_costs[model]["calls"] += 1
                model_costs[model]["tokens"] += prompt + completion
                model_costs[model]["cost"] += cost
        
        # Build report
        lines = [
            "💰 Cost Analysis",
            "=" * 50,
            f"LLM Calls: {llm_calls}",
            f"Cache Hits: {cache_hits}",
            f"Total Tokens: {total_tokens:,}",
            f"Total Cost: ${total_cost:.4f}",
            "",
            "Per-Model Breakdown:",
        ]
        
        for model, stats in model_costs.items():
            lines.append(f"  {model}:")
            lines.append(f"    Calls: {stats['calls']}")
            if "tokens" in stats:
                lines.append(f"    Tokens: {stats['tokens']:,}")
            lines.append(f"    Cost: ${stats['cost']:.4f}")
        
        # Cache savings
        if cache_hits > 0:
            estimated_savings = cache_hits * 0.002  # Rough estimate
            lines.extend([
                "",
                f"💡 Estimated Cache Savings: ${estimated_savings:.4f}",
            ])
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error analyzing costs: {e}"


# =============================================================================
# Rollback
# =============================================================================

def rollback_to_sequence(
    session_id: str,
    agent_id: str,
    target_sequence: int,
    db_path: str = ":memory:",
) -> tuple[str, str]:
    """Rollback session to a specific sequence.
    
    Args:
        session_id: Session UUID
        agent_id: Agent UUID
        target_sequence: Sequence number to rollback to
        db_path: Database path
        
    Returns:
        Tuple of (snapshot JSON, status message)
    """
    try:
        store = EventStore(db_path) if db_path != ":memory:" else EventStore()
        snapshot_json = store.rollback_to_sequence(session_id, agent_id, target_sequence)
        snapshot = json.loads(snapshot_json)
        
        formatted = json.dumps(snapshot, indent=2, default=str)
        return formatted, f"✓ Rolled back to sequence {target_sequence}"
    except Exception as e:
        return "", f"✗ Rollback failed: {str(e)}"


# =============================================================================
# Gradio UI
# =============================================================================

def create_ui() -> gr.Blocks:
    """Create the Gradio UI."""
    
    with gr.Blocks(title="Piranha Time-Travel Debugger", theme=gr.themes.Soft()) as ui:
        gr.Markdown("# 🐍 Piranha Time-Travel Debugger")
        gr.Markdown("Load agent traces, visualize events, analyze costs, and rollback to previous states.")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📥 Load Trace")
                session_id = gr.Textbox(
                    label="Session ID",
                    placeholder="550e8400-e29b-41d4-a716-446655440000",
                )
                db_path = gr.Textbox(
                    label="Database Path (optional)",
                    placeholder=":memory: or /path/to/db.sqlite",
                    value=":memory:",
                )
                load_btn = gr.Button("Load Trace", variant="primary")
                load_status = gr.Textbox(label="Status", interactive=False)
            
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Timeline")
                timeline = gr.Textbox(
                    label="Event Timeline",
                    lines=15,
                    max_lines=20,
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Trace JSON")
                trace_json = gr.Textbox(
                    label="Raw Trace",
                    lines=20,
                    max_lines=30,
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 💰 Cost Analysis")
                cost_analysis = gr.Textbox(
                    label="Cost Report",
                    lines=20,
                    max_lines=30,
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⏪ Rollback")
                rollback_session = gr.Textbox(
                    label="Session ID",
                    placeholder="Same as above",
                )
                rollback_agent = gr.Textbox(
                    label="Agent ID",
                    placeholder="660e8400-e29b-41d4-a716-446655440000",
                )
                rollback_sequence = gr.Number(
                    label="Target Sequence",
                    value=0,
                    precision=0,
                )
                rollback_btn = gr.Button("Rollback", variant="stop")
                rollback_status = gr.Textbox(label="Rollback Status", interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("### 📋 Snapshot")
                snapshot_json = gr.Textbox(
                    label="State Snapshot",
                    lines=20,
                    max_lines=30,
                )
        
        # Event inspector
        with gr.Row():
            gr.Markdown("### 🔍 Event Inspector")
        
        event_list = gr.JSON(label="Events")
        
        # Wire up events
        load_btn.click(
            fn=load_trace,
            inputs=[session_id, db_path],
            outputs=[trace_json, load_status],
        ).then(
            fn=build_timeline,
            inputs=[trace_json],
            outputs=[timeline],
        ).then(
            fn=analyze_costs,
            inputs=[trace_json],
            outputs=[cost_analysis],
        ).then(
            fn=parse_events,
            inputs=[trace_json],
            outputs=[event_list],
        )
        
        rollback_btn.click(
            fn=rollback_to_sequence,
            inputs=[rollback_session, rollback_agent, rollback_sequence, db_path],
            outputs=[snapshot_json, rollback_status],
        )
        
        # Examples
        gr.Markdown("### 📚 Examples")
        gr.Examples(
            examples=[
                ["550e8400-e29b-41d4-a716-446655440000", ":memory:"],
            ],
            inputs=[session_id, db_path],
        )
    
    return ui


# =============================================================================
# Main
# =============================================================================

def main():
    """Launch the Time-Travel Debugger."""
    ui = create_ui()
    ui.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
    )


if __name__ == "__main__":
    main()
