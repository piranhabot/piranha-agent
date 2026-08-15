"""Tests for real embeddings in piranha_agent.memory.

MemoryManager's EmbeddingModel used to default to a SHA-256 hash-based
"embedding" with no actual semantic meaning - two related-but-differently-
worded texts hashed to unrelated vectors, so "semantic" memory search was
really just near-exact-match search. It now defaults to real embeddings via
a local Ollama instance, falling back to the hash-based approach if Ollama
isn't reachable.
"""

import pytest
from piranha_agent import EmbeddingModel, get_embedding_model, list_supported_providers
from piranha_agent.memory import HashEmbeddingProvider, MemoryManager, OllamaEmbeddingProvider


def _ollama_reachable() -> bool:
    try:
        OllamaEmbeddingProvider().embed("reachability check")
        import requests

        requests.get("http://localhost:11434/api/tags", timeout=2).raise_for_status()
        return True
    except Exception:
        return False


def test_list_supported_providers():
    providers = list_supported_providers()
    assert set(providers) == {"ollama", "sentence-transformers", "openai", "hash"}


def test_default_provider_is_ollama():
    model = EmbeddingModel()
    assert isinstance(model._impl, OllamaEmbeddingProvider)


def test_explicit_hash_provider_still_available():
    model = EmbeddingModel(provider="hash")
    assert isinstance(model._impl, HashEmbeddingProvider)
    embedding = model.embed("some text")
    assert len(embedding) == 384


def test_unknown_provider_raises():
    with pytest.raises(ValueError):
        EmbeddingModel(provider="not-a-real-provider")


def test_get_embedding_model_convenience_function():
    model = get_embedding_model(provider="hash")
    assert isinstance(model, EmbeddingModel)


def test_ollama_provider_falls_back_when_unreachable():
    provider = OllamaEmbeddingProvider(base_url="http://localhost:1")
    embedding = provider.embed("test text")
    assert embedding is not None
    assert len(embedding) == provider.dimension()  # fallback matches real dim, not hardcoded 384


def test_ollama_provider_fallback_respects_custom_dimension():
    provider = OllamaEmbeddingProvider(base_url="http://localhost:1", dim=123)
    embedding = provider.embed("test text")
    assert len(embedding) == 123


@pytest.mark.skipif(not _ollama_reachable(), reason="No reachable Ollama for real-embedding tests")
class TestRealEmbeddingsIntegration:
    def test_related_prompts_have_high_similarity(self):
        import math

        model = EmbeddingModel()
        e1 = model.embed("What is Python?")
        e2 = model.embed("Tell me about Python")

        dot = sum(x * y for x, y in zip(e1, e2))
        norm1 = math.sqrt(sum(x * x for x in e1))
        norm2 = math.sqrt(sum(x * x for x in e2))
        similarity = dot / (norm1 * norm2)

        assert similarity > 0.8

    def test_memory_search_ranks_relevant_content_highest(self):
        memory = MemoryManager()
        memory.add("Python is a programming language")
        memory.add("The weather today is sunny")

        results = memory.search("What is Python?", top_k=2)
        assert results[0][0].content == "Python is a programming language"
