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
