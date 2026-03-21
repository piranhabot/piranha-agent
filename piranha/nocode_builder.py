#!/usr/bin/env python3
"""No-Code Visual Agent Builder - n8n-style with full drag-and-drop.

This implementation uses a self-contained HTML/JS canvas that properly
handles drag-and-drop, connections, and node management.
"""

import json
import gradio as gr


# Node type definitions
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

# Templates
TEMPLATES = {
    "Basic Chat": {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Start", "position": {"x": 100, "y": 150}},
            {"id": "n2", "type": "agent", "name": "Chat Agent", "position": {"x": 350, "y": 150}},
            {"id": "n3", "type": "output", "name": "Response", "position": {"x": 600, "y": 150}},
        ],
        "connections": [{"source": "n1", "target": "n2"}, {"source": "n2", "target": "n3"}],
    },
    "Research": {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Query", "position": {"x": 100, "y": 150}},
            {"id": "n2", "type": "skill", "name": "Web Search", "position": {"x": 350, "y": 100}},
            {"id": "n3", "type": "llm", "name": "Analyze", "position": {"x": 600, "y": 100}},
            {"id": "n4", "type": "output", "name": "Report", "position": {"x": 850, "y": 100}},
        ],
        "connections": [{"source": "n1", "target": "n2"}, {"source": "n2", "target": "n3"}, {"source": "n3", "target": "n4"}],
    },
    "Code Review": {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Code", "position": {"x": 100, "y": 150}},
            {"id": "n2", "type": "skill", "name": "Review", "position": {"x": 350, "y": 150}},
            {"id": "n3", "type": "condition", "name": "Has Issues?", "position": {"x": 600, "y": 150}},
            {"id": "n4", "type": "llm", "name": "Suggest", "position": {"x": 850, "y": 80}},
            {"id": "n5", "type": "output", "name": "Report", "position": {"x": 850, "y": 220}},
        ],
        "connections": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
            {"source": "n3", "target": "n4", "label": "Yes"},
            {"source": "n3", "target": "n5", "label": "No"},
        ],
    },
}


