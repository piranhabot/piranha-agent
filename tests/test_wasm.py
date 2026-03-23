"""Tests for Wasm Sandbox Integration (Phase 2)."""

import pytest
from piranha_agent import WasmRunner, DynamicSkillCompiler


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
        # Minimal valid Wasm binary (magic number + version)
        wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        
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
        wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        
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
        wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        
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
        """Test compile_and_execute with base64 encoded Wasm."""
        import base64
        compiler = DynamicSkillCompiler()
        
        # Create valid Wasm bytes and encode as base64
        wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        skill_code = base64.b64encode(wasm_bytes).decode('utf-8')
        
        result = compiler.compile_and_execute(skill_code, "test input")
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "output" in result
        assert result["success"] is True
        assert "bytes" in result["output"].lower()  # Should mention byte count

    def test_compile_and_execute_invalid_base64(self):
        """Test compile_and_execute with invalid base64 raises error."""
        compiler = DynamicSkillCompiler()
        
        with pytest.raises(RuntimeError):
            compiler.compile_and_execute("not valid base64!!!", "input")

    def test_compile_and_execute_result_structure(self):
        """Test that compile_and_execute result has correct structure."""
        import base64
        compiler = DynamicSkillCompiler()
        
        wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
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
        
        # Create valid Wasm bytes
        wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        
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
        wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        
        results = []
        for i in range(5):
            result = runner.execute(wasm_bytes, f"func_{i}", f"input_{i}")
            results.append(result)
        
        # All should succeed
        assert all(r["success"] for r in results)
        
        # Execution times should be reasonable (< 1000ms each)
        assert all(r["execution_time_ms"] < 1000 for r in results)
