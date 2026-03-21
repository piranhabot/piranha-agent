#!/usr/bin/env python3
"""No-Code Visual Agent Builder - Simple working version with Gradio."""

import json
import gradio as gr


NODE_TYPES = {
    "trigger": {"icon": "⚡", "label": "Trigger", "color": "#FF6B6B"},
    "agent": {"icon": "🤖", "label": "Agent", "color": "#4ECDC4"},
    "llm": {"icon": "💬", "label": "LLM", "color": "#95E1D3"},
    "skill": {"icon": "🔧", "label": "Skill", "color": "#F38181"},
    "condition": {"icon": "🔀", "label": "Condition", "color": "#AA96DA"},
    "transform": {"icon": "🔁", "label": "Transform", "color": "#FFD93D"},
    "output": {"icon": "📤", "label": "Output", "color": "#6BCB77"},
    "http": {"icon": "🌐", "label": "HTTP", "color": "#4D96FF"},
}

TEMPLATES = {
    "Basic Chat": {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Start", "x": 100, "y": 150},
            {"id": "n2", "type": "agent", "name": "Chat Agent", "x": 350, "y": 150},
            {"id": "n3", "type": "output", "name": "Response", "x": 600, "y": 150},
        ],
        "connections": [{"source": "n1", "target": "n2"}, {"source": "n2", "target": "n3"}],
    },
    "Research": {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Query", "x": 100, "y": 150},
            {"id": "n2", "type": "skill", "name": "Web Search", "x": 350, "y": 100},
            {"id": "n3", "type": "llm", "name": "Analyze", "x": 600, "y": 100},
            {"id": "n4", "type": "output", "name": "Report", "x": 850, "y": 100},
        ],
        "connections": [{"source": "n1", "target": "n2"}, {"source": "n2", "target": "n3"}, {"source": "n3", "target": "n4"}],
    },
    "Code Review": {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Code", "x": 100, "y": 150},
            {"id": "n2", "type": "skill", "name": "Review", "x": 350, "y": 150},
            {"id": "n3", "type": "condition", "name": "Has Issues?", "x": 600, "y": 150},
            {"id": "n4", "type": "llm", "name": "Suggest", "x": 850, "y": 80},
            {"id": "n5", "type": "output", "name": "Report", "x": 850, "y": 220},
        ],
        "connections": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
            {"source": "n3", "target": "n4", "label": "Yes"},
            {"source": "n3", "target": "n5", "label": "No"},
        ],
    },
}


def generate_code(workflow):
    """Generate Python code from workflow."""
    nodes = workflow.get("nodes", [])
    lines = ["#!/usr/bin/env python3", '"""Auto-generated Workflow"""', "", "from piranha import Agent", "import json", ""]
    
    for node in nodes:
        ntype, nid, name = node.get("type"), node.get("id"), node.get("name", "Node")
        lines.append(f"# {name} ({ntype})")
        if ntype == "agent":
            lines.append(f'agent_{nid} = Agent(name="agent", model="ollama/llama3:latest")')
        elif ntype == "llm":
            lines.append(f"def run_{nid}(data): return 'LLM response'")
        elif ntype == "skill":
            lines.append(f"def run_{nid}(data): return 'Skill result'")
        elif ntype == "trigger":
            lines.append(f"def run_{nid}(): return {{}}")
        elif ntype == "output":
            lines.append(f"def run_{nid}(data): print(f'Output: {{data}}')")
        else:
            lines.append(f"def run_{nid}(data): return data")
        lines.append("")
    
    lines.extend(["# Execute", "def run_workflow():", "    results = {}"])
    for node in nodes:
        nid = node["id"]
        if node.get("type") == "trigger":
            lines.append(f'    results["{nid}"] = run_{nid}()')
        else:
            lines.append(f'    results["{nid}"] = run_{nid}(results)')
    lines.extend(["    return results", "", 'if __name__ == "__main__":', "    print(run_workflow())"])
    return "\n".join(lines)