def get_canvas_html():
    """Return the complete HTML/JS canvas."""
    return '''
<div id="app" style="width:100%;height:550px;position:relative;overflow:hidden;background:#0d1117;border:1px solid #30363d;border-radius:8px;">
    <svg id="connections" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1;">
        <defs>
            <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#666"/>
            </marker>
        </defs>
    </svg>
    <div id="nodes" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:2;"></div>
    <div id="palette" style="position:absolute;bottom:10px;left:10px;z-index:100;display:flex;gap:8px;">
    </div>
</div>

<script>
(function() {
    const NODE_TYPES = ''' + json.dumps(NODE_TYPES) + ''';
    const TEMPLATES = ''' + json.dumps(TEMPLATES) + ''';
    
    let workflow = { nodes: [], connections: [] };
    let selectedNode = null;
    let dragging = null;
    let connecting = null;
    let tempLine = null;
    let scale = 1;
    let pan = { x: 0, y: 0 };
    let isPanning = false;
    let panStart = { x: 0, y: 0 };
    
    // Initialize
    const app = document.getElementById('app');
    const nodesEl = document.getElementById('nodes');
    const svg = document.getElementById('connections');
    
    // Grid background
    app.style.backgroundImage = `
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
    `;
    app.style.backgroundSize = '20px 20px';
    
    // Create palette
    const palette = document.getElementById('palette');
    Object.entries(NODE_TYPES).forEach(([type, info]) => {
        const btn = document.createElement('div');
        btn.innerHTML = info.icon + ' ' + info.label;
        btn.style.cssText = `
            background: ${info.color}22;
            border: 1px solid ${info.color};
            color: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            user-select: none;
        `;
        btn.onmouseover = () => btn.style.background = info.color + '44';
        btn.onmouseout = () => btn.style.background = info.color + '22';
        btn.onclick = () => addNode(type);
        palette.appendChild(btn);
    });
    
    // Canvas events
    app.addEventListener('mousedown', e => {
        if (e.target === app || e.target === nodesEl) {
            isPanning = true;
            panStart = { x: e.clientX - pan.x, y: e.clientY - pan.y };
            app.style.cursor = 'grabbing';
        }
    });
    
    app.addEventListener('mousemove', e => {
        if (isPanning) {
            pan.x = e.clientX - panStart.x;
            pan.y = e.clientY - panStart.y;
            updateTransform();
        }
        if (dragging) {
            const rect = app.getBoundingClientRect();
            const x = (e.clientX - rect.left - pan.x - dragging.offset.x) / scale;
            const y = (e.clientY - rect.top - pan.y - dragging.offset.y) / scale;
            dragging.el.style.left = x + 'px';
            dragging.el.style.top = y + 'px';
            renderConnections();
        }
        if (connecting) {
            updateTempLine(e);
        }
    });
    
    app.addEventListener('mouseup', e => {
        if (isPanning) {
            isPanning = false;
            app.style.cursor = 'default';
        }
        if (dragging) {
            const node = workflow.nodes.find(n => n.id === dragging.el.dataset.id);
            if (node) {
                node.position.x = Math.round(parseFloat(dragging.el.style.left));
                node.position.y = Math.round(parseFloat(dragging.el.style.top));
            }
            dragging.el.style.zIndex = '';
            dragging = null;
            saveState();
        }
        if (connecting && e.target.classList.contains('port')) {
            const targetId = e.target.dataset.nodeId;
            if (targetId !== connecting.from) {
                const exists = workflow.connections.find(
                    c => c.source === connecting.from && c.target === targetId
                );
                if (!exists) {
                    workflow.connections.push({
                        id: 'c' + Date.now(),
                        source: connecting.from,
                        target: targetId,
                    });
                    renderConnections();
                    saveState();
                }
            }
        }
        if (tempLine) {
            tempLine.remove();
            tempLine = null;
        }
        connecting = null;
    });
    
    app.addEventListener('wheel', e => {
        e.preventDefault();
        scale *= e.deltaY > 0 ? 0.9 : 1.1;
        scale = Math.max(0.5, Math.min(2, scale));
        updateTransform();
    });
    
    function updateTransform() {
        nodesEl.style.transform = `translate(${pan.x}px, ${pan.y}px) scale(${scale})`;
        svg.style.transform = `translate(${pan.x}px, ${pan.y}px) scale(${scale})`;
    }
    
    function addNode(type, x, y) {
        const id = 'n' + Date.now();
        const node = {
            id: id,
            type: type,
            name: NODE_TYPES[type].label,
            position: { x: x || 150, y: y || 150 },
            config: {},
        };
        workflow.nodes.push(node);
        renderNodes();
        renderConnections();
        selectNode(id);
        saveState();
    }
    
    function renderNodes() {
        nodesEl.innerHTML = '';
        workflow.nodes.forEach(node => {
            const info = NODE_TYPES[node.type] || { icon: '📦', label: node.type, color: '#888' };
            const el = document.createElement('div');
            el.dataset.id = node.id;
            el.style.cssText = `
                position: absolute;
                left: ${node.position.x}px;
                top: ${node.position.y}px;
                width: 180px;
                background: #161b22;
                border: 2px solid ${selectedNode === node.id ? '#58a6ff' : info.color};
                border-radius: 8px;
                cursor: grab;
                user-select: none;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                z-index: ${selectedNode === node.id ? 100 : 10};
            `;
            el.innerHTML = `
                <div class="node-header" style="
                    padding: 10px 12px;
                    background: ${info.color}22;
                    border-bottom: 1px solid ${info.color}44;
                    border-radius: 6px 6px 0 0;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <span style="font-size:18px">${info.icon}</span>
                    <span style="font-weight:600;color:#fff;font-size:14px">${node.name}</span>
                </div>
                <div style="padding:8px 12px;">
                    <div style="font-size:11px;color:#8b949e;text-transform:uppercase">${info.label}</div>
                </div>
                <div class="port" data-node-id="${node.id}" data-port="in" style="
                    position:absolute;left:-6px;top:50%;transform:translateY(-50%);
                    width:12px;height:12px;background:#8b949e;border-radius:50%;
                    border:2px solid #161b22;cursor:crosshair;
                "></div>
                <div class="port" data-node-id="${node.id}" data-port="out" style="
                    position:absolute;right:-6px;top:50%;transform:translateY(-50%);
                    width:12px;height:12px;background:${info.color};border-radius:50%;
                    border:2px solid #161b22;cursor:crosshair;
                "></div>
            `;
            
            // Drag
            const header = el.querySelector('.node-header');
            header.onmousedown = e => {
                e.preventDefault();
                const rect = el.getBoundingClientRect();
                dragging = {
                    el: el,
                    offset: { x: e.clientX - rect.left, y: e.clientY - rect.top }
                };
                el.style.zIndex = 100;
            };
            
            // Select
            el.onclick = e => {
                e.stopPropagation();
                selectNode(node.id);
            };
            
            // Connect from output port
            const outPort = el.querySelector('[data-port="out"]');
            outPort.onmousedown = e => {
                e.stopPropagation();
                e.preventDefault();
                connecting = { from: node.id };
                createTempLine(e, node);
            };
            
            nodesEl.appendChild(el);
        });
    }
    
    function createTempLine(e, node) {
        tempLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        tempLine.setAttribute('stroke', '#58a6ff');
        tempLine.setAttribute('stroke-width', '2');
        tempLine.setAttribute('fill', 'none');
        tempLine.setAttribute('stroke-dasharray', '5,5');
        svg.appendChild(tempLine);
        updateTempLine(e);
    }
    
    function updateTempLine(e) {
        if (!tempLine || !connecting) return;
        const node = workflow.nodes.find(n => n.id === connecting.from);
        if (!node) return;
        const rect = app.getBoundingClientRect();
        const x1 = node.position.x + 180;
        const y1 = node.position.y + 40;
        const x2 = (e.clientX - rect.left - pan.x) / scale;
        const y2 = (e.clientY - rect.top - pan.y) / scale;
        const d = `M ${x1} ${y1} C ${x1+50} ${y1}, ${x2-50} ${y2}, ${x2} ${y2}`;
        tempLine.setAttribute('d', d);
    }
    
    function renderConnections() {
        // Remove old paths (keep marker)
        svg.querySelectorAll('path').forEach(p => p.remove());
        
        workflow.connections.forEach(conn => {
            const src = workflow.nodes.find(n => n.id === conn.source);
            const tgt = workflow.nodes.find(n => n.id === conn.target);
            if (!src || !tgt) return;
            
            const x1 = src.position.x + 180;
            const y1 = src.position.y + 40;
            const x2 = tgt.position.x;
            const y2 = tgt.position.y + 40;
            
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', `M ${x1} ${y1} C ${x1+50} ${y1}, ${x2-50} ${y2}, ${x2} ${y2}`);
            path.setAttribute('stroke', '#666');
            path.setAttribute('stroke-width', '2');
            path.setAttribute('fill', 'none');
            path.setAttribute('marker-end', 'url(#arrow)');
            path.style.pointerEvents = 'all';
            path.style.cursor = 'pointer';
            path.onclick = () => {
                if (confirm('Delete connection?')) {
                    workflow.connections = workflow.connections.filter(c => c.id !== conn.id);
                    renderConnections();
                    saveState();
                }
            };
            svg.appendChild(path);
            
            if (conn.label) {
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', (x1+x2)/2);
                text.setAttribute('y', (y1+y2)/2 - 10);
                text.setAttribute('fill', '#8b949e');
                text.setAttribute('font-size', '11');
                text.setAttribute('text-anchor', 'middle');
                text.textContent = conn.label;
                svg.appendChild(text);
            }
        });
    }
    
    function selectNode(id) {
        selectedNode = id;
        renderNodes();
        const node = workflow.nodes.find(n => n.id === id);
        if (window.parent && window.parent.updateConfig) {
            window.parent.updateConfig(id, node);
        }
    }
    
    function saveState() {
        if (window.parent && window.parent.saveWorkflow) {
            window.parent.saveWorkflow(workflow);
        }
    }
    
    function loadTemplate(name) {
        const tpl = TEMPLATES[name];
        if (!tpl) return;
        workflow = {
            nodes: JSON.parse(JSON.stringify(tpl.nodes)),
            connections: JSON.parse(JSON.stringify(tpl.connections || [])),
        };
        renderNodes();
        renderConnections();
        saveState();
    }
    
    function clearCanvas() {
        workflow = { nodes: [], connections: [] };
        renderNodes();
        renderConnections();
        saveState();
    }
    
    function getWorkflow() {
        return workflow;
    }
    
    // Expose API
    window.canvasAPI = {
        addNode, loadTemplate, clearCanvas, getWorkflow,
        setWorkflow: (w) => { workflow = w; renderNodes(); renderConnections(); },
    };
    
    // Initial render
    renderNodes();
    renderConnections();
})();
</script>
'''


