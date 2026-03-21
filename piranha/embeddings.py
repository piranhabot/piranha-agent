#!/usr/bin/env python3
"""Real Embeddings Support for Piranha Semantic Cache.

This module adds support for real embedding models:
- sentence-transformers
- OpenAI embeddings
- Ollama embeddings (nomic-embed-text)
- Custom embedding providers

Usage:
    from piranha import SemanticCache, EmbeddingModel
    
    # Use sentence-transformers
    model = EmbeddingModel(provider="sentence-transformers", model="all-MiniLM-L6-v2")
    cache = SemanticCache(embedding_model=model)
    
    # Use Ollama embeddings
    model = EmbeddingModel(provider="ollama", model="nomic-embed-text")
    cache = SemanticCache(embedding_model=model)
"""

from __future__ import annotations

import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        pass
    
    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension."""
        pass


class SentenceTransformersProvider(EmbeddingProvider):
    """sentence-transformers embedding provider."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self._dimension = self.model.get_sentence_embedding_dimension()
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
    
    def embed(self, text: str) -> list[float]:
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    @property
    def dimension(self) -> int:
        return self._dimension


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama embedding provider (nomic-embed-text, mxbai-embed-large)."""
    
    def __init__(self, model_name: str = "nomic-embed-text", api_base: str = "http://localhost:11434"):
        self.model_name = model_name
        self.api_base = api_base
        
        # Get dimension from model
        self._dimension = self._get_dimension()
    
    def _get_dimension(self) -> int:
        """Get embedding dimension for model."""
        try:
            import httpx
            response = httpx.get(f"{self.api_base}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model.get("name", "").startswith(self.model_name):
                        # Ollama embedding models typically have 768 dimensions
                        return 768
        except Exception as e:
            # Log error but return default dimension
            logger.debug(f"Failed to get Ollama model dimension: {e}")
        
        return 768  # Default dimension
    
    def embed(self, text: str) -> list[float]:
        try:
            import httpx
            response = httpx.post(
                f"{self.api_base}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json().get("embedding", [])
        except ImportError:
            raise ImportError("httpx not installed. Install with: pip install httpx")
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]
    
    @property
    def dimension(self) -> int:
        return self._dimension


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embeddings provider (text-embedding-3-small, text-embedding-3-large)."""
    
    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: str | None = None,
        organization: str | None = None
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.organization = organization
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, organization=organization)
            self._dimension = 1536 if "small" in model_name else 3072
        except ImportError:
            raise ImportError("openai not installed. Install with: pip install openai")
    
    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    @property
    def dimension(self) -> int:
        return self._dimension


class HashEmbeddingProvider(EmbeddingProvider):
    """Fallback hash-based embedding provider (deterministic, fast, no dependencies)."""
    
    def __init__(self, dimension: int = 384):
        self._dimension = dimension
    
    def embed(self, text: str) -> list[float]:
        """Generate deterministic pseudo-embedding using SHA-256."""
        hash_bytes = hashlib.sha256(text.encode()).digest()
        vector = []
        for i in range(self._dimension):
            byte_idx = i % len(hash_bytes)
            value = (hash_bytes[byte_idx] / 127.5) - 1.0
            vector.append(value)
        return vector
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]
    
    @property
    def dimension(self) -> int:
        return self._dimension


