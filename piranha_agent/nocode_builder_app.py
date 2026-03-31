import gradio as gr
# import time  # Not used
# import asyncio  # Not used
# import json  # Not used
from piranha_agent.nocode_builder import NODE_CATEGORIES, TEMPLATES, generate_code, render_canvas, add_node, update_node_config, delete_node, load_template, clear_canvas, populate_sidebar

def create_builder_ui():
    """Create functional UI."""
    with gr.Blocks(title="Piranha Workflow Builder") as ui:
        gr.Markdown("# 🛠️ Piranha Workflow Builder\nBuild AI agent workflows visually")
        
        workflow_state = gr.State({"nodes": [], "connections": []})
        
        with gr.Row():
            # Left sidebar - Node palette
            with gr.Column(scale=1, min_width=220):
                gr.Markdown("### 📦 Node Library")
                node_buttons = []
                for cat_name, cat_nodes in NODE_CATEGORIES.items():
                    gr.Markdown(f"**{cat_name}**")
                    for ntype, info in cat_nodes.items():
                        btn = gr.Button(f"{info['icon']} {info['label']}", size="sm", variant="secondary")
                        node_buttons.append((btn, ntype))
                    gr.Markdown("---")
            
            # Center - Canvas and toolbar
            with gr.Column(scale=3):
                with gr.Row():
                    template_dd = gr.Dropdown(choices=list(TEMPLATES.keys()), label="📋 Load Template", scale=2)
                    clear_btn = gr.Button("🗑️ Clear", variant="stop", size="sm", scale=0)
                    run_btn = gr.Button("▶️ Run", variant="primary", size="sm", scale=0)
                
                canvas = gr.HTML(value=render_canvas({"nodes": [], "connections": []}), variant="panel")
                
                gr.Markdown("### 📄 Generated Code")
                code_out = gr.Code(label="Python", language="python", lines=12)
            
            # Right sidebar - Configuration
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("### ⚙️ Configuration")
                node_selector = gr.Dropdown(label="Select Node to Edit", choices=[])
                cfg_name = gr.Textbox(label="Node Name")
                cfg_type = gr.Textbox(label="Type", interactive=False)
                
                with gr.Row():
                    update_btn = gr.Button("✅ Update", variant="primary", size="sm")
                    delete_btn = gr.Button("🗑️ Delete", variant="stop", size="sm")
                
                gr.Markdown("---")
                gr.Markdown("### 📊 Workflow Stats")
                stats_out = gr.Markdown("No nodes added yet.")
        
        # Events
        def update_stats(wf):
            return f"Nodes: **{len(wf['nodes'])}** | Connections: **{len(wf['connections'])}**"

        # Bind Node Library Events
        for btn, ntype in node_buttons:
            btn.click(
                fn=add_node,
                inputs=[workflow_state, gr.State(ntype)],
                outputs=[workflow_state, canvas, code_out, node_selector],
            ).then(update_stats, workflow_state, stats_out)

        template_dd.change(
            fn=load_template,
            inputs=[template_dd],
            outputs=[workflow_state, canvas, code_out, node_selector],
        ).then(update_stats, workflow_state, stats_out)

        clear_btn.click(
            fn=clear_canvas,
            outputs=[workflow_state, canvas, code_out, node_selector],
        ).then(update_stats, workflow_state, stats_out)

        node_selector.change(
            fn=populate_sidebar,
            inputs=[workflow_state, node_selector],
            outputs=[cfg_name, cfg_type]
        )

        update_btn.click(
            fn=update_node_config,
            inputs=[workflow_state, node_selector, cfg_name],
            outputs=[workflow_state, canvas, code_out]
        ).then(update_stats, workflow_state, stats_out)

        delete_btn.click(
            fn=delete_node,
            inputs=[workflow_state, node_selector],
            outputs=[workflow_state, canvas, code_out, node_selector]
        ).then(update_stats, workflow_state, stats_out)

        run_btn.click(fn=lambda wf: gr.Info("Workflow execution started! Check console for output."), inputs=[workflow_state])
    
    return ui

if __name__ == "__main__":
    ui = create_builder_ui()
    ui.launch(server_name="127.0.0.1", server_port=7861, inbrowser=True)
