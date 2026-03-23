#!/usr/bin/env python3
"""Ollama Local LLM Example.

This example demonstrates using Piranha with Ollama's local LLMs.

Prerequisites:
1. Install Ollama: https://ollama.ai
2. Pull a model: ollama pull llama3:latest
3. Start Ollama: ollama serve (or just run ollama run llama3:latest)

Usage:
    python examples/05_ollama_local.py
"""

import httpx
from piranha_agent import Agent, Task
from piranha_agent.skill import skill


# Define a skill for calling Ollama
@skill(
    name="ollama_chat",
    description="Chat with a local Ollama LLM",
    parameters={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "The prompt to send"},
            "model": {"type": "string", "description": "Model name (default: llama3:latest)"},
        },
        "required": ["prompt"],
    },
    permissions=["network_read", "network_write"],
)
def call_ollama(prompt: str, model: str = "llama3:latest") -> str:
    """Call Ollama API and return the response."""
    try:
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120.0,
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response from Ollama")
    except httpx.ConnectError:
        return "Error: Could not connect to Ollama. Is it running? (ollama serve)"
    except httpx.TimeoutException:
        return "Error: Ollama request timed out"
    except Exception as e:
        return f"Error calling Ollama: {str(e)}"


def check_ollama_running() -> bool:
    """Check if Ollama is running."""
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def main():
    print("=" * 60)
    print("PIRANHA WITH OLLAMA (LOCAL LLM)")
    print("=" * 60)
    print()
    
    # Check if Ollama is running
    print("Checking Ollama connection...")
    if not check_ollama_running():
        print("❌ Ollama is not running!")
        print()
        print("To start Ollama:")
        print("  1. Install: https://ollama.ai")
        print("  2. Pull model: ollama pull llama3:latest")
        print("  3. Run: ollama run llama3:latest")
        print()
        print("Then run this example again.")
        return
    
    print("✓ Ollama is running")
    
    # List available models
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        models = response.json().get("models", [])
        print(f"✓ Available models: {[m['name'] for m in models]}")
    except Exception as e:
        # Silently ignore if Ollama is not running or unavailable
        print(f"Note: Could not fetch available models: {e}")
    
    print()
    
    # Create an agent with Ollama skill
    agent = Agent(
        name="local_assistant",
        model="ollama/llama3:latest",
        description="A local AI assistant powered by Ollama",
        skills=[call_ollama],
    )
    
    print(f"Created agent: {agent.name}")
    print(f"Model: {agent.model}")
    print()
    
    # Test the Ollama skill directly
    print("-" * 60)
    print("Testing Ollama skill directly:")
    print("-" * 60)
    
    test_prompt = "What is 2 + 2? Answer in one word."
    print(f"Prompt: {test_prompt}")
    
    result = call_ollama(test_prompt)
    print(f"Response: {result}")
    print()
    
    # Create a task
    print("-" * 60)
    print("Running a task:")
    print("-" * 60)
    
    task = Task(
        description="Explain what Python is in 2 sentences",
        agent=agent,
        context="Use the ollama_chat skill to get the answer",
    )
    
    result = task.run()
    print(f"Task result: {result.result}")
    print()
    
    # Show session info
    print(f"Session: {agent.session}")
    print(f"Trace exported: {len(agent.export_trace())} bytes")
    
    print()
    print("=" * 60)
    print("OLLAMA INTEGRATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
