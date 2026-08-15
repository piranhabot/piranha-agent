"""Tests for the no-code workflow builder's data model, code generation,
and real workflow execution.

run_workflow() used to be entirely fake: clicking "Run" in the UI just
showed a gr.Info toast ("Workflow execution started!") and never actually
executed anything. Fixing that also surfaced two real bugs in
generate_code(): it called a nonexistent Task.run_async() and read a
nonexistent TaskResult.content attribute (Task.run() is sync and returns
a TaskResult with .result) - bugs that were invisible before because the
generated code was never actually run.
"""

from unittest.mock import patch

from piranha_agent.nocode_builder import (
    TEMPLATES,
    add_node,
    clear_canvas,
    delete_node,
    generate_code,
    load_template,
    run_workflow,
    update_node_config,
)


def _basic_chat_workflow():
    wf, _, _, _ = load_template("💬 Basic Chat")
    return wf


def test_generate_code_uses_real_task_api():
    """generate_code() must call Task's actual sync API, not a nonexistent
    async method or a nonexistent result attribute."""
    code = generate_code(_basic_chat_workflow())
    assert "task_n2.run()" in code
    assert ".result" in code
    assert "run_async" not in code
    assert ".content" not in code


def test_generate_code_includes_agent_and_task_setup():
    code = generate_code(_basic_chat_workflow())
    assert "Agent(name=" in code
    assert "Task(description=" in code


def test_all_templates_produce_syntactically_valid_code():
    """Every bundled template's generated code must at least be valid
    Python (catches the class of bug run_async/.content was)."""
    for name in TEMPLATES:
        wf, _, _, _ = load_template(name)
        code = generate_code(wf)
        compile(code, f"<template {name}>", "exec")


def test_http_node_generates_real_request():
    wf = {
        "nodes": [{"id": "n1", "type": "http", "name": "Fetch", "x": 0, "y": 0}],
        "connections": [],
    }
    code = generate_code(wf)
    assert "httpx.get(" in code
    compile(code, "<test>", "exec")


def test_llm_node_generates_direct_llm_call():
    wf = {
        "nodes": [{"id": "n1", "type": "llm", "name": "Ask", "x": 0, "y": 0}],
        "connections": [],
    }
    code = generate_code(wf)
    assert "LLMProvider(" in code
    assert "LLMMessage(" in code
    compile(code, "<test>", "exec")


def test_transform_node_generates_real_function():
    wf = {
        "nodes": [{"id": "n1", "type": "transform", "name": "Parse", "x": 0, "y": 0}],
        "connections": [],
    }
    code = generate_code(wf)
    assert "def transform_n1(data):" in code
    assert "transform_n1(input_data)" in code
    compile(code, "<test>", "exec")


def test_skill_node_generates_agent_backed_execution():
    wf = {
        "nodes": [{"id": "n1", "type": "skill", "name": "Search", "x": 0, "y": 0}],
        "connections": [],
    }
    code = generate_code(wf)
    assert 'agent_n1 = Agent(name="Search"' in code
    assert "register_complete_claude_skills(agent_n1)" in code
    compile(code, "<test>", "exec")


def test_condition_node_branches_on_connection_labels():
    """Nodes connected via a "Yes"-labeled edge must land inside the if
    branch; "No"-labeled nodes must land inside the else branch - this
    requires following the actual connection graph, not just node order."""
    wf = {
        "nodes": [
            {"id": "cond", "type": "condition", "name": "Check", "x": 0, "y": 0},
            {"id": "yes_node", "type": "output", "name": "YesOutput", "x": 0, "y": 0},
            {"id": "no_node", "type": "output", "name": "NoOutput", "x": 0, "y": 0},
        ],
        "connections": [
            {"source": "cond", "target": "yes_node", "label": "Yes"},
            {"source": "cond", "target": "no_node", "label": "No"},
        ],
    }
    code = generate_code(wf)
    compile(code, "<test>", "exec")

    if_block, _, else_block = code.partition("else:")
    assert "YesOutput" in if_block
    assert "NoOutput" not in if_block
    assert "NoOutput" in else_block
    assert "YesOutput" not in else_block


def test_condition_node_with_only_one_branch_still_compiles():
    wf = {
        "nodes": [
            {"id": "cond", "type": "condition", "name": "Check", "x": 0, "y": 0},
            {"id": "yes_node", "type": "output", "name": "YesOutput", "x": 0, "y": 0},
        ],
        "connections": [{"source": "cond", "target": "yes_node", "label": "Yes"}],
    }
    code = generate_code(wf)
    compile(code, "<test>", "exec")
    assert "else:" in code
    assert "pass" in code


def test_compose_node_is_distinct_from_transform():
    wf = {"nodes": [{"id": "n1", "type": "compose", "name": "Build"}], "connections": []}
    code = generate_code(wf)
    assert "composed_n1" in code
    assert "def transform_n1" not in code
    compile(code, "<test>", "exec")


def test_filter_node_generates_real_list_comprehension():
    wf = {"nodes": [{"id": "n1", "type": "filter", "name": "Keep"}], "connections": []}
    code = generate_code(wf)
    assert "[item for item in items_n1 if True]" in code
    compile(code, "<test>", "exec")


