#!/usr/bin/env python3
"""No-Code Visual Agent Builder with Gradio - n8n-style Workflow Editor.

Full-featured drag-and-drop workflow builder with:
- Real drag-and-drop node positioning
- Interactive SVG connection drawing
- Node port/handle system
- Real-time Python code generation
- Import/Export workflows
"""

import json
import uuid
from dataclasses import dataclass, field
from typing import Optional

import gradio as gr


# =============================================================================
# Node Type Definitions
# =============================================================================

NODE_TYPES = {
    "trigger": {
        "icon": "⚡",
        "label": "Trigger",
        "color": "#FF6B6B",
        "description": "Start workflow execution",
        "config_fields": [
            {"name": "trigger_type", "type": "dropdown", "choices": ["manual", "schedule", "webhook"], "default": "manual"},
            {"name": "schedule", "type": "text", "placeholder": "Cron expression", "visible_if": {"trigger_type": "schedule"}},
            {"name": "webhook_path", "type": "text", "placeholder": "/webhook/endpoint", "visible_if": {"trigger_type": "webhook"}},
        ],
    },
    "agent": {
        "icon": "🤖",
        "label": "Agent",
        "color": "#4ECDC4",
        "description": "AI Agent for tasks",
        "config_fields": [
            {"name": "agent_name", "type": "text", "default": "assistant"},
            {"name": "model", "type": "dropdown", "choices": ["ollama/llama3:latest", "gpt-4", "claude-3-5-sonnet", "gemini-pro"], "default": "ollama/llama3:latest"},
            {"name": "system_prompt", "type": "textarea", "default": "You are a helpful AI assistant."},
            {"name": "temperature", "type": "slider", "min": 0, "max": 2, "step": 0.1, "default": 0.7},
        ],
    },
    "llm": {
        "icon": "💬",
        "label": "LLM Call",
        "color": "#95E1D3",
        "description": "Call LLM for processing",
        "config_fields": [
            {"name": "prompt", "type": "textarea", "default": "Process this input: {{input}}"},
            {"name": "model", "type": "dropdown", "choices": ["ollama/llama3:latest", "gpt-4", "claude-3-5-sonnet", "gemini-pro"], "default": "ollama/llama3:latest"},
            {"name": "temperature", "type": "slider", "min": 0, "max": 2, "step": 0.1, "default": 0.7},
        ],
    },
    "skill": {
        "icon": "🔧",
        "label": "Skill",
        "color": "#F38181",
        "description": "Execute a skill/function",
        "config_fields": [
            {"name": "skill_name", "type": "dropdown", "choices": ["web_search", "code_review", "text_summarizer", "sentiment_analysis", "translation"], "default": "web_search"},
            {"name": "input_mapping", "type": "text", "default": "{{input}}"},
        ],
    },
    "condition": {
        "icon": "🔀",
        "label": "Condition",
        "color": "#AA96DA",
        "description": "Conditional branching",
        "config_fields": [
            {"name": "condition", "type": "text", "default": "result > 0.5"},
            {"name": "true_label", "type": "text", "default": "Yes"},
            {"name": "false_label", "type": "text", "default": "No"},
        ],
    },
    "transform": {
        "icon": "🔁",
        "label": "Transform",
        "color": "#FFD93D",
        "description": "Transform data",
        "config_fields": [
            {"name": "transform_type", "type": "dropdown", "choices": ["json", "text", "extract", "format"], "default": "json"},
            {"name": "expression", "type": "textarea", "default": "{{input}}"},
        ],
    },
    "output": {
        "icon": "📤",
        "label": "Output",
        "color": "#6BCB77",
        "description": "Output result",
        "config_fields": [
            {"name": "output_type", "type": "dropdown", "choices": ["console", "file", "api"], "default": "console"},
            {"name": "format", "type": "dropdown", "choices": ["json", "text", "csv"], "default": "text"},
        ],
    },
    "http": {
        "icon": "🌐",
        "label": "HTTP Request",
        "color": "#4D96FF",
        "description": "Make HTTP requests",
        "config_fields": [
            {"name": "method", "type": "dropdown", "choices": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
            {"name": "url", "type": "text", "default": "https://api.example.com"},
            {"name": "headers", "type": "textarea", "default": "{}"},
        ],
    },
}


# =============================================================================
# Pre-built Templates
# =============================================================================

TEMPLATES = {
    "Basic Chat": {
        "description": "Simple conversational chat agent",
        "icon": "💬",
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Start", "config": {"trigger_type": "manual"}, "position": {"x": 100, "y": 150}},
            {"id": "n2", "type": "agent", "name": "Chat Agent", "config": {"agent_name": "assistant", "model": "ollama/llama3:latest"}, "position": {"x": 350, "y": 150}},
            {"id": "n3", "type": "output", "name": "Response", "config": {"output_type": "console"}, "position": {"x": 600, "y": 150}},
        ],
        "connections": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
        ],
    },
    "Research Assistant": {
        "description": "Research with web search and synthesis",
        "icon": "🔍",
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Query", "config": {"trigger_type": "manual"}, "position": {"x": 100, "y": 150}},
            {"id": "n2", "type": "skill", "name": "Web Search", "config": {"skill_name": "web_search"}, "position": {"x": 350, "y": 100}},
            {"id": "n3", "type": "llm", "name": "Analyze", "config": {"model": "ollama/llama3:latest", "prompt": "Analyze: {{input}}"}, "position": {"x": 600, "y": 100}},
            {"id": "n4", "type": "output", "name": "Report", "config": {"output_type": "console"}, "position": {"x": 850, "y": 100}},
        ],
        "connections": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
            {"source": "n3", "target": "n4"},
        ],
    },
    "Code Reviewer": {
        "description": "Review code and provide suggestions",
        "icon": "📝",
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Code", "config": {"trigger_type": "manual"}, "position": {"x": 100, "y": 150}},
            {"id": "n2", "type": "skill", "name": "Review", "config": {"skill_name": "code_review"}, "position": {"x": 350, "y": 150}},
            {"id": "n3", "type": "condition", "name": "Has Issues?", "config": {"condition": "issues > 0"}, "position": {"x": 600, "y": 150}},
            {"id": "n4", "type": "llm", "name": "Suggest", "config": {"model": "ollama/llama3:latest"}, "position": {"x": 850, "y": 80}},
            {"id": "n5", "type": "output", "name": "Report", "config": {"output_type": "console"}, "position": {"x": 850, "y": 220}},
        ],
        "connections": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
            {"source": "n3", "target": "n4", "label": "Yes"},
            {"source": "n3", "target": "n5", "label": "No"},
        ],
    },
    "Data Pipeline": {
        "description": "Process and analyze data",
        "icon": "📊",
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Data", "config": {"trigger_type": "manual"}, "position": {"x": 100, "y": 150}},
            {"id": "n2", "type": "transform", "name": "Clean", "config": {"transform_type": "json"}, "position": {"x": 350, "y": 150}},
            {"id": "n3", "type": "skill", "name": "Analyze", "config": {"skill_name": "statistical_analysis"}, "position": {"x": 600, "y": 150}},
            {"id": "n4", "type": "output", "name": "Result", "config": {"output_type": "console"}, "position": {"x": 850, "y": 150}},
        ],
        "connections": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
            {"source": "n3", "target": "n4"},
        ],
    },
    "API Integration": {
        "description": "Call external APIs",
        "icon": "🌐",
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Schedule", "config": {"trigger_type": "schedule", "schedule": "0 */6 * * *"}, "position": {"x": 100, "y": 150}},
            {"id": "n2", "type": "http", "name": "Fetch API", "config": {"method": "GET", "url": "https://api.example.com/data"}, "position": {"x": 350, "y": 150}},
            {"id": "n3", "type": "llm", "name": "Process", "config": {"model": "ollama/llama3:latest"}, "position": {"x": 600, "y": 150}},
            {"id": "n4", "type": "output", "name": "Save", "config": {"output_type": "console"}, "position": {"x": 850, "y": 150}},
        ],
        "connections": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
            {"source": "n3", "target": "n4"},
        ],
    },
}


