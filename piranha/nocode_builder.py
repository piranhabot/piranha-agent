#!/usr/bin/env python3
"""No-Code Visual Agent Builder - Clean categorized UI."""

import json
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
        "condition": {"icon": "🔀", "label": "Condition", "color": "#AA96DA", "desc": "Branch logic"},
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
    """Generate Python code."""
    nodes = workflow.get("nodes", [])
    lines = ['#!/usr/bin/env python3', '"""Auto-generated Workflow"""', "", "from piranha import Agent", "import json", ""]
    
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
        elif ntype == "http":
            lines.append(f"def run_{nid}(): return 'HTTP response'")
        elif ntype == "output":
            lines.append(f"def run_{nid}(data): print(f'Output: {{data}}')")
        else:
            lines.append(f"def run_{nid}(data): return data")
        lines.append("")
    
    lines.extend(["# Execute", "def run_workflow():", "    results = {}"])
    for node in nodes:
        nid = node["id"]
        if node.get("type") in ["trigger", "http"]:
            lines.append(f'    results["{nid}"] = run_{nid}()')
        else:
            lines.append(f'    results["{nid}"] = run_{nid}(results)')
    lines.extend(["    return results", "", 'if __name__ == "__main__":', "    print(run_workflow())"])
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
            if conn.get("label"):
                conn_paths.append(f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2-8}" fill="#8b949e" font-size="11" text-anchor="middle">{conn["label"]}</text>')
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
<div class="node" data-id="{nid}" data-type="{node.get('type')}" data-name="{name}" data-x="{x}" data-y="{y}"
     style="position:absolute;left:{x}px;top:{y}px;width:200px;background:#161b22;border:2px solid {color};border-radius:10px;cursor:grab;box-shadow:0 4px 12px rgba(0,0,0,0.3);">
    <div class="header" style="padding:12px;background:linear-gradient(135deg,{color}33,{color}11);border-bottom:1px solid {color}44;border-radius:8px 8px 0 0;display:flex;align-items:center;gap:10px;">
        <span style="font-size:20px">{icon}</span>
        <div>
            <div style="font-weight:600;color:#fff;font-size:14px">{name}</div>
            <div style="font-size:11px;color:#8b949e">{label}</div>
        </div>
    </div>
    <div style="padding:10px 12px;"><div style="font-size:11px;color:#6e7681;">Drag to move • Click to edit</div></div>
    <div class="port in" data-node="{nid}" style="position:absolute;left:-6px;top:35px;width:12px;height:12px;background:#8b949e;border-radius:50%;border:2px solid #161b22;cursor:crosshair;"></div>
    <div class="port out" data-node="{nid}" style="position:absolute;right:-6px;top:35px;width:12px;height:12px;background:{color};border-radius:50%;border:2px solid #161b22;cursor:crosshair;"></div>
</div>''')
    
    return f'''
