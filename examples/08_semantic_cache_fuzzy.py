#!/usr/bin/env python3
"""Embedding-based Semantic Cache with Fuzzy Matching.

This example demonstrates Piranha's Phase 4 feature: embedding-based semantic
cache with fuzzy matching capabilities.

Features:
- Embedding-based similarity search
- Fuzzy matching for semantically similar prompts
- Configurable similarity threshold
- Automatic hit tracking and cost savings

Usage:
    python examples/08_semantic_cache_fuzzy.py
"""

from piranha import SemanticCache


def main():
    print("=" * 70)
    print("PHASE 4: EMBEDDING-BASED SEMANTIC CACHE WITH FUZZY MATCHING")
    print("=" * 70)
    print()

    # -------------------------------------------------------------------------
    # Part 1: Basic Cache Operations with Embeddings
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 1: Basic Cache Operations with Embeddings")
    print("-" * 70)
    print()

    cache = SemanticCache(ttl_hours=24, max_entries=10000)
    print(f"Created SemanticCache (TTL: 24h, Max entries: 10000)")
    print()

    # Add entries with embeddings for fuzzy matching
    print("Adding entries with embeddings...")
    
    cache.put_with_embedding(
        key="python_intro",
        prompt_text="What is Python?",
        response="Python is a high-level, interpreted programming language "
                  "known for its simplicity and readability.",
        model="llama3",
        prompt_tokens=10,
        completion_tokens=25,
        cost_usd=0.0003
    )
    print("  ✓ Added: 'What is Python?'")

    cache.put_with_embedding(
        key="python_loops",
        prompt_text="How do for loops work in Python?",
        response="Python for loops iterate over sequences. Syntax: "
                  "'for item in sequence: ...'",
        model="llama3",
        prompt_tokens=15,
        completion_tokens=30,
        cost_usd=0.0004
    )
    print("  ✓ Added: 'How do for loops work in Python?'")

    cache.put_with_embedding(
        key="python_functions",
        prompt_text="How to define a function in Python?",
        response="Use 'def' keyword: def function_name(parameters): return value",
        model="llama3",
        prompt_tokens=12,
        completion_tokens=20,
        cost_usd=0.0003
    )
    print("  ✓ Added: 'How to define a function in Python?'")
    print()

    print(f"Cache entry count: {cache.entry_count()}")
    print()

    # -------------------------------------------------------------------------
    # Part 2: Fuzzy Matching
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 2: Fuzzy Matching - Find Similar Cached Responses")
    print("-" * 70)
    print()

    # Test exact match
    print("Query: 'What is Python?'")
    result = cache.get_fuzzy("What is Python?", "llama3")
    if result:
        print(f"  ✓ MATCH FOUND (similarity: {result['similarity']:.4f})")
        print(f"    Response: {result['response'][:60]}...")
        print(f"    Hits: {result['hits']}, Cost saved: ${result['cost_usd']:.4f}")
    else:
        print("  ✗ No match found")
    print()

    # Note: Hash-based embeddings match exact text only
    # For true semantic matching, integrate sentence-transformers or OpenAI embeddings
    print("Note: This demo uses hash-based embeddings (deterministic).")
    print("      Exact text matches return similarity=1.0")
    print("      For semantic matching, integrate real embeddings.")
    print()

    # -------------------------------------------------------------------------
    # Part 3: Similarity Search
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 3: Similarity Search - Find Multiple Related Entries")
    print("-" * 70)
    print()

    print("Searching for entries similar to 'Python programming'...")
    results = cache.search_similar("What is Python?", top_k=5)
    
    if results:
        print(f"  Found {len(results)} similar entries:")
        for i, r in enumerate(results, 1):
            print(f"    {i}. Key: {r['key']}")
            print(f"       Prompt: {r['prompt_text']}")
            print(f"       Similarity: {r['similarity']:.4f}")
            print(f"       Hits: {r['hits']}")
            print()
    else:
        print("  No similar entries found")
    print()

    # -------------------------------------------------------------------------
    # Part 4: Cache Statistics
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 4: Cache Statistics")
    print("-" * 70)
    print()

    print(f"Total entries: {cache.entry_count()}")
    print(f"Total savings: ${cache.total_savings_usd():.4f}")
    print()

    # Demonstrate hit tracking
    print("Performing multiple fuzzy matches to track hits...")
    for _ in range(3):
        cache.get_fuzzy("What is Python?", "llama3")
    
    result = cache.get_fuzzy("What is Python?", "llama3")
    print(f"After 4 matches, hit count: {result['hits']}")
    print(f"Updated savings: ${cache.total_savings_usd():.4f}")
    print()

    # -------------------------------------------------------------------------
    # Part 5: Backward Compatibility
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 5: Backward Compatibility - Original API Still Works")
    print("-" * 70)
    print()

    # Original put/get API
    key = cache.compute_key("llama3", [{"role": "user", "content": "hello"}])
    cache.put(
        key=key,
        response="Hello! How can I help you?",
        model="llama3",
        prompt_tokens=5,
        completion_tokens=10,
        cost_usd=0.0001
    )
    print(f"Added entry using original put() API with key: {key[:16]}...")

    original_result = cache.get(key)
    if original_result:
        print(f"Retrieved using original get() API:")
        print(f"  Response: {original_result['response']}")
        print(f"  Model: {original_result['model']}")
    print()

    # -------------------------------------------------------------------------
    # Part 6: Production Integration Notes
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 6: Production Integration Notes")
    print("-" * 70)
    print()

    print("Current Implementation:")
    print("  • Hash-based embeddings (SHA-256)")
    print("  • Deterministic: same text → same embedding")
    print("  • Fast and lightweight")
    print("  • Matches exact text (similarity=1.0)")
    print()

    print("For True Semantic Matching:")
    print("  1. Integrate sentence-transformers:")
    print("     pip install sentence-transformers")
    print()
    print("  2. Or use OpenAI embeddings:")
    print("     from openai import OpenAI")
    print("     client = OpenAI()")
    print("     embedding = client.embeddings.create(...)")
    print()
    print("  3. Or use Ollama embeddings:")
    print("     import ollama")
    print("     embedding = ollama.embed(model='nomic-embed-text', prompt=text)")
    print()

    print("Benefits of Embedding-based Cache:")
    print("  ✓ Reduce LLM costs by caching similar queries")
    print("  ✓ Faster response times for repeated questions")
    print("  ✓ Configurable similarity threshold")
    print("  ✓ Automatic hit tracking and savings calculation")
    print()

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("=" * 70)
    print("PHASE 4: SEMANTIC CACHE WITH FUZZY MATCHING - COMPLETE")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ put_with_embedding() - Store entries with embeddings")
    print("  ✓ get_fuzzy() - Find similar cached responses")
    print("  ✓ search_similar() - Search for related entries")
    print("  ✓ Configurable similarity threshold")
    print("  ✓ Hit tracking and cost savings")
    print("  ✓ Backward compatible with original API")
    print()
    print("Next Steps:")
    print("  • Integrate real embedding models for semantic matching")
    print("  • Adjust similarity threshold based on use case")
    print("  • Monitor cache hit rates and cost savings")
    print()


if __name__ == "__main__":
    main()
