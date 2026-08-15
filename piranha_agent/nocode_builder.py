#!/usr/bin/env python3
"""No-Code Visual Agent Builder - workflow data model and code generation.

The Gradio UI itself lives in nocode_builder_app.py, which imports the
functions defined here.
"""

import os
import subprocess
import sys
import tempfile
import time

import gradio as gr


# Categorized node types
NODE_CATEGORIES = {
    "📥 Input": {
        "trigger": {"icon": "⚡", "label": "Trigger", "color": "#FF6B6B", "desc": "Start workflow"},
        "http": {"icon": "🌐", "label": "HTTP", "color": "#4D96FF", "desc": "HTTP request"},
    },
    "🤖 AI": {
        "agent": {"icon": "🤖", "label": "Agent", "color": "#4ECDC4", "desc": "AI Agent"},
        "llm": {"icon": "💬", "label": "LLM", "color": "#95E1D3", "desc": "LLM call"},
    },
    "🔧 Processing": {
        "skill": {"icon": "🔧", "label": "Skill", "color": "#F38181", "desc": "Execute skill"},
        "transform": {"icon": "🔁", "label": "Transform", "color": "#FFD93D", "desc": "Transform data"},
        "compose": {"icon": "🧩", "label": "Compose", "color": "#F6BD60", "desc": "Build/construct a value"},
    },
    "🔁 Control Flow": {
        "condition": {"icon": "🔀", "label": "Condition", "color": "#AA96DA", "desc": "Branch logic (if/else)"},
        "filter": {"icon": "🧹", "label": "Filter", "color": "#84A59D", "desc": "Filter a list"},
        "apply_to_each": {"icon": "🔂", "label": "Apply to Each", "color": "#F28482", "desc": "Loop over a list"},
        "do_until": {"icon": "🔁", "label": "Do Until", "color": "#F5CAC3", "desc": "Loop until a condition"},
    },
    "📤 Output": {
        "output": {"icon": "📤", "label": "Output", "color": "#6BCB77", "desc": "Output result"},
    },
}

TEMPLATES = {
    "💬 Basic Chat": {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Start", "x": 50, "y": 180},
            {"id": "n2", "type": "agent", "name": "Chat Agent", "x": 280, "y": 180},
            {"id": "n3", "type": "output", "name": "Response", "x": 510, "y": 180},
        ],
        "connections": [{"source": "n1", "target": "n2"}, {"source": "n2", "target": "n3"}],
    },
    "🔍 Research Assistant": {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Query", "x": 50, "y": 180},
            {"id": "n2", "type": "skill", "name": "Web Search", "x": 280, "y": 180},
            {"id": "n3", "type": "llm", "name": "Analyze", "x": 510, "y": 180},
            {"id": "n4", "type": "output", "name": "Report", "x": 740, "y": 180},
        ],
        "connections": [{"source": "n1", "target": "n2"}, {"source": "n2", "target": "n3"}, {"source": "n3", "target": "n4"}],
    },
    "📝 Code Review": {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Code", "x": 50, "y": 180},
            {"id": "n2", "type": "skill", "name": "Review", "x": 280, "y": 180},
            {"id": "n3", "type": "condition", "name": "Has Issues?", "x": 510, "y": 180},
            {"id": "n4", "type": "llm", "name": "Suggest", "x": 740, "y": 100},
            {"id": "n5", "type": "output", "name": "Report", "x": 740, "y": 260},
        ],
        "connections": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
            {"source": "n3", "target": "n4", "label": "Yes"},
            {"source": "n3", "target": "n5", "label": "No"},
        ],
    },
    "🌐 API Integration": {
        "nodes": [
            {"id": "n1", "type": "http", "name": "Fetch API", "x": 50, "y": 180},
            {"id": "n2", "type": "transform", "name": "Parse", "x": 280, "y": 180},
            {"id": "n3", "type": "llm", "name": "Process", "x": 510, "y": 180},
            {"id": "n4", "type": "output", "name": "Save", "x": 740, "y": 180},
        ],
        "connections": [{"source": "n1", "target": "n2"}, {"source": "n2", "target": "n3"}, {"source": "n3", "target": "n4"}],
    },
}