# =============================================================================
# JavaScript for Canvas
# =============================================================================

CANVAS_JS = """
<script>
(function() {
    // Workflow state
    let workflowData = { nodes: [], connections: [] };
    let selectedNode = null;
    let draggingNode = null;
    let dragOffset = { x: 0, y: 0 };
    let connectingFrom = null;
    let tempConnection = null;
    let scale = 1;
    let panX = 0;
    let panY = 0;
    let isPanning = false;
    let panStart = { x: 0, y: 0 };

    // Initialize canvas
    function initCanvas() {
        const canvas = document.getElementById('workflow-canvas');
        if (!canvas) return;
        
        canvas.innerHTML = '';
        
        // Create SVG layer for connections
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.id = 'connections-svg';
        svg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1;';
        svg.innerHTML = '<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#666"/></marker></defs>';
        canvas.appendChild(svg);
        
        // Create nodes layer
        const nodesLayer = document.createElement('div');
        nodesLayer.id = 'nodes-layer';
        nodesLayer.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;z-index:2;';
        canvas.appendChild(nodesLayer);
        
        // Grid background
        canvas.style.background = `
            linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
        `;
        canvas.style.backgroundSize = '20px 20px';
        canvas.style.backgroundColor = '#0d1117';
        
        setupEventListeners(canvas);
        renderWorkflow();
    }

    function setupEventListeners(canvas) {
        // Mouse events for canvas
        canvas.addEventListener('mousedown', handleCanvasMouseDown);
        canvas.addEventListener('mousemove', handleCanvasMouseMove);
        canvas.addEventListener('mouseup', handleCanvasMouseUp);
        canvas.addEventListener('wheel', handleWheel);
        
        // Prevent context menu
        canvas.addEventListener('contextmenu', e => e.preventDefault());
    }

    function handleCanvasMouseDown(e) {
        if (e.target.id === 'workflow-canvas' || e.target.id === 'nodes-layer') {
            // Start panning
            isPanning = true;
            panStart = { x: e.clientX - panX, y: e.clientY - panY };
            canvas.style.cursor = 'grabbing';
        }
    }

    function handleCanvasMouseMove(e) {
        if (isPanning) {
            panX = e.clientX - panStart.x;
            panY = e.clientY - panStart.y;
            updateTransform();
        }
        
        if (draggingNode) {
            const canvas = document.getElementById('workflow-canvas');
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left - panX - dragOffset.x) / scale;
            const y = (e.clientY - rect.top - panY - dragOffset.y) / scale;
            
            draggingNode.style.left = x + 'px';
            draggingNode.style.top = y + 'px';
            
            // Update connection positions
            updateConnections();
        }
        
        if (connectingFrom) {
            updateTempConnection(e);
        }
    }

    function handleCanvasMouseUp(e) {
        isPanning = false;
        canvas.style.cursor = 'default';
        
        if (draggingNode) {
            // Save new position
            const nodeId = draggingNode.dataset.nodeId;
            const node = workflowData.nodes.find(n => n.id === nodeId);
            if (node) {
                const canvas = document.getElementById('workflow-canvas');
                const rect = canvas.getBoundingClientRect();
                node.position.x = Math.round((parseFloat(draggingNode.style.left) * scale + panX) / scale);
                node.position.y = Math.round((parseFloat(draggingNode.style.top) * scale + panY) / scale);
            }
            draggingNode = null;
            saveWorkflow();
        }
        
        if (connectingFrom && e.target.closest('.node-port')) {
            const port = e.target.closest('.node-port');
            const targetNodeId = port.dataset.nodeId;
            if (targetNodeId !== connectingFrom && targetNodeId !== connectingFrom) {
                // Create connection
                const existingConn = workflowData.connections.find(
                    c => c.source === connectingFrom && c.target === targetNodeId
                );
                if (!existingConn) {
                    workflowData.connections.push({
                        id: 'c' + Date.now(),
                        source: connectingFrom,
                        target: targetNodeId,
                    });
                    saveWorkflow();
                }
            }
        }
        
        connectingFrom = null;
        if (tempConnection) {
            tempConnection.remove();
            tempConnection = null;
        }
    }

    function handleWheel(e) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        scale = Math.max(0.5, Math.min(2, scale * delta));
        updateTransform();
    }

    function updateTransform() {
        const nodesLayer = document.getElementById('nodes-layer');
        const svg = document.getElementById('connections-svg');
        if (nodesLayer && svg) {
            nodesLayer.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
            svg.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
        }
    }

    function renderWorkflow() {
        const nodesLayer = document.getElementById('nodes-layer');
        if (!nodesLayer) return;
        
        nodesLayer.innerHTML = '';
        
        // Render nodes
        workflowData.nodes.forEach(node => {
            const nodeEl = createNodeElement(node);
            nodesLayer.appendChild(nodeEl);
        });
        
        // Render connections
        renderConnections();
    }

    function createNodeElement(node) {
        const nodeType = window.NODE_TYPES[node.type] || {};
        const color = nodeType.color || '#888';
        const icon = nodeType.icon || '📦';
        const label = nodeType.label || node.type;
        
        const nodeEl = document.createElement('div');
        nodeEl.className = 'workflow-node';
        nodeEl.dataset.nodeId = node.id;
        nodeEl.dataset.nodeType = node.type;
        nodeEl.style.cssText = `
            position: absolute;
            left: ${node.position.x}px;
            top: ${node.position.y}px;
            width: 200px;
            background: #161b22;
            border: 2px solid ${selectedNode === node.id ? '#58a6ff' : color};
            border-radius: 8px;
            padding: 0;
            cursor: grab;
            user-select: none;
            z-index: 10;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            transition: border-color 0.2s, box-shadow 0.2s;
        `;
        
        nodeEl.innerHTML = `
            <div class="node-header" style="
                padding: 10px 12px;
                background: ${color}22;
                border-bottom: 1px solid ${color}44;
                border-radius: 6px 6px 0 0;
                cursor: grab;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                <span style="font-size: 18px;">${icon}</span>
                <span style="font-weight: 600; color: #fff; font-size: 14px;">${node.name}</span>
            </div>
            <div class="node-body" style="padding: 8px 12px;">
                <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px;">${label}</div>
            </div>
            <div class="node-port node-port-input" data-node-id="${node.id}" data-port="input" style="
                position: absolute;
                left: -6px;
                top: 50%;
                transform: translateY(-50%);
                width: 12px;
                height: 12px;
                background: #8b949e;
                border-radius: 50%;
                border: 2px solid #161b22;
                cursor: crosshair;
                z-index: 20;
            "></div>
            <div class="node-port node-port-output" data-node-id="${node.id}" data-port="output" style="
                position: absolute;
                right: -6px;
                top: 50%;
                transform: translateY(-50%);
                width: 12px;
                height: 12px;
                background: ${color};
                border-radius: 50%;
                border: 2px solid #161b22;
                cursor: crosshair;
                z-index: 20;
            "></div>
        `;
        
        // Event listeners
        const header = nodeEl.querySelector('.node-header');
        header.addEventListener('mousedown', (e) => {
            e.preventDefault();
            draggingNode = nodeEl;
            const rect = nodeEl.getBoundingClientRect();
            dragOffset = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
            nodeEl.style.cursor = 'grabbing';
            nodeEl.style.zIndex = '100';
        });
        
        header.addEventListener('mouseup', () => {
            nodeEl.style.cursor = 'grab';
            nodeEl.style.zIndex = '10';
        });
        
        nodeEl.addEventListener('click', (e) => {
            e.stopPropagation();
            selectNode(node.id);
        });
        
        // Port event listeners
        const outputPort = nodeEl.querySelector('.node-port-output');
        outputPort.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            e.preventDefault();
            connectingFrom = node.id;
            startTempConnection(e, nodeEl);
        });
        
        const inputPort = nodeEl.querySelector('.node-port-input');
        inputPort.addEventListener('mouseup', (e) => {
            e.stopPropagation();
        });
        
        return nodeEl;
    }

    function startTempConnection(e, nodeEl) {
        const svg = document.getElementById('connections-svg');
        tempConnection = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        tempConnection.setAttribute('stroke', '#58a6ff');
        tempConnection.setAttribute('stroke-width', '2');
        tempConnection.setAttribute('fill', 'none');
        tempConnection.setAttribute('stroke-dasharray', '5,5');
        svg.appendChild(tempConnection);
    }

    function updateTempConnection(e) {
        if (!tempConnection || !connectingFrom) return;
        
        const fromNode = workflowData.nodes.find(n => n.id === connectingFrom);
        if (!fromNode) return;
        
        const canvas = document.getElementById('workflow-canvas');
        const rect = canvas.getBoundingClientRect();
        
        const x1 = fromNode.position.x + 200;
        const y1 = fromNode.position.y + 40;
        const x2 = (e.clientX - rect.left - panX) / scale;
        const y2 = (e.clientY - rect.top - panY) / scale;
        
        const d = `M ${x1} ${y1} C ${x1 + 50} ${y1}, ${x2 - 50} ${y2}, ${x2} ${y2}`;
        tempConnection.setAttribute('d', d);
    }

    function renderConnections() {
        const svg = document.getElementById('connections-svg');
        if (!svg) return;
        
        // Remove old connections (keep marker definition)
        const oldPaths = svg.querySelectorAll('path:not([stroke-dasharray])');
        oldPaths.forEach(p => p.remove());
        
        workflowData.connections.forEach(conn => {
            const sourceNode = workflowData.nodes.find(n => n.id === conn.source);
            const targetNode = workflowData.nodes.find(n => n.id === conn.target);
            
            if (!sourceNode || !targetNode) return;
            
            const x1 = sourceNode.position.x + 200;
            const y1 = sourceNode.position.y + 40;
            const x2 = targetNode.position.x;
            const y2 = targetNode.position.y + 40;
            
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            const d = `M ${x1} ${y1} C ${x1 + 50} ${y1}, ${x2 - 50} ${y2}, ${x2} ${y2}`;
            path.setAttribute('d', d);
            path.setAttribute('stroke', '#666');
            path.setAttribute('stroke-width', '2');
            path.setAttribute('fill', 'none');
            path.setAttribute('marker-end', 'url(#arrowhead)');
            path.style.cursor = 'pointer';
            path.style.pointerEvents = 'all';
            
            // Click to select/delete connection
            path.addEventListener('click', (e) => {
                if (confirm('Delete this connection?')) {
                    workflowData.connections = workflowData.connections.filter(c => c.id !== conn.id);
                    saveWorkflow();
                }
            });
            
            svg.appendChild(path);
            
            // Add label if present
            if (conn.label) {
                const midX = (x1 + x2) / 2;
                const midY = (y1 + y2) / 2 - 10;
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', midX);
                text.setAttribute('y', midY);
                text.setAttribute('fill', '#8b949e');
                text.setAttribute('font-size', '11');
                text.setAttribute('text-anchor', 'middle');
                text.textContent = conn.label;
                svg.appendChild(text);
            }
        });
    }

    function updateConnections() {
        renderConnections();
    }

    function selectNode(nodeId) {
        selectedNode = nodeId;
        const node = workflowData.nodes.find(n => n.id === nodeId);
        
        // Update visual selection
        document.querySelectorAll('.workflow-node').forEach(el => {
            const nodeType = window.NODE_TYPES[el.dataset.nodeType] || {};
            const color = nodeType.color || '#888';
            el.style.borderColor = el.dataset.nodeId === nodeId ? '#58a6ff' : color;
        });
        
        // Notify Gradio
        if (window.gradioUpdateSelected) {
            window.gradioUpdateSelected(nodeId, node);
        }
    }

    function saveWorkflow() {
        renderConnections();
        if (window.gradioSaveWorkflow) {
            window.gradioSaveWorkflow(workflowData);
        }
    }

    // Expose functions globally
    window.workflowCanvas = {
        init: initCanvas,
        setWorkflow: (data) => {
            workflowData = data;
            renderWorkflow();
        },
        getWorkflow: () => workflowData,
        addNode: (node) => {
            workflowData.nodes.push(node);
            renderWorkflow();
        },
        removeNode: (nodeId) => {
            workflowData.nodes = workflowData.nodes.filter(n => n.id !== nodeId);
            workflowData.connections = workflowData.connections.filter(
                c => c.source !== nodeId && c.target !== nodeId
            );
            renderWorkflow();
        },
        selectNode: selectNode,
        setScale: (s) => {
            scale = s;
            updateTransform();
        },
        fitView: () => {
            scale = 1;
            panX = 0;
            panY = 0;
            updateTransform();
        },
        clear: () => {
            workflowData = { nodes: [], connections: [] };
            renderWorkflow();
        },
    };
    
    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCanvas);
    } else {
        initCanvas();
    }
})();
</script>
"""