class EmbeddingModel:
    """Unified embedding model interface for Piranha.
    
    Supports multiple providers:
    - sentence-transformers (local, free)
    - Ollama (local, free)
    - OpenAI (cloud, paid)
    - Hash-based (fallback, no dependencies)
    
    Example:
        # Use sentence-transformers
        model = EmbeddingModel(
            provider="sentence-transformers",
            model="all-MiniLM-L6-v2"
        )
        
        # Use Ollama
        model = EmbeddingModel(
            provider="ollama",
            model="nomic-embed-text"
        )
        
        # Use OpenAI
        model = EmbeddingModel(
            provider="openai",
            model="text-embedding-3-small",
            api_key="sk-..."
        )
        
        # Use hash-based (default fallback)
        model = EmbeddingModel()
    """
    
    def __init__(
        self,
        provider: str = "hash",
        model: str | None = None,
        api_key: str | None = None,
        api_base: str | None = None,
        dimension: int | None = None,
        **kwargs: Any
    ):
        """Initialize embedding model.
        
        Args:
            provider: Provider name (hash, sentence-transformers, ollama, openai)
            model: Model name (depends on provider)
            api_key: API key (for OpenAI)
            api_base: API base URL (for Ollama)
            dimension: Embedding dimension (optional)
            **kwargs: Additional provider-specific arguments
        """
        self.provider = provider
        self._model = model
        self._api_key = api_key
        self._api_base = api_base
        self._provider_instance = self._create_provider(provider, model, api_key, api_base, dimension, **kwargs)
    
    def _create_provider(
        self,
        provider: str,
        model: str | None,
        api_key: str | None,
        api_base: str | None,
        dimension: int | None,
        **kwargs: Any
    ) -> EmbeddingProvider:
        """Create embedding provider instance."""
        if provider == "sentence-transformers":
            model_name = model or "all-MiniLM-L6-v2"
            return SentenceTransformersProvider(model_name)
        
        elif provider == "ollama":
            model_name = model or "nomic-embed-text"
            return OllamaEmbeddingProvider(model_name, api_base or "http://localhost:11434")
        
        elif provider == "openai":
            model_name = model or "text-embedding-3-small"
            return OpenAIEmbeddingProvider(model_name, api_key)
        
        elif provider == "hash":
            return HashEmbeddingProvider(dimension or 384)
        
        else:
            raise ValueError(
                f"Unknown provider: {provider}. "
                "Available: hash, sentence-transformers, ollama, openai"
            )
    
    def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        return self._provider_instance.embed(text)
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        return self._provider_instance.embed_batch(texts)
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._provider_instance.dimension
    
    def __repr__(self) -> str:
        return f"EmbeddingModel(provider={self.provider!r}, dimension={self.dimension})"


# Convenience functions
def get_embedding_model(
    provider: str = "hash",
    **kwargs: Any
) -> EmbeddingModel:
    """Get embedding model for provider.
    
    Args:
        provider: Provider name
        **kwargs: Provider-specific arguments
    
    Returns:
        Configured EmbeddingModel
    """
    return EmbeddingModel(provider=provider, **kwargs)


def list_supported_providers() -> list[str]:
    """List supported embedding providers."""
    return ["hash", "sentence-transformers", "ollama", "openai"]


def get_recommended_model(use_case: str) -> tuple[str, str]:
    """Get recommended provider and model for use case.
    
    Args:
        use_case: Use case (semantic-cache, search, clustering, etc.)
    
    Returns:
        Tuple of (provider, model)
    """
    recommendations = {
        "semantic-cache": ("sentence-transformers", "all-MiniLM-L6-v2"),
        "search": ("sentence-transformers", "all-mpnet-base-v2"),
        "clustering": ("sentence-transformers", "all-MiniLM-L6-v2"),
        "local-fast": ("hash", None),
        "local-best": ("ollama", "nomic-embed-text"),
        "cloud-best": ("openai", "text-embedding-3-large"),
    }
    
    return recommendations.get(use_case, ("sentence-transformers", "all-MiniLM-L6-v2"))


if __name__ == "__main__":
    # Test embedding models
    print("Testing Embedding Models")
    print("=" * 50)
    
    # Hash-based (default)
    print("\n1. Hash-based (fallback):")
    hash_model = EmbeddingModel(provider="hash")
    embedding = hash_model.embed("Hello, world!")
    print(f"   Dimension: {hash_model.dimension}")
    print(f"   Sample: {embedding[:5]}...")
    
    # Try sentence-transformers
    try:
        print("\n2. sentence-transformers:")
        st_model = EmbeddingModel(provider="sentence-transformers")
        embedding = st_model.embed("Hello, world!")
        print(f"   Dimension: {st_model.dimension}")
        print(f"   Sample: {embedding[:5]}...")
    except ImportError as e:
        print(f"   Not available: {e}")
    
    # Try Ollama
    try:
        print("\n3. Ollama embeddings:")
        ollama_model = EmbeddingModel(provider="ollama")
        embedding = ollama_model.embed("Hello, world!")
        print(f"   Dimension: {ollama_model.dimension}")
        print(f"   Sample: {embedding[:5]}...")
    except Exception as e:
        print(f"   Not available: {e}")
    
    # Try OpenAI
    try:
        print("\n4. OpenAI embeddings:")
        openai_model = EmbeddingModel(provider="openai")
        embedding = openai_model.embed("Hello, world!")
        print(f"   Dimension: {openai_model.dimension}")
        print(f"   Sample: {embedding[:5]}...")
    except Exception as e:
        print(f"   Not available: {e}")
    
    print("\n" + "=" * 50)
    print("Embedding models ready!")