def render_canvas(workflow):
    """Render workflow as interactive HTML with drag-and-drop."""
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", [])
    
    if not nodes:
        return '''<div style="width:100%;height:500px;background:#0d1117;display:flex;align-items:center;justify-content:center;color:#888;font-size:18px;">
Click "Add Node" buttons below or load a template to start building
</div>'''
    
    # Build node HTML
    node_html = []
    for node in nodes:
        info = NODE_TYPES.get(node.get("type"), {"icon": "📦", "label": "Node", "color": "#888"})
        nid, name, x, y = node.get("id"), node.get("name", "Node"), node.get("x", 0), node.get("y", 0)
        color = info["color"]
        node_html.append(f'''
<div class="node" data-id="{nid}" data-type="{node.get('type')}" data-name="{name}" data-x="{x}" data-y="{y}"
     style="position:absolute;left:{x}px;top:{y}px;width:180px;background:#161b22;border:2px solid {color};border-radius:8px;cursor:grab;">
    <div class="header" style="padding:10px;background:{color}22;border-bottom:1px solid {color}44;border-radius:6px 6px 0 0;display:flex;align-items:center;gap:8px;">
        <span style="font-size:18px">{info["icon"]}</span>
        <span style="font-weight:600;color:#fff;font-size:14px">{name}</span>
    </div>
    <div style="padding:8px 12px;"><div style="font-size:11px;color:#8b949e;text-transform:uppercase">{info["label"]}</div></div>
    <div class="port in" data-node="{nid}" style="position:absolute;left:-6px;top:50%;width:12px;height:12px;background:#8b949e;border-radius:50%;border:2px solid #161b22;cursor:crosshair;"></div>
    <div class="port out" data-node="{nid}" style="position:absolute;right:-6px;top:50%;width:12px;height:12px;background:{color};border-radius:50%;border:2px solid #161b22;cursor:crosshair;"></div>
</div>''')
    
    # Build connection SVG
    conn_svg = ['<svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;">']
    conn_svg.append('<defs><marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#666"/></marker></defs>')
    
    node_map = {n["id"]: n for n in nodes}
    for conn in connections:
        src, tgt = node_map.get(conn.get("source")), node_map.get(conn.get("target"))
        if src and tgt:
            x1, y1 = src.get("x", 0) + 180, src.get("y", 0) + 40
            x2, y2 = tgt.get("x", 0), tgt.get("y", 0) + 40
            conn_svg.append(f'<path d="M {x1} {y1} C {x1+50} {y1}, {x2-50} {y2}, {x2} {y2}" stroke="#666" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
            if conn.get("label"):
                conn_svg.append(f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2-10}" fill="#8b949e" font-size="11" text-anchor="middle">{conn["label"]}</text>')
    conn_svg.append('</svg>')
    
    return f'''
<div id="canvas" style="width:100%;height:500px;position:relative;overflow:hidden;background:#0d1117;border:1px solid #30363d;border-radius:8px;">
    <div style="position:absolute;top:10px;right:10px;color:#8b949e;font-size:12px;">Drag nodes • Scroll to zoom • Right-click to pan</div>
    {''.join(conn_svg)}
    {''.join(node_html)}
</div>
<script>
(function(){{
    const canvas = document.getElementById('canvas');
    let nodes = {json.dumps(nodes)};
    let connections = {json.dumps(connections)};
    let selected = null;
    let dragging = null;
    let scale = 1;
    
    canvas.querySelectorAll('.node').forEach(el => {{
        const header = el.querySelector('.header');
        header.onmousedown = e => {{
            e.preventDefault();
            dragging = {{ el, ox: e.clientX, oy: e.clientY, startX: parseFloat(el.dataset.x), startY: parseFloat(el.dataset.y) }};
            el.style.zIndex = 100;
        }};
        el.onclick = e => {{
            e.stopPropagation();
            selected = el.dataset.id;
            canvas.querySelectorAll('.node').forEach(n => n.style.borderColor = NODE_TYPES[n.dataset.type]?.color || '#888');
            el.style.borderColor = '#58a6ff';
            const node = nodes.find(n => n.id === selected);
            if (window.parent?.updateNode) window.parent.updateNode(node);
        }};
    }});
    
    canvas.onmousemove = e => {{
        if (dragging) {{
            const dx = (e.clientX - dragging.ox) / scale;
            const dy = (e.clientY - dragging.oy) / scale;
            dragging.el.style.left = (dragging.startX + dx) + 'px';
            dragging.el.style.top = (dragging.startY + dy) + 'px';
        }}
    }};
    
    canvas.onmouseup = e => {{
        if (dragging) {{
            const node = nodes.find(n => n.id === dragging.el.dataset.id);
            if (node) {{
                node.x = Math.round(parseFloat(dragging.el.style.left));
                node.y = Math.round(parseFloat(dragging.el.style.top));
            }}
            dragging.el.style.zIndex = '';
            dragging = null;
            if (window.parent?.onWorkflowChange) window.parent.onWorkflowChange({{ nodes, connections }});
        }}
    }};
    
    canvas.onwheel = e => {{
        e.preventDefault();
        scale *= e.deltaY > 0 ? 0.9 : 1.1;
        scale = Math.max(0.5, Math.min(2, scale));
        canvas.style.transform = `scale(${{scale}})`;
        canvas.style.transformOrigin = 'top left';
    }};
    
    window.canvasAPI = {{
        setWorkflow: wf => {{ nodes = wf.nodes; connections = wf.connections; location.reload(); }},
        getWorkflow: () => ({{ nodes, connections }}),
    }};
}})();
</script>
'''


def add_node(workflow, node_type):
    """Add a node to workflow."""
    info = NODE_TYPES.get(node_type, {"label": "Node"})
    nid = f"n{len(workflow.get('nodes', [])) + 1}_{int(__import__('time').time())}"
    workflow.setdefault("nodes", []).append({
        "id": nid, "type": node_type, "name": info["label"],
        "x": 100 + len(workflow["nodes"]) * 30, "y": 150,
    })
    return workflow, render_canvas(workflow), generate_code(workflow)


def load_template(workflow, name):
    """Load a template."""
    tpl = TEMPLATES.get(name, {})
    return {"nodes": tpl.get("nodes", []), "connections": tpl.get("connections", [])}, render_canvas(workflow), generate_code(workflow)


def clear_canvas(workflow):
    """Clear the canvas."""
    return {"nodes": [], "connections": []}, render_canvas({"nodes": [], "connections": []}), generate_code({"nodes": [], "connections": []})


def export_json(workflow):
    """Export as JSON."""
    return json.dumps(workflow, indent=2)


def run_workflow(workflow):
    """Simulate running."""
    lines = ["🚀 Running workflow..."]
    for n in workflow.get("nodes", []):
        lines.append(f"  ▶️ {n.get('name')} ({n.get('type')})")
    lines.append("✅ Complete!")
    return "\n".join(lines)


def update_node_config(workflow, node_id, name, config_json):
    """Update node configuration."""
    for node in workflow.get("nodes", []):
        if node.get("id") == node_id:
            if name:
                node["name"] = name
            try:
                node["config"] = json.loads(config_json) if config_json else {}
            except:
                pass
    return workflow, render_canvas(workflow), generate_code(workflow)


def delete_node(workflow, node_id):
    """Delete a node."""
    workflow["nodes"] = [n for n in workflow.get("nodes", []) if n.get("id") != node_id]
    workflow["connections"] = [c for c in workflow.get("connections", []) if c.get("source") != node_id and c.get("target") != node_id]
    return workflow, render_canvas(workflow), generate_code(workflow)


def create_builder_ui():
    """Create the workflow builder UI."""
    with gr.Blocks(title="Piranha Workflow Builder") as ui:
        gr.Markdown("# 🛠️ Piranha Workflow Builder")
        
        workflow_state = gr.State({"nodes": [], "connections": []})
        
        # Toolbar
        with gr.Row():
            template_dd = gr.Dropdown(choices=list(TEMPLATES.keys()), label="Template", scale=1)
            with gr.Column(scale=2):
                with gr.Row():
                    for ntype, info in list(NODE_TYPES.items())[:4]:
                        gr.Button(f"{info['icon']} {info['label']}", size="sm").click(
                            add_node, inputs=[workflow_state, gr.State(ntype)],
                            outputs=[workflow_state, gr.HTML(), gr.Code()]
                        )
            export_btn = gr.Button("📤 JSON", size="sm")
            run_btn = gr.Button("▶️ Run", variant="primary", size="sm")
            clear_btn = gr.Button("🗑️ Clear", variant="stop", size="sm")
        
        # Canvas
        canvas = gr.HTML(value='<div style="width:100%;height:500px;background:#0d1117;display:flex;align-items:center;justify-content:center;color:#888;">Select a template or add nodes</div>', label="Canvas")
        
        # More node buttons
        with gr.Row():
            for ntype, info in list(NODE_TYPES.items())[4:]:
                gr.Button(f"{info['icon']} {info['label']}", size="sm").click(
                    add_node, inputs=[workflow_state, gr.State(ntype)],
                    outputs=[workflow_state, gr.HTML(), gr.Code()]
                )
        
        # Config
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Config")
                cfg_id = gr.Textbox(label="ID", interactive=False)
                cfg_name = gr.Textbox(label="Name")
                cfg_type = gr.Textbox(label="Type", interactive=False)
                cfg_json = gr.Code(label="Config (JSON)", language="json", lines=4)
                update_btn = gr.Button("✅ Update", size="sm")
                delete_btn = gr.Button("🗑️ Delete", size="sm")
            with gr.Column(scale=2):
                gr.Markdown("### Code")
                code_out = gr.Code(label="Python", language="python", lines=15)
        
        run_out = gr.Textbox(label="Output", lines=4, visible=False)
        
        # Wire up
        template_dd.change(load_template, inputs=[workflow_state, template_dd], outputs=[workflow_state, canvas, code_out])
        clear_btn.click(clear_canvas, inputs=[workflow_state], outputs=[workflow_state, canvas, code_out])
        export_btn.click(export_json, inputs=[workflow_state], outputs=[code_out])
        run_btn.click(run_workflow, inputs=[workflow_state], outputs=[run_out])
        update_btn.click(update_node_config, inputs=[workflow_state, cfg_id, cfg_name, cfg_json], outputs=[workflow_state, canvas, code_out])
        delete_btn.click(delete_node, inputs=[workflow_state, cfg_id], outputs=[workflow_state, canvas, code_out])
    
    return ui


if __name__ == "__main__":
    ui = create_builder_ui()
    ui.launch(server_name="0.0.0.0", server_port=7861, inbrowser=True)