# =============================================================================
# Code Generator
# =============================================================================

def generate_code(workflow_data: dict) -> str:
    """Generate Python code from workflow data."""
    nodes = workflow_data.get("nodes", [])
    connections = workflow_data.get("connections", [])
    
    lines = [
        '#!/usr/bin/env python3',
        '"""Auto-generated Workflow"""',
        '',
        'from piranha import Agent, Task',
        'import json',
        '',
    ]
    
    # Build node map
    node_map = {n["id"]: n for n in nodes}
    
    # Generate node code
    for node in nodes:
        node_type = node.get("type", "llm")
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Node")
        config = node.get("config", {})
        
        lines.append(f'# {node_name} ({node_type})')
        
        if node_type == "agent":
            lines.append(f'''agent_{node_id} = Agent(
    name="{config.get('agent_name', 'agent')}",
    model="{config.get('model', 'ollama/llama3:latest')}",
)''')
        elif node_type == "llm":
            lines.append(f'''def run_{node_id}(input_data):
    from piranha.llm_provider import create_provider
    provider = create_provider("{config.get('model', 'ollama/llama3:latest')}")
    return provider.complete(
        prompt="{config.get('prompt', 'Process this')}",
        temperature={config.get('temperature', 0.7)},
    )''')
        elif node_type == "skill":
            lines.append(f'''def run_{node_id}(input_data):
    # Skill: {config.get('skill_name', 'unknown')}
    return input_data''')
        elif node_type == "trigger":
            lines.append(f'def run_{node_id}():')
            lines.append(f'    # Trigger: {config.get("trigger_type", "manual")}')
            lines.append('    return {}')
        elif node_type == "output":
            lines.append(f'''def run_{node_id}(input_data):
    print(f"Output: {{input_data}}")
    return input_data''')
        else:
            lines.append(f'def run_{node_id}(input_data):')
            lines.append('    return input_data')
        
        lines.append('')
    
    # Generate execution flow
    lines.append('# Execute workflow')
    lines.append('def run_workflow():')
    lines.append('    results = {}')
    lines.append('')
    
    # Simple sequential execution (topological sort would be better)
    for node in nodes:
        node_id = node["id"]
        lines.append(f'    # Run {node.get("name", node_id)}')
        if node.get("type") == "trigger":
            lines.append(f'    results["{node_id}"] = run_{node_id}()')
        else:
            lines.append(f'    results["{node_id}"] = run_{node_id}(results.get(list(results.keys())[-1], {{}}) if results else {{}})')
        lines.append('')
    
    lines.append('    return results')
    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    results = run_workflow()')
    lines.append('    print("Workflow completed!")')
    lines.append('    print(json.dumps(results, indent=2))')
    
    return '\n'.join(lines)