<div id="canvas" style="width:100%;height:450px;position:relative;overflow:hidden;background:linear-gradient(135deg,#0d1117 0%,#161b22 100%);border:1px solid #30363d;border-radius:12px;">
    <div style="position:absolute;top:10px;right:10px;z-index:10;color:#8b949e;font-size:12px;background:#161b22;padding:6px 12px;border-radius:6px;">🖱️ Drag nodes • Scroll to zoom</div>
    {''.join(conn_paths)}
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
            el.style.boxShadow = '0 8px 24px rgba(0,0,0,0.5)';
        }};
        el.onclick = e => {{
            e.stopPropagation();
            selected = el.dataset.id;
            canvas.querySelectorAll('.node').forEach(n => {{
                const type = n.dataset.type;
                const colors = {json.dumps(node_colors)};
                n.style.borderColor = colors[type] || '#888';
            }});
            el.style.borderColor = '#58a6ff';
            const node = nodes.find(n => n.id === selected);
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
            dragging.el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
            dragging = null;
        }}
    }};
    
    canvas.onwheel = e => {{
        e.preventDefault();
        scale *= e.deltaY > 0 ? 0.9 : 1.1;
        scale = Math.max(0.5, Math.min(2, scale));
    }};
}})();
</script>
'''


def add_node(workflow, node_type):
    """Add a node."""
    all_nodes = {k: v for cat in NODE_CATEGORIES.values() for k, v in cat.items()}
    info = all_nodes.get(node_type, {"label": "Node"})
    nid = f"n{len(workflow.get('nodes', [])) + 1}_{int(time.time())[-4:]}"
    new_wf = {"nodes": list(workflow.get("nodes", [])), "connections": list(workflow.get("connections", []))}
    new_wf["nodes"].append({
        "id": nid, "type": node_type, "name": info["label"],
        "x": 50 + len(new_wf["nodes"]) * 30, "y": 180,
    })
    return new_wf, render_canvas(new_wf), generate_code(new_wf), new_wf.get("nodes", [])


def load_template(name):
    """Load template."""
    tpl = TEMPLATES.get(name, {})
    wf = {"nodes": list(tpl.get("nodes", [])), "connections": list(tpl.get("connections", []))}
    return wf, render_canvas(wf), generate_code(wf), wf.get("nodes", [])


def clear_canvas():
    """Clear."""
    wf = {"nodes": [], "connections": []}
    return wf, render_canvas(wf), generate_code(wf), []


def create_builder_ui():
    """Create UI."""
    with gr.Blocks(title="Piranha Workflow Builder") as ui:
        gr.Markdown("# 🛠️ Piranha Workflow Builder\nBuild AI agent workflows visually")
        
        workflow_state = gr.State({"nodes": [], "connections": []})
        
        with gr.Row():
            # Left sidebar - Node palette
            with gr.Column(scale=1, min_width=220):
                gr.Markdown("### 📦 Node Library")
                
                for cat_name, cat_nodes in NODE_CATEGORIES.items():
                    gr.Markdown(f"**{cat_name}**")
                    for ntype, info in cat_nodes.items():
                        btn = gr.Button(f"{info['icon']} {info['label']}", size="sm", variant="secondary")
                        btn.click(
                            fn=add_node,
                            inputs=[workflow_state, gr.State(ntype)],
                            outputs=[workflow_state, gr.HTML(variant="panel"), gr.Code(), gr.JSON(visible=False)],
                        )
                    gr.Markdown("---")
            
            # Center - Canvas and toolbar
            with gr.Column(scale=3):
                with gr.Row():
                    template_dd = gr.Dropdown(choices=list(TEMPLATES.keys()), label="📋 Load Template", scale=2)
                    clear_btn = gr.Button("🗑️ Clear", variant="stop", size="sm", scale=0)
                    export_btn = gr.Button("📤 Export", size="sm", scale=0)
                    run_btn = gr.Button("▶️ Run", variant="primary", size="sm", scale=0)
                
                canvas = gr.HTML(value=render_canvas({"nodes": [], "connections": []}), label="Workflow Canvas", variant="panel")
                
                gr.Markdown("### 📄 Generated Code")
                code_out = gr.Code(label="Python", language="python", lines=12)
            
            # Right sidebar - Configuration
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("### ⚙️ Configuration")
                cfg_id = gr.Textbox(label="Node ID", interactive=False)
                cfg_name = gr.Textbox(label="Node Name", placeholder="Enter name")
                cfg_type = gr.Textbox(label="Type", interactive=False)
                cfg_json = gr.Code(label="Config (JSON)", language="json", lines=5, value='{}')
                with gr.Row():
                    update_btn = gr.Button("✅ Update", variant="primary", size="sm")
                    delete_btn = gr.Button("🗑️ Delete", variant="stop", size="sm")
                
                gr.Markdown("---")
                gr.Markdown("### 📊 Workflow Info")
                info_out = gr.JSON(label="Nodes", value=[])
        
        run_out = gr.Textbox(label="🚀 Run Output", lines=5, visible=False)
        
        # Events
        template_dd.change(
            fn=load_template,
            inputs=[template_dd],
            outputs=[workflow_state, gr.HTML(variant="panel"), gr.Code(), info_out],
        )
        clear_btn.click(
            fn=clear_canvas,
            outputs=[workflow_state, gr.HTML(variant="panel"), gr.Code(), info_out],
        )
        export_btn.click(fn=lambda wf: json.dumps(wf, indent=2), inputs=[workflow_state], outputs=[code_out])
        run_btn.click(fn=lambda wf: "🚀 Running...\n" + "\n".join([f"  ▶️ {n.get('name')}" for n in wf.get("nodes", [])]) + "\n✅ Complete!", inputs=[workflow_state], outputs=[run_out])
    
    return ui


if __name__ == "__main__":
    ui = create_builder_ui()
    ui.launch(server_name="0.0.0.0", server_port=7861, inbrowser=True)