def generate_code(workflow):
    """Generate functional Python code using Piranha SDK.

    Follows the actual connection graph (not just node list order), so
    condition nodes produce real if/else branches based on which outgoing
    connection is labeled "Yes"/"No" - a linear node-order walk can't do
    that. http/llm/skill/transform nodes generate real, runnable code;
    where a node genuinely needs configuration that this builder's UI
    doesn't yet expose (e.g. which URL, which specific skill), the
    generated code is real and correct in structure, with a clearly
    marked TODO for the value only a person can supply.
    """
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", [])
    node_by_id = {n["id"]: n for n in nodes}

    outgoing: dict[str, list[tuple[str, str | None]]] = {}
    targets: set[str] = set()
    for conn in connections:
        outgoing.setdefault(conn["source"], []).append((conn["target"], conn.get("label")))
        targets.add(conn["target"])
    roots = [n["id"] for n in nodes if n["id"] not in targets]

    lines = [
        '#!/usr/bin/env python3',
        '"""Auto-generated Workflow using Piranha Agent"""',
        "",
        "import asyncio",
        "import httpx",
        "from piranha_agent import Agent, Task",
        "from piranha_agent.complete_claude_skills import register_complete_claude_skills",
        "from piranha_agent.llm_provider import LLMMessage, LLMProvider",
        "",
        "async def main():",
        "    # Initialize Agents and Tools",
    ]

    # Instantiate agents up front (agent and skill nodes both need one).
    executor_nodes = [n for n in nodes if n["type"] in ("agent", "skill")]
    for node in executor_nodes:
        nid, name = node["id"], node.get("name", "Assistant")
        lines.append(f'    agent_{nid} = Agent(name="{name}", model="ollama/llama3:latest")')
        lines.append(f'    register_complete_claude_skills(agent_{nid})')

    lines.append("")
    lines.append("    # Define Workflow Execution")

    def emit(nid: str, indent: int, visited: set[str]) -> None:
        if nid in visited or nid not in node_by_id:
            return
        visited.add(nid)

        node = node_by_id[nid]
        ntype, name = node["type"], node.get("name", "Node")
        pad = "    " * indent

        if ntype == "trigger":
            lines.append(f'{pad}# {name}: Entry point')
            lines.append(f'{pad}input_data = "Start workflow"')
        elif ntype == "agent":
            lines.append(f'{pad}# {name}: Agent processing')
            lines.append(f'{pad}task_{nid} = Task(description=input_data, agent=agent_{nid})')
            lines.append(f'{pad}result_{nid} = task_{nid}.run()')
            lines.append(f'{pad}input_data = result_{nid}.result')
        elif ntype == "skill":
            lines.append(f'{pad}# {name}: Skill execution (agent picks the right registered skill)')
            lines.append(f'{pad}task_{nid} = Task(description=input_data, agent=agent_{nid})')
            lines.append(f'{pad}result_{nid} = task_{nid}.run()')
            lines.append(f'{pad}input_data = result_{nid}.result')
        elif ntype == "llm":
            lines.append(f'{pad}# {name}: Direct LLM call')
            lines.append(f'{pad}llm_{nid} = LLMProvider(model="ollama/llama3:latest")')
            lines.append(f'{pad}response_{nid} = llm_{nid}.chat([LLMMessage(role="user", content=input_data)])')
            lines.append(f'{pad}input_data = response_{nid}.content')
        elif ntype == "http":
            lines.append(f'{pad}# {name}: HTTP request')
            lines.append(f'{pad}url_{nid} = "https://api.example.com"  # TODO: set the real URL for "{name}"')
            lines.append(f'{pad}response_{nid} = httpx.get(url_{nid})')
            lines.append(f'{pad}input_data = response_{nid}.text')
        elif ntype == "transform":
            lines.append(f'{pad}# {name}: Data transform')
            lines.append(f'{pad}def transform_{nid}(data):')
            lines.append(f'{pad}    # TODO: implement the transform for "{name}"')
            lines.append(f'{pad}    return data')
            lines.append(f'{pad}input_data = transform_{nid}(input_data)')
        elif ntype == "compose":
            lines.append(f'{pad}# {name}: Compose a value')
            lines.append(f'{pad}composed_{nid} = input_data  # TODO: build the real expression for "{name}"')
            lines.append(f'{pad}input_data = composed_{nid}')
        elif ntype == "filter":
            lines.append(f'{pad}# {name}: Filter')
            lines.append(f'{pad}items_{nid} = input_data if isinstance(input_data, list) else [input_data]')
            lines.append(f'{pad}input_data = [item for item in items_{nid} if True]  # TODO: real filter condition for "{name}"')
        elif ntype == "condition":
            lines.append(f'{pad}# {name}: Branch')
            lines.append(f'{pad}if True:  # TODO: implement the real condition for "{name}"')
        elif ntype == "apply_to_each":
            lines.append(f'{pad}# {name}: Apply to Each')
            lines.append(f'{pad}items_{nid} = input_data if isinstance(input_data, list) else [input_data]')
            lines.append(f'{pad}for item_{nid} in items_{nid}:')
            lines.append(f'{pad}    input_data = item_{nid}')
        elif ntype == "do_until":
            lines.append(f'{pad}# {name}: Do Until')
            lines.append(
                f'{pad}for _ in range(1):  # TODO: replace with a real until-condition for "{name}" '
                '(runs once by default so generated code never loops forever)'
            )
        elif ntype == "output":
            lines.append(f'{pad}# {name}: Final Result')
            lines.append(f'{pad}print("--- Workflow Result ---\\n", input_data)')

        next_edges = outgoing.get(nid, [])
        if ntype == "condition":
            yes = [t for t, label in next_edges if label == "Yes"]
            no = [t for t, label in next_edges if label == "No"]
            other = [t for t, label in next_edges if label not in ("Yes", "No")]

            for target in yes:
                emit(target, indent + 1, visited)
            if not yes:
                lines.append(f'{pad}    pass')

            lines.append(f'{pad}else:')
            for target in no:
                emit(target, indent + 1, visited)
            if not no:
                lines.append(f'{pad}    pass')

            for target in other:
                emit(target, indent, visited)
        elif ntype in ("apply_to_each", "do_until"):
            for target, _label in next_edges:
                emit(target, indent + 1, visited)
            if not next_edges:
                lines.append(f'{pad}    pass')
        else:
            for target, _label in next_edges:
                emit(target, indent, visited)

    visited: set[str] = set()
    for root_id in roots:
        emit(root_id, 1, visited)
    # Nodes unreachable from any root (e.g. a floating node with no
    # incoming connection that also isn't a root due to a cycle) still
    # get emitted, so nothing a user placed on the canvas is silently
    # dropped.
    for node in nodes:
        emit(node["id"], 1, visited)

    lines.extend([
        "",
        "if __name__ == \"__main__\":",
        "    asyncio.run(main())"
    ])
    return "\n".join(lines)