def generate_code(workflow_data: dict) -> str:
    """Generate Python code from workflow."""
    nodes = workflow_data.get("nodes", [])
    connections = workflow_data.get("connections", [])
    
    lines = [
        '#!/usr/bin/env python3',
        '"""Auto-generated Workflow"""',
        '',
        'from piranha import Agent',
        'import json',
        '',
    ]
    
    for node in nodes:
        node_type = node.get("type")
        node_id = node.get("id")
        name = node.get("name", "Node")
        config = node.get("config", {})
        
        lines.append(f'# {name} ({node_type})')
        
        if node_type == "agent":
            lines.append(f'agent_{node_id} = Agent(name="{config.get("agent_name", "agent")}", model="{config.get("model", "ollama/llama3:latest")}"))')
        elif node_type == "llm":
            lines.append(f'def run_{node_id}(data): return "LLM response"')
        elif node_type == "skill":
            lines.append(f'def run_{node_id}(data): return "Skill result"')
        elif node_type == "trigger":
            lines.append(f'def run_{node_id}(): return {{}}')
        elif node_type == "output":
            lines.append(f'def run_{node_id}(data): print(f"Output: {{data}}")')
        else:
            lines.append(f'def run_{node_id}(data): return data')
        lines.append('')
    
    lines.append('# Execute')
    lines.append('def run_workflow():')
    lines.append('    results = {}')
    for node in nodes:
        node_id = node["id"]
        if node.get("type") == "trigger":
            lines.append(f'    results["{node_id}"] = run_{node_id}()')
        else:
            lines.append(f'    results["{node_id}"] = run_{node_id}(results)')
    lines.append('    return results')
    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    print(run_workflow())')
    
    return '\n'.join(lines)


