"""Tests for Wasm Sandbox Integration (Phase 2)."""

import pytest
from piranha_agent import DynamicSkillCompiler, WasmRunner


def wasm_with_export(func_name: str) -> bytes:
    """Build a minimal valid Wasm module that exports a no-op function
    under the given name, so execute()/execute_with_io() have something
    real to call (the bare 8-byte header has no functions at all)."""
    header = bytes([0x00, 0x61, 0x73, 0x6D, 0x01, 0x00, 0x00, 0x00])
    type_section = bytes([0x01, 0x04, 0x01, 0x60, 0x00, 0x00])
    func_section = bytes([0x03, 0x02, 0x01, 0x00])
    name_bytes = func_name.encode("utf-8")
    export_content = bytes([0x01, len(name_bytes)]) + name_bytes + bytes([0x00, 0x00])
    export_section = bytes([0x07, len(export_content)]) + export_content
    code_section = bytes([0x0A, 0x04, 0x01, 0x02, 0x00, 0x0B])
    return header + type_section + func_section + export_section + code_section


class TestWasmRunner:
    """Tests for the WasmRunner class."""

    def test_create_wasm_runner(self):
        """Test creating a WasmRunner."""
        runner = WasmRunner()
        assert runner is not None

    def test_validate_valid_wasm(self):
        """Test validating a valid Wasm module."""
        runner = WasmRunner()
        # Valid Wasm magic number: 0x00 0x61 0x73 0x6d (\0asm)
        valid_wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        result = runner.validate(valid_wasm_bytes)
        assert result is True

    def test_validate_invalid_wasm(self):
        """Test validating invalid Wasm bytes raises error."""
        runner = WasmRunner()
        invalid_bytes = b"not a wasm module"
        with pytest.raises(ValueError):
            runner.validate(invalid_bytes)

    def test_execute_valid_wasm(self):
        """Test executing a valid Wasm module."""
        runner = WasmRunner()
        wasm_bytes = wasm_with_export("main")

        result = runner.execute(wasm_bytes, "main", "test input")

        assert isinstance(result, dict)
        assert "success" in result
        assert "output" in result
        assert "error" in result
        assert "execution_time_ms" in result
        assert "function_name" in result

    def test_execute_with_io(self):
        """Test execute_with_io method."""
        runner = WasmRunner()
        # execute_with_io always invokes the WASI "_start" entry point.
        wasm_bytes = wasm_with_export("_start")

        result = runner.execute_with_io(wasm_bytes, "test input")

        assert isinstance(result, dict)
        assert "success" in result
        assert "output" in result
        assert result["success"] is True

    def test_execute_invalid_wasm(self):
        """Test executing invalid Wasm bytes raises error."""
        runner = WasmRunner()
        invalid_bytes = b"invalid"
        with pytest.raises(RuntimeError):
            runner.execute(invalid_bytes, "main", "input")

    def test_execute_result_structure(self):
        """Test that execute result has correct structure."""
        runner = WasmRunner()
        wasm_bytes = wasm_with_export("test_func")

        result = runner.execute(wasm_bytes, "test_func", "input")
        
        # Verify all expected keys are present
        expected_keys = ["success", "output", "error", "execution_time_ms", "function_name"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
        
        # Verify types
        assert isinstance(result["success"], bool)
        assert isinstance(result["output"], str)
        assert isinstance(result["execution_time_ms"], int)
        assert isinstance(result["function_name"], str)


class TestDynamicSkillCompiler:
    """Tests for the DynamicSkillCompiler class."""

    def test_create_compiler(self):
        """Test creating a DynamicSkillCompiler."""
        compiler = DynamicSkillCompiler()
        assert compiler is not None

    def test_register_wasm_skill(self):
        """Test registering a pre-compiled Wasm skill."""
        compiler = DynamicSkillCompiler()
        wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        
        result = compiler.register_wasm_skill("test_skill", wasm_bytes)
        
        assert result is True

    def test_register_invalid_wasm_skill(self):
        """Test registering invalid Wasm skill raises error."""
        compiler = DynamicSkillCompiler()
        invalid_bytes = b"not wasm"
        
        with pytest.raises(Exception):
            compiler.register_wasm_skill("bad_skill", invalid_bytes)

    def test_compile_and_execute_base64(self):
        """Test compile_and_execute genuinely runs the decoded Wasm module
        (it used to be a stub that only reported the decoded byte count
        without actually executing anything)."""
        import base64
        compiler = DynamicSkillCompiler()

        # compile_and_execute always targets the WASI "_start" entry point,
        # same convention as WasmRunner.execute_with_io.
        wasm_bytes = wasm_with_export("_start")
        skill_code = base64.b64encode(wasm_bytes).decode('utf-8')

        result = compiler.compile_and_execute(skill_code, "test input")

        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["output"] == "Execution successful"

    def test_compile_and_execute_reports_missing_entry_point(self):
        """A module with no "_start" export should fail execution, not
        silently report success like the old byte-count stub did."""
        import base64
        compiler = DynamicSkillCompiler()

        # Header-only module: no functions, so no "_start" to call.
        wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        skill_code = base64.b64encode(wasm_bytes).decode('utf-8')

        with pytest.raises(RuntimeError):
            compiler.compile_and_execute(skill_code, "test input")

    def test_compile_and_execute_invalid_base64(self):
        """Test compile_and_execute with invalid base64 raises error."""
        compiler = DynamicSkillCompiler()

        with pytest.raises(RuntimeError):
            compiler.compile_and_execute("not valid base64!!!", "input")

    def test_compile_and_execute_result_structure(self):
        """Test that compile_and_execute result has correct structure."""
        import base64
        compiler = DynamicSkillCompiler()

        wasm_bytes = wasm_with_export("_start")
        skill_code = base64.b64encode(wasm_bytes).decode('utf-8')

        result = compiler.compile_and_execute(skill_code, "input")

        # Verify all expected keys are present
        expected_keys = ["success", "output", "error", "execution_time_ms"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

        # Verify types
        assert isinstance(result["success"], bool)
        assert isinstance(result["output"], str)
        assert isinstance(result["execution_time_ms"], int)


class TestWasmIntegration:
    """Integration tests for Wasm functionality."""

    def test_wasm_runner_and_compiler_workflow(self):
        """Test complete workflow: validate, register, execute."""
        runner = WasmRunner()
        compiler = DynamicSkillCompiler()

        # Create valid Wasm bytes exporting "main"
        wasm_bytes = wasm_with_export("main")

        # 1. Validate
        assert runner.validate(wasm_bytes) is True

        # 2. Register skill
        assert compiler.register_wasm_skill("my_skill", wasm_bytes) is True

        # 3. Execute
        result = runner.execute(wasm_bytes, "main", "test")
        assert result["success"] is True

    def test_multiple_wasm_executions(self):
        """Test multiple consecutive Wasm executions."""
        runner = WasmRunner()

        results = []
        for i in range(5):
            wasm_bytes = wasm_with_export(f"func_{i}")
            result = runner.execute(wasm_bytes, f"func_{i}", f"input_{i}")
            results.append(result)
        
        # All should succeed
        assert all(r["success"] for r in results)
        
        # Execution times should be reasonable (< 1000ms each)
        assert all(r["execution_time_ms"] < 1000 for r in results)