def render_canvas(workflow):
    """Render workflow canvas."""
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", [])

    if not nodes:
        return '''<div style="width:100%;height:450px;background:linear-gradient(135deg,#0d1117 0%,#161b22 100%);display:flex;align-items:center;justify-content:center;flex-direction:column;color:#8b949e;">
            <div style="font-size:48px;margin-bottom:16px;">🎨</div>
            <div style="font-size:18px;font-weight:600;">Start Building Your Workflow</div>
            <div style="font-size:14px;margin-top:8px;">Click a template or add nodes from the sidebar</div>
        </div>'''

    # Build connection SVG
    node_map = {n["id"]: n for n in nodes}
    conn_paths = ['<svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1;">']
    conn_paths.append('<defs><marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#666"/></marker></defs>')
    
    for conn in connections:
        src, tgt = node_map.get(conn.get("source")), node_map.get(conn.get("target"))
        if src and tgt:
            x1, y1 = src.get("x", 0) + 200, src.get("y", 0) + 35
            x2, y2 = tgt.get("x", 0), tgt.get("y", 0) + 35
            conn_paths.append(f'<path d="M {x1} {y1} C {x1+50} {y1}, {x2-50} {y2}, {x2} {y2}" stroke="#484f58" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
    conn_paths.append('</svg>')
    
    # Build node HTML
    node_colors = {k: v["color"] for cat in NODE_CATEGORIES.values() for k, v in cat.items()}
    node_icons = {k: v["icon"] for cat in NODE_CATEGORIES.values() for k, v in cat.items()}
    node_labels = {k: v["label"] for cat in NODE_CATEGORIES.values() for k, v in cat.items()}
    
    node_html = []
    for node in nodes:
        color = node_colors.get(node.get("type"), "#888")
        icon = node_icons.get(node.get("type"), "📦")
        label = node_labels.get(node.get("type"), "Node")
        nid, name, x, y = node.get("id"), node.get("name", "Node"), node.get("x", 0), node.get("y", 0)
        node_html.append(f'''
<div class="node" data-id="{nid}"
     style="position:absolute;left:{x}px;top:{y}px;width:200px;background:#161b22;border:2px solid {color};border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,0.3);">
    <div class="header" style="padding:12px;background:linear-gradient(135deg,{color}33,{color}11);border-bottom:1px solid {color}44;border-radius:8px 8px 0 0;display:flex;align-items:center;gap:10px;">
        <span style="font-size:20px">{icon}</span>
        <div>
            <div style="font-weight:600;color:#fff;font-size:14px">{name}</div>
            <div style="font-size:11px;color:#8b949e">{label}</div>
        </div>
    </div>
    <div style="padding:10px 12px;"><div style="font-size:11px;color:#6e7681;">ID: {nid}</div></div>
    <div style="position:absolute;left:-6px;top:35px;width:12px;height:12px;background:#8b949e;border-radius:50%;border:2px solid #161b22;"></div>
    <div style="position:absolute;right:-6px;top:35px;width:12px;height:12px;background:{color};border-radius:50%;border:2px solid #161b22;"></div>
</div>''')
    
    return f'''
<div id="canvas" style="width:100%;height:450px;position:relative;overflow:hidden;background:linear-gradient(135deg,#0d1117 0%,#161b22 100%);border:1px solid #30363d;border-radius:12px;">
    {''.join(conn_paths)}
    {''.join(node_html)}
</div>
'''


def add_node(workflow, node_type):
    """Add a node."""
    all_nodes = {k: v for cat in NODE_CATEGORIES.values() for k, v in cat.items()}
    info = all_nodes.get(node_type, {"label": "Node"})
    # Fix ID generation
    timestamp_str = str(int(time.time()))[-4:]
    nid = f"n{len(workflow.get('nodes', [])) + 1}_{timestamp_str}"
    
    new_wf = {"nodes": list(workflow.get("nodes", [])), "connections": list(workflow.get("connections", []))}
    new_wf["nodes"].append({
        "id": nid, "type": node_type, "name": info["label"],
        "x": 50 + len(new_wf["nodes"]) * 40, "y": 100 + (len(new_wf["nodes"]) % 3) * 80,
    })
    
    # Auto-connect if there's a previous node
    if len(new_wf["nodes"]) > 1:
        prev_id = new_wf["nodes"][-2]["id"]
        new_wf["connections"].append({"source": prev_id, "target": nid})
        
    choices = [n["id"] for n in new_wf["nodes"]]
    return new_wf, render_canvas(new_wf), generate_code(new_wf), gr.update(choices=choices, value=nid)


def update_node_config(workflow, node_id, new_name):
    """Update a node's configuration."""
    if not node_id:
        return workflow, render_canvas(workflow), generate_code(workflow)
        
    new_wf = {"nodes": [dict(n) for n in workflow.get("nodes", [])], "connections": list(workflow.get("connections", []))}
    for node in new_wf["nodes"]:
        if node["id"] == node_id:
            node["name"] = new_name
            break
            
    return new_wf, render_canvas(new_wf), generate_code(new_wf)


def delete_node(workflow, node_id):
    """Delete a node and its connections."""
    if not node_id:
        choices = [n["id"] for n in workflow["nodes"]]
        return workflow, render_canvas(workflow), generate_code(workflow), gr.update(choices=choices)
        
    new_wf = {
        "nodes": [n for n in workflow["nodes"] if n["id"] != node_id],
        "connections": [c for c in workflow["connections"] if c["source"] != node_id and c["target"] != node_id]
    }
    
    choices = [n["id"] for n in new_wf["nodes"]]
    new_val = choices[-1] if choices else None
    return new_wf, render_canvas(new_wf), generate_code(new_wf), gr.update(choices=choices, value=new_val)


def load_template(name):
    """Load template."""
    tpl = TEMPLATES.get(name, {"nodes": [], "connections": []})
    wf = {"nodes": [dict(n) for n in tpl.get("nodes", [])], "connections": list(tpl.get("connections", []))}
    choices = [n["id"] for n in wf["nodes"]]
    new_val = choices[0] if choices else None
    return wf, render_canvas(wf), generate_code(wf), gr.update(choices=choices, value=new_val)


def clear_canvas():
    """Clear."""
    wf = {"nodes": [], "connections": []}
    return wf, render_canvas(wf), generate_code(wf), gr.update(choices=[], value=None)


def update_stats(workflow):
    """Update workflow stats."""
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", [])
    return {
        "total_nodes": len(nodes),
        "total_connections": len(connections),
        "node_types": list(set(n["type"] for n in nodes)),
    }


def populate_sidebar(workflow, node_id):
    """Populate sidebar with node data."""
    if not node_id:
        return "", ""
    for node in workflow["nodes"]:
        if node["id"] == node_id:
            return node["name"], node["type"]
    return "", ""


def run_workflow(workflow: dict, timeout_seconds: int = 60) -> str:
    """Actually execute a workflow's generated code and return its output.

    Writes generate_code(workflow) to a temp file and runs it as a real
    subprocess using the current Python interpreter (so it has access to
    the installed piranha_agent package), rather than just claiming
    execution "started" without doing anything.
    """
    if not workflow.get("nodes"):
        return "No nodes in workflow - nothing to run."

    code = generate_code(workflow)

    fd, temp_path = tempfile.mkstemp(suffix=".py", prefix="piranha_workflow_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        output = result.stdout
        if result.returncode != 0:
            output += f"\n--- Workflow exited with code {result.returncode} ---\n{result.stderr}"
        return output or "(workflow produced no output)"
    except subprocess.TimeoutExpired:
        return f"Workflow execution timed out after {timeout_seconds}s."
    finally:
        os.unlink(temp_path)