def create_builder_ui():
    """Create the workflow builder UI."""

    with gr.Blocks(
        title="Piranha Workflow Builder",
    ) as ui:
        gr.Markdown("# 🛠️ Piranha Workflow Builder - Drag & Drop")

        workflow_state = gr.State({"nodes": [], "connections": []})

        # Toolbar
        with gr.Row():
            template_select = gr.Dropdown(
                choices=list(TEMPLATES.keys()),
                label="Load Template",
                scale=1,
            )
            zoom_slider = gr.Slider(0.5, 2.0, 1.0, 0.1, label="Zoom", scale=1)
            fit_btn = gr.Button("🔍 Fit", size="sm", scale=0)
            export_btn = gr.Button("📤 Export", size="sm", scale=0)
            run_btn = gr.Button("▶️ Run", variant="primary", size="sm", scale=0)
            clear_btn = gr.Button("🗑️ Clear", variant="stop", size="sm", scale=0)

        # Canvas
        canvas = gr.HTML(value=get_canvas_html(), label="Workflow Canvas")

        # Config panel
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Node Configuration")
                config_id = gr.Textbox(label="Node ID", interactive=False)
                config_name = gr.Textbox(label="Node Name")
                config_type = gr.Textbox(label="Type", interactive=False)
                config_json = gr.Code(label="Config (JSON)", language="json", lines=6)
                update_btn = gr.Button("✅ Update", variant="primary", size="sm")
                delete_btn = gr.Button("🗑️ Delete", variant="stop", size="sm")
            with gr.Column(scale=2):
                gr.Markdown("### 📄 Generated Code")
                code_output = gr.Code(label="Python Code", language="python", lines=20)

        run_output = gr.Textbox(label="Output", lines=5, visible=False)

        # Load template - just update workflow state, code is generated via JS
        def load_template(name):
            tpl = TEMPLATES.get(name, {})
            return {"nodes": tpl.get("nodes", []), "connections": tpl.get("connections", [])}

        template_select.change(load_template, inputs=[template_select], outputs=[workflow_state])

        # Clear
        def clear():
            return {"nodes": [], "connections": []}

        clear_btn.click(clear, outputs=[workflow_state])

        # Export
        def export(wf):
            return json.dumps(wf, indent=2)
        
        export_btn.click(export, inputs=[workflow_state], outputs=[code_output])
        
        # Run
        def run_wf(wf):
            lines = ["🚀 Running workflow..."]
            for n in wf.get("nodes", []):
                lines.append(f"  ▶️ {n.get('name')} ({n.get('type')})")
            lines.append("✅ Complete!")
            return "\n".join(lines)
        
        run_btn.click(run_wf, inputs=[workflow_state], outputs=[run_output])
    
    return ui


if __name__ == "__main__":
    ui = create_builder_ui()
    ui.launch(server_name="0.0.0.0", server_port=7861, inbrowser=True)
