#!/usr/bin/env python3
"""Complete example demonstrating all Piranha features.

This example shows:
- LiteLLM integration (Ollama, OpenAI, etc.)
- Async agent execution
- Streaming responses
- Memory and context management
- Multi-agent coordination
"""

import asyncio

from piranha_agent import (
    Agent,
    AgentGroup,
    AsyncAgent,
    ContextManager,
    MemoryManager,
)
from piranha_agent.llm_provider import LLMMessage, LLMProvider

# =============================================================================
# Feature 1: LiteLLM Integration
# =============================================================================

def demo_llm_provider():
    """Demonstrate LiteLLM provider with multiple backends."""
    print("\n" + "=" * 60)
    print("FEATURE 1: LiteLLM Integration")
    print("=" * 60)
    
    # Ollama (local)
    ollama = LLMProvider(
        model="ollama/llama3:latest",
        api_base="http://localhost:11434",
    )

    messages = [LLMMessage(role="user", content="Say hello in one word")]
    
    try:
        response = ollama.chat(messages)
        print(f"✓ Ollama response: {response.content[:50]}...")
        print(f"  Model: {response.model}")
        print(f"  Tokens: {response.total_tokens}")
    except Exception as e:
        print(f"⚠ Ollama not available: {e}")
    
    # You can also use cloud providers:
    # openai = LLMProvider(model="gpt-4", api_key="sk-...")
    # anthropic = LLMProvider(model="claude-3-5-sonnet", api_key="...")


# =============================================================================
# Feature 2: Async Agent Execution
# =============================================================================

async def demo_async_agent():
    """Demonstrate async agent execution."""
    print("\n" + "=" * 60)
    print("FEATURE 2: Async Agent Execution")
    print("=" * 60)
    
    agent = AsyncAgent(
        name="async_assistant",
        model="ollama/llama3:latest",
        api_base="http://localhost:11434",
    )
    
    try:
        # Single async call
        response = await agent.chat("What is Python?")
        print(f"✓ Async response: {response[:50]}...")
        
        # Parallel execution
        group = AgentGroup([
            AsyncAgent(name="agent1", model="ollama/llama3:latest", api_base="http://localhost:11434"),
            AsyncAgent(name="agent2", model="ollama/llama3:latest", api_base="http://localhost:11434"),
        ])
        
        results = await group.run_parallel("Say hi")
        print(f"✓ Parallel execution: {len(results)} agents responded")
        
    except Exception as e:
        print(f"⚠ Async demo skipped: {e}")


# =============================================================================
# Feature 3: Memory Management
# =============================================================================

def demo_memory():
    """Demonstrate memory management with vector search."""
    print("\n" + "=" * 60)
    print("FEATURE 3: Memory Management")
    print("=" * 60)
    
    memory = MemoryManager()
    
    # Add memories
    memory.add("Python is a programming language created by Guido van Rossum")
    memory.add("Java was developed by James Gosling at Sun Microsystems")
    memory.add("Rust is known for memory safety without garbage collection")
    memory.add("JavaScript runs in web browsers")
    
    print(f"✓ Added {len(memory)} memories")
    
    # Search memories
    results = memory.search("What is Python?", top_k=2)
    
    if results:
        print("✓ Search results for 'What is Python?':")
        for mem, score in results:
            print(f"  - {mem.content[:60]}... (score: {score:.2f})")
    
    # Context building
    context = memory.get_context("programming languages", max_tokens=200)
    print(f"✓ Built context: {len(context)} chars")


# =============================================================================
# Feature 4: Context Management
# =============================================================================

def demo_context():
    """Demonstrate context window management."""
    print("\n" + "=" * 60)
    print("FEATURE 4: Context Management")
    print("=" * 60)
    
    ctx = ContextManager(
        max_tokens=1000,
        system_prompt="You are a helpful coding assistant.",
    )
    
    # Add messages
    ctx.add_message("user", "What is Python?")
    ctx.add_message("assistant", "Python is a programming language...")
    ctx.add_message("user", "Show me an example")
    ctx.add_message("assistant", "Here's a Python example...")
    
    print(f"✓ Added {len(ctx._messages)} messages")
    print(f"✓ Token count: {ctx.get_token_count()}")
    
    # Get messages for LLM
    messages = ctx.get_messages()
    print(f"✓ Total messages (with system): {len(messages)}")
    
    # Auto-summarization when limit reached
    for i in range(100):
        ctx.add_message("user", f"Message {i}")
        ctx.add_message("assistant", f"Response {i}")
    
    print(f"✓ After 100 exchanges: {len(ctx._messages)} messages, {len(ctx._summaries)} summaries")


# =============================================================================
# Feature 5: Complete Agent with All Features
# =============================================================================

def demo_complete_agent():
    """Demonstrate complete agent with all features."""
    print("\n" + "=" * 60)
    print("FEATURE 5: Complete Agent")
    print("=" * 60)
    
    # Create agent with Ollama
    agent = Agent(
        name="complete_agent",
        model="ollama/llama3:latest",
        api_base="http://localhost:11434",
        system_prompt="You are a helpful AI assistant.",
    )
    
    # Add to memory
    agent.add_to_memory("User prefers Python over JavaScript")
    agent.add_to_memory("User is learning machine learning")
    
    print(f"✓ Created agent: {agent.name}")
    print(f"✓ Memory size: {len(agent.memory)}")
    
    # Search memory
    memories = agent.search_memory("What does user prefer?")
    if memories:
        print(f"✓ Memory search: {memories[0][0].content}")
    
    # Run task (requires Ollama running)
    try:
        response = agent.chat("Hello!")
        print(f"✓ Agent response: {response[:50]}...")
        print(f"✓ Conversation history: {len(agent.get_history())} messages")
    except Exception as e:
        print(f"⚠ Agent chat skipped: {e}")


# =============================================================================
# Main
# =============================================================================

def main():
    print("\n" + "=" * 60)
    print("PIRANHA - COMPLETE FEATURE DEMO")
    print("=" * 60)
    
    # Sync demos
    demo_llm_provider()
    demo_memory()
    demo_context()
    demo_complete_agent()
    
    # Async demo
    print("\n" + "=" * 60)
    print("Running async demo...")
    print("=" * 60)
    asyncio.run(demo_async_agent())
    
    print("\n" + "=" * 60)
    print("ALL FEATURES DEMONSTRATED!")
    print("=" * 60)
    print()
    print("To test with real LLM responses:")
    print("1. Start Ollama: ollama run llama3:latest")
    print("2. Run this example again")
    print()


if __name__ == "__main__":
    main()
