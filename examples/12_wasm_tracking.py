#!/usr/bin/env python3
"""Wasm Execution Tracking Demo.

Demonstrates real-time Wasm execution tracking in Piranha Studio.

Usage:
    python examples/12_wasm_tracking.py
"""

from piranha_agent import start_monitoring, WasmRunner
import time


def main():
    print("=" * 70)
    print("WASM EXECUTION TRACKING DEMO")
    print("=" * 70)
    print()

    # Start monitoring
    print("Starting Piranha Studio with Wasm tracking...")
    monitor = start_monitoring(port=8080)
    print("✓ Studio started at http://localhost:8080")
    print()
    print("Open http://localhost:8080/wasm to see real-time Wasm logs")
    print()

    # Create Wasm runner
    runner = WasmRunner()
    print("✓ WasmRunner created")
    print()

    # Sample Wasm bytes (minimal valid Wasm)
    wasm_bytes = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
    
    print("Running Wasm executions (watch the UI for real-time updates)...")
    print()

    # Run several Wasm executions
    for i in range(5):
        print(f"Execution {i+1}/5...")
        
        try:
            # Execute Wasm (this will be tracked automatically)
            result = runner.execute(
                wasm_bytes=wasm_bytes,
                function_name="test_function",
                input_data=f"test_input_{i}"
            )
            
            # Track in monitor
            monitor.execute_wasm(
                wasm_bytes=wasm_bytes,
                function_name=f"function_{i}",
                input_data=f"input_{i}"
            )
            
            print(f"  ✓ Success: {result.get('success', False)}")
            print(f"  ✓ Time: {result.get('execution_time_ms', 0)}ms")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        time.sleep(1)
    
    print()
    print("=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print()
    print("View Wasm execution logs at:")
    print("  http://localhost:8080/wasm")
    print()
    print("Dashboard:")
    print("  http://localhost:8080")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Studio...")
        monitor.stop()
        print("Studio stopped.")


if __name__ == "__main__":
    main()