# =============================================================================
# UI Builder
# =============================================================================

def create_builder_ui():
    """Create the n8n-style Workflow Builder UI."""
    
    custom_css = """
    .workflow-container {
        background: #0d1117;
        border-radius: 12px;
        overflow: hidden;
    }
    .node-palette {
        background: #161b22;
        border-radius: 8px;
        padding: 12px;
    }
    .node-type-btn {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 10px;
        margin: 6px 0;
        cursor: grab;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .node-type-btn:hover {
        background: #30363d;
        transform: translateX(4px);
    }
    .toolbar {
        background: #21262d;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .config-panel {
        background: #161b22;
        border-radius: 8px;
        padding: 12px;
    }
    .gradio-container {
        max-width: 100% !important;
    }
    """
    
    with gr.Blocks(
        title="🛠️ Piranha Workflow Builder",
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="slate",
        ),
        css=custom_css,
    ) as ui:
        
        gr.Markdown("""
        # 🛠️ Piranha Workflow Builder
        
        Build AI agent workflows visually with drag-and-drop nodes.
        """)
        
        # State
        workflow_state = gr.State({"nodes": [], "connections": []})
        selected_node_state = gr.State(None)
        
        # Toolbar
        with gr.Row(elem_classes=["toolbar"]):
            workflow_name = gr.Textbox(
                label="Workflow Name",
                value="My Workflow",
                show_label=False,
                container=False,
                scale=2,
            )
            save_btn = gr.Button("💾 Save", variant="secondary", size="sm")
            export_json_btn = gr.Button("📤 Export", variant="secondary", size="sm")
            export_python_btn = gr.Button("🐍 Python", variant="secondary", size="sm")
            run_btn = gr.Button("▶️ Run", variant="primary", size="sm")
            clear_btn = gr.Button("🗑️ Clear", variant="stop", size="sm")
        
        # Main content
        with gr.Row():
            # Left - Node Palette
            with gr.Column(scale=1, min_width=200, elem_classes=["node-palette"]):
                gr.Markdown("### 📦 Nodes")
                
                # Template selector
                template_dropdown = gr.Dropdown(
                    choices=[f"{info['icon']} {name}" for name, info in TEMPLATES.items()],
                    label="Load Template",
                    show_label=True,
                )
                
                gr.Markdown("---")
                
                # Node type buttons
                for node_type, node_info in NODE_TYPES.items():
                    gr.HTML(f'''
                    <div class="node-type-btn" onclick="addNodeType('{node_type}')">
                        <span style="font-size: 20px;">{node_info['icon']}</span>
                        <div>
                            <div style="font-weight: 600; color: #fff;">{node_info['label']}</div>
                            <div style="font-size: 11px; color: #8b949e;">{node_info['description']}</div>
                        </div>
                    </div>
                    ''')
            
            # Center - Canvas
            with gr.Column(scale=3):
                # Canvas controls
                with gr.Row():
                    zoom_slider = gr.Slider(
                        minimum=0.5, maximum=2.0, value=1.0, step=0.1,
                        label="Zoom", show_label=False, container=False, scale=1
                    )
                    fit_btn = gr.Button("🔍 Fit", size="sm", scale=0)
                
                # Workflow canvas
                canvas_html = gr.HTML(
                    value=f'''
                    <div id="workflow-canvas" style="
                        width: 100%;
                        height: 500px;
                        position: relative;
                        overflow: hidden;
                        border: 1px solid #30363d;
                        border-radius: 8px;
                    "></div>
                    {CANVAS_JS}
                    <script>
                    window.NODE_TYPES = {json.dumps(NODE_TYPES)};
                    window.gradioSaveWorkflow = (data) => {{
                        // Save workflow data
                        console.log('Workflow saved:', data);
                    }};
                    </script>
                    ''',
                    label="Workflow Canvas",
                )
            
            # Right - Configuration
            with gr.Column(scale=1, min_width=250, elem_classes=["config-panel"]):
                gr.Markdown("### ⚙️ Configuration")
                
                config_node_id = gr.Textbox(label="Node ID", interactive=False)
                config_node_name = gr.Textbox(label="Node Name")
                config_node_type = gr.Textbox(label="Node Type", interactive=False)
                
                config_json = gr.Code(
                    label="Configuration (JSON)",
                    language="json",
                    lines=8,
                )
                
                with gr.Row():
                    update_btn = gr.Button("✅ Update", variant="primary", size="sm")
                    delete_btn = gr.Button("🗑️ Delete", variant="stop", size="sm")
                
                gr.Markdown("---")
                gr.Markdown("### 📊 Nodes")
                nodes_json = gr.JSON(label="Nodes", value=[])
                
                gr.Markdown("---")
                gr.Markdown("### 🔗 Connections")
                connections_json = gr.JSON(label="Connections", value=[])
        
        # Generated code
        with gr.Accordion("📄 Generated Code", open=False):
            generated_code = gr.Code(label="Python Code", language="python", lines=15)
        
        # Run output
        run_output = gr.Textbox(label="Run Output", lines=5, visible=False)
        
        # JavaScript for adding nodes
        add_node_js = """
        <script>
        function addNodeType(nodeType) {
            const canvas = window.workflowCanvas;
            if (!canvas) return;
            
            const node = {
                id: 'n' + Date.now(),
                type: nodeType,
                name: window.NODE_TYPES[nodeType]?.label || nodeType,
                config: {},
                position: {
                    x: 150 - (window.workflowCanvas.getWorkflow().nodes.length * 30),
                    y: 200
                }
            };
            
            canvas.addNode(node);
            canvas.selectNode(node.id);
        }
        </script>
        """
        gr.HTML(add_node_js)
        
        # Event: Load template
        def load_template(template_name):
            name = template_name.split(" ", 1)[1] if " " in template_name else template_name
            if name not in TEMPLATES:
                return {"nodes": [], "connections": []}, [], [], ""
            
            template = TEMPLATES[name]
            workflow_data = {
                "nodes": template.get("nodes", []),
                "connections": template.get("connections", []),
            }
            
            code = generate_code(workflow_data)
            return (
                workflow_data,
                workflow_data["nodes"],
                workflow_data["connections"],
                code,
            )
        
        template_dropdown.change(
            fn=load_template,
            inputs=[template_dropdown],
            outputs=[workflow_state, nodes_json, connections_json, generated_code],
        )
        
        # Event: Clear canvas
        def clear_workflow():
            return {"nodes": [], "connections": []}, [], [], ""
        
        clear_btn.click(
            fn=clear_workflow,
            outputs=[workflow_state, nodes_json, connections_json, generated_code],
        )
        
        # Event: Export Python
        def export_python(workflow: dict):
            return generate_code(workflow)
        
        export_python_btn.click(
            fn=export_python,
            inputs=[workflow_state],
            outputs=[generated_code],
        )
        
        # Event: Export JSON
        def export_json(workflow: dict):
            return json.dumps(workflow, indent=2)
        
        export_json_btn.click(
            fn=export_json,
            inputs=[workflow_state],
            outputs=[generated_code],
        )
        
        # Event: Run workflow
        def run_workflow(workflow: dict):
            lines = [
                "🚀 Running workflow...",
                "",
            ]
            for node in workflow.get("nodes", []):
                lines.append(f"  ▶️  {node.get('name', node.get('id'))} ({node.get('type')})")
            lines.append("")
            lines.append("✅ Workflow simulation complete!")
            return "\n".join(lines)
        
        run_btn.click(
            fn=run_workflow,
            inputs=[workflow_state],
            outputs=[run_output],
        )
    
    return ui


if __name__ == "__main__":
    ui = create_builder_ui()
    ui.launch(
        server_name="0.0.0.0",
        server_port=7861,
        inbrowser=True,
    )