def test_apply_to_each_nests_child_nodes_inside_the_loop():
    wf = {
        "nodes": [
            {"id": "loop", "type": "apply_to_each", "name": "ForEach"},
            {"id": "body", "type": "output", "name": "PerItem"},
        ],
        "connections": [{"source": "loop", "target": "body"}],
    }
    code = generate_code(wf)
    compile(code, "<test>", "exec")

    for_line_idx = next(i for i, line in enumerate(code.splitlines()) if line.strip().startswith("for item_loop"))
    body_line_idx = next(i for i, line in enumerate(code.splitlines()) if "PerItem" in line)
    assert body_line_idx > for_line_idx
    body_line = code.splitlines()[body_line_idx]
    for_line = code.splitlines()[for_line_idx]
    assert len(body_line) - len(body_line.lstrip()) > len(for_line) - len(for_line.lstrip())


def test_apply_to_each_actually_loops_over_a_real_list():
    """End-to-end: the generated for-loop must genuinely iterate, not just
    compile - verified by running it and checking each item is processed."""
    wf = {
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Start"},
            {"id": "n2", "type": "apply_to_each", "name": "ForEachItem"},
            {"id": "n3", "type": "output", "name": "Item"},
        ],
        "connections": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
        ],
    }
    code = generate_code(wf).replace(
        'input_data = "Start workflow"', 'input_data = ["x", "y", "z"]'
    )
    with patch("piranha_agent.nocode_builder.generate_code", return_value=code):
        output = run_workflow(wf, timeout_seconds=30)
    assert output.count("--- Workflow Result ---") == 3
    assert "x" in output
    assert "y" in output
    assert "z" in output


def test_do_until_defaults_to_running_once_not_forever():
    """A do_until with an unimplemented condition must never hang - it
    should run its body once and stop by default."""
    wf = {"nodes": [{"id": "n1", "type": "do_until", "name": "Retry"}], "connections": []}
    code = generate_code(wf)
    assert "while True" not in code
    compile(code, "<test>", "exec")


def test_add_node_appends_and_auto_connects():
    wf = {"nodes": [], "connections": []}
    wf, _, _, _ = add_node(wf, "trigger")
    wf, _, _, _ = add_node(wf, "agent")

    assert len(wf["nodes"]) == 2
    assert len(wf["connections"]) == 1
    assert wf["connections"][0]["source"] == wf["nodes"][0]["id"]
    assert wf["connections"][0]["target"] == wf["nodes"][1]["id"]


def test_update_node_config_renames_node():
    wf, _, _, _ = add_node({"nodes": [], "connections": []}, "agent")
    node_id = wf["nodes"][0]["id"]

    wf, _, _ = update_node_config(wf, node_id, "Renamed Agent")

    assert wf["nodes"][0]["name"] == "Renamed Agent"


def test_delete_node_removes_node_and_its_connections():
    wf, _, _, _ = add_node({"nodes": [], "connections": []}, "trigger")
    wf, _, _, _ = add_node(wf, "agent")
    first_id = wf["nodes"][0]["id"]

    wf, _, _, _ = delete_node(wf, first_id)

    assert len(wf["nodes"]) == 1
    assert wf["connections"] == []


def test_clear_canvas_empties_workflow():
    wf, _, _, _ = add_node({"nodes": [], "connections": []}, "trigger")
    wf, _, _, _ = clear_canvas()
    assert wf == {"nodes": [], "connections": []}


def test_run_workflow_empty_workflow_does_not_spawn_a_process():
    result = run_workflow({"nodes": [], "connections": []})
    assert "nothing to run" in result.lower()


def test_run_workflow_actually_executes_generated_code():
    """run_workflow() must genuinely execute the generated code, not just
    claim it did - verified here by having the generated program print a
    sentinel and checking it comes back in the real captured output."""
    fake_code = (
        "print('SENTINEL_OUTPUT_12345')"
    )
    with patch("piranha_agent.nocode_builder.generate_code", return_value=fake_code):
        output = run_workflow({"nodes": [{"id": "n1", "type": "trigger", "name": "x"}], "connections": []})
    assert "SENTINEL_OUTPUT_12345" in output


def test_run_workflow_surfaces_real_errors():
    """A workflow whose generated code raises must report the real
    traceback, not silently report success."""
    fake_code = "raise RuntimeError('boom')"
    with patch("piranha_agent.nocode_builder.generate_code", return_value=fake_code):
        output = run_workflow({"nodes": [{"id": "n1", "type": "trigger", "name": "x"}], "connections": []})
    assert "boom" in output
    assert "exited with code" in output


def test_run_workflow_respects_timeout():
    fake_code = "import time; time.sleep(5)"
    with patch("piranha_agent.nocode_builder.generate_code", return_value=fake_code):
        output = run_workflow(
            {"nodes": [{"id": "n1", "type": "trigger", "name": "x"}], "connections": []},
            timeout_seconds=1,
        )
    assert "timed out" in output.lower()
