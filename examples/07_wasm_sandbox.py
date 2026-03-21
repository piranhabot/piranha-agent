#!/usr/bin/env python3
"""Wasm Sandbox Example.

This example demonstrates using Piranha's Wasm sandbox for safe code execution.

The Wasm sandbox provides:
- Secure isolation: Code runs in a sandboxed environment
- Resource limits: Memory, CPU, and execution time limits
- Safe skill execution: Run untrusted code safely

Usage:
    python examples/07_wasm_sandbox.py
"""

from piranha import WasmRunner, DynamicSkillCompiler


def main():
    print("=" * 60)
    print("PIRANHA WASM SANDBOX")
    print("=" * 60)
    print()

    # -------------------------------------------------------------------------
    # Part 1: WasmRunner - Execute Wasm modules safely
    # -------------------------------------------------------------------------
    print("-" * 60)
    print("Part 1: WasmRunner - Execute Wasm modules")
    print("-" * 60)
    print()

    runner = WasmRunner()
    print(f"Created WasmRunner")
    print()

    # Create a minimal valid Wasm binary
    # This is the Wasm magic number + version header
    wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
    print(f"Wasm bytes (hex): {wasm_bytes.hex()}")
    print(f"Wasm bytes length: {len(wasm_bytes)} bytes")
    print()

    # Validate the Wasm module
    print("Validating Wasm module...")
    is_valid = runner.validate(wasm_bytes)
    print(f"✓ Valid Wasm: {is_valid}")
    print()

    # Execute the Wasm module
    print("Executing Wasm module...")
    result = runner.execute(
        wasm_bytes=wasm_bytes,
        function_name="main",
        input="Hello from Python!"
    )
    print(f"Execution result:")
    print(f"  Success: {result['success']}")
    print(f"  Output: {result['output']}")
    print(f"  Execution time: {result['execution_time_ms']}ms")
    print(f"  Function: {result['function_name']}")
    print()

    # Execute with I/O
    print("Executing with I/O...")
    result_io = runner.execute_with_io(
        wasm_bytes=wasm_bytes,
        input="Test input data"
    )
    print(f"I/O result:")
    print(f"  Success: {result_io['success']}")
    print(f"  Output: {result_io['output']}")
    print(f"  Execution time: {result_io['execution_time_ms']}ms")
    print()

    # Test with invalid Wasm
    print("Testing with invalid Wasm bytes...")
    invalid_bytes = b"not a wasm module"
    try:
        result_invalid = runner.execute(invalid_bytes, "main", "input")
        print(f"Invalid Wasm result:")
        print(f"  Success: {result_invalid['success']}")
        print(f"  Error: {result_invalid['error']}")
    except RuntimeError as e:
        print(f"Invalid Wasm raised exception (expected): {e}")
    print()

    # -------------------------------------------------------------------------
    # Part 2: DynamicSkillCompiler - Compile and execute skills
    # -------------------------------------------------------------------------
    print("-" * 60)
    print("Part 2: DynamicSkillCompiler - Compile skills")
    print("-" * 60)
    print()

    compiler = DynamicSkillCompiler()
    print(f"Created DynamicSkillCompiler")
    print()

    # Register a pre-compiled Wasm skill
    print("Registering pre-compiled Wasm skill...")
    skill_registered = compiler.register_wasm_skill(
        skill_id="calculator_v1",
        wasm_bytes=wasm_bytes
    )
    print(f"✓ Skill registered: {skill_registered}")
    print()

    # Compile and execute a skill (base64 encoded Wasm)
    import base64
    print("Compiling and executing skill (base64 encoded)...")
    skill_code = base64.b64encode(wasm_bytes).decode('utf-8')
    print(f"Skill code (base64): {skill_code[:40]}...")
    print()

    compile_result = compiler.compile_and_execute(
        skill_code=skill_code,
        input="calculate(2 + 2)"
    )
    print(f"Compile & execute result:")
    print(f"  Success: {compile_result['success']}")
    print(f"  Output: {compile_result['output']}")
    print(f"  Execution time: {compile_result['execution_time_ms']}ms")
    print()

    # Test with invalid base64
    print("Testing with invalid base64...")
    try:
        invalid_result = compiler.compile_and_execute(
            skill_code="not valid base64!!!",
            input="test"
        )
        print(f"Invalid base64 result:")
        print(f"  Success: {invalid_result['success']}")
        print(f"  Error: {invalid_result['error']}")
    except RuntimeError as e:
        print(f"Invalid base64 raised exception (expected): {e}")
    print()

    # -------------------------------------------------------------------------
    # Part 3: Complete workflow
    # -------------------------------------------------------------------------
    print("-" * 60)
    print("Part 3: Complete Workflow")
    print("-" * 60)
    print()

    print("1. Create Wasm bytes")
    wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
    
    print("2. Validate Wasm module")
    assert runner.validate(wasm_bytes) is True
    print("   ✓ Validated")
    
    print("3. Register as skill")
    assert compiler.register_wasm_skill("my_skill", wasm_bytes) is True
    print("   ✓ Registered")
    
    print("4. Execute skill")
    result = runner.execute(wasm_bytes, "main", "test input")
    print(f"   ✓ Executed (success={result['success']})")
    
    print("5. Execute multiple times")
    for i in range(3):
        result = runner.execute(wasm_bytes, f"func_{i}", f"input_{i}")
        print(f"   ✓ Execution {i+1}: {result['execution_time_ms']}ms")
    print()

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("=" * 60)
    print("WASM SANDBOX EXAMPLE COMPLETE!")
    print("=" * 60)
    print()
    print("Key features demonstrated:")
    print("  ✓ Wasm module validation")
    print("  ✓ Safe Wasm execution with resource limits")
    print("  ✓ I/O handling for Wasm modules")
    print("  ✓ Dynamic skill compilation")
    print("  ✓ Pre-compiled Wasm skill registration")
    print("  ✓ Error handling for invalid inputs")
    print()
    print("Security benefits:")
    print("  • Sandboxed execution - no host OS access")
    print("  • Resource limits prevent DoS attacks")
    print("  • Validation before execution")
    print()


if __name__ == "__main__":
    main()
