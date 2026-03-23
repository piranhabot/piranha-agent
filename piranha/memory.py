"""Memory and Context Management with Vector Search.

Provides:
- Vector-based semantic memory
- Context window management
- Long-term memory retrieval
- Conversation summarization
"""

from __future__ import annotations

import hashlib
import uuid
import requests
import logging
import sqlite3
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Approximate number of characters per token used for rough token budgeting.
# This is a heuristic and may need adjustment depending on the model/tokenizer.
CHARS_PER_TOKEN_ESTIMATE = 4


@dataclass
class Memory:
    """A single memory item."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    embedding: list[float] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    importance: float = 1.0
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "importance": self.importance,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class VectorStore:
    """Simple in-memory vector store with optional SQLite persistence.
    
    For high-scale production, consider:
    - FAISS / ChromaDB / Qdrant
    """
    
    def __init__(self, persist_path: str | None = None):
        self.vectors: dict[str, list[float]] = {}
        self.items: dict[str, Any] = {}
        self.persist_path = persist_path
        
        if self.persist_path:
            self._init_db()
            self._load_from_disk()
    
    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.persist_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    vector BLOB,
                    item_json TEXT
                )
            """)
            conn.commit()

    def _load_from_disk(self):
        """Load vectors from disk into memory."""
        try:
            with sqlite3.connect(self.persist_path) as conn:
                cursor = conn.execute("SELECT id, vector, item_json FROM vectors")
                for row in cursor:
                    item_id, vector_json, item_json = row
                    self.vectors[item_id] = json.loads(vector_json)
                    self.items[item_id] = json.loads(item_json)
            logger.info(f"Loaded {len(self.vectors)} items from {self.persist_path}")
        except Exception as e:
            logger.error(f"Failed to load from disk: {e}")

    def add(self, item_id: str, vector: list[float], item: Any) -> None:
        """Add item to store and persist to disk."""
        self.vectors[item_id] = vector
        self.items[item_id] = item
        
        if self.persist_path:
            try:
                # Convert item to dict if it has to_dict method
                item_data = item.to_dict() if hasattr(item, 'to_dict') else item
                with sqlite3.connect(self.persist_path) as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO vectors (id, vector, item_json) VALUES (?, ?, ?)",
                        (item_id, json.dumps(vector), json.dumps(item_data))
                    )
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to persist item {item_id}: {e}")
    
    def remove(self, item_id: str) -> None:
        """Remove item from store and disk."""
        self.vectors.pop(item_id, None)
        self.items.pop(item_id, None)
        
        if self.persist_path:
            with sqlite3.connect(self.persist_path) as conn:
                conn.execute("DELETE FROM vectors WHERE id = ?", (item_id,))
                conn.commit()
    
    def get(self, item_id: str) -> Any | None:
        """Get item by ID."""
        return self.items.get(item_id)
    
    def similarity_search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[tuple[Any, float]]:
        """Find most similar items.
        
        Uses cosine similarity.
        """
        if not self.vectors:
            return []
        
        scores = []
        for item_id, vector in self.vectors.items():
            score = self._cosine_similarity(query_vector, vector)
            scores.append((item_id, score))
        
        # Sort by similarity (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        results = []
        for item_id, score in scores[:top_k]:
            results.append((self.items[item_id], score))
        
        return results
    
    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def __len__(self) -> int:
        return len(self.items)


class EmbeddingProvider:
    """Base interface for embedding providers."""
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError
    def dimension(self) -> int:
        raise NotImplementedError


class HashEmbeddingProvider(EmbeddingProvider):
    """Simple hash-based pseudo-embeddings (for development)."""
    def __init__(self, dim: int = 384):
        self._dim = dim
    def embed(self, text: str) -> list[float]:
        hash_bytes = hashlib.sha256(text.encode()).digest()
        vector = []
        for i in range(self._dim):
            byte_idx = i % len(hash_bytes)
            vector.append((hash_bytes[byte_idx] / 127.5) - 1.0)
        return vector
    def dimension(self) -> int:
        return self._dim


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Semantic embeddings using Ollama (e.g., nomic-embed-text)."""
    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
        dim: int | None = None
    ):
        self.model = model
        self.base_url = base_url
        # Default dimension matches nomic-embed-text unless overridden.
        self._dim = dim if dim is not None else 768

    def embed(self, text: str) -> list[float] | None:
        """
        Generate an embedding for the given text using the configured Ollama model.
        This method calls the Ollama `/api/embeddings` endpoint and returns the
        embedding vector from the response. If any error occurs while making the
        request or parsing the response (for example, network issues, timeouts,
        or non-success HTTP status codes), the error is logged and ``None`` is
        returned so that callers can handle the failure explicitly.
        """
        try:
            res = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=30
            )
            res.raise_for_status()
            
            data = res.json()
            embedding = data.get("embedding")
            if not isinstance(embedding, list):
                raise ValueError("Ollama embedding response missing 'embedding' list")
            return embedding
        except Exception as e:
            truncated_text = text[:50] + ("..." if len(text) > 50 else "")
            logger.error(
                "Ollama embedding failed for model '%s' at '%s' with text '%s': %s",
                self.model,
                self.base_url,
                truncated_text,
                e,
            )
            return None
    def dimension(self) -> int:
        return self._dim


class _SentenceTransformerWrapper(EmbeddingProvider):
    """Adapter that wraps a SentenceTransformer instance to match EmbeddingProvider."""
    def __init__(self, model) -> None:
        self._model = model
    def embed(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()
    def dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()


class SentenceTransformerProvider(EmbeddingProvider):
    """Semantic embeddings using local sentence-transformers."""
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self._impl: EmbeddingProvider = _SentenceTransformerWrapper(SentenceTransformer(model))
        except Exception as e:
            logger.error(
                "Failed to initialize SentenceTransformer model '%s': %s. "
                "Falling back to hash-based embeddings.",
                model,
                e,
            )
            # Fallback to a simple hash-based provider to avoid crashing the application.
            self._impl = HashEmbeddingProvider()
            
    def embed(self, text: str) -> list[float]:
        return self._impl.embed(text)
    def dimension(self) -> int:
        return self._impl.dimension()


class EmbeddingModel:
    """Entry point for generating text embeddings.
    
    Supports:
    - hash (default)
    - ollama (nomic-embed-text)
    - sentence-transformers (local)
    - openai (cloud)
    """
    
    def __init__(self, provider: str = "hash", model: str | None = None, **kwargs):
        if provider == "ollama":
            # Allow callers to override the Ollama embedding dimension (default 768).
            dim = kwargs.pop("dim", None)
            self._impl = OllamaEmbeddingProvider(model or "nomic-embed-text", dim=dim, **kwargs)
        elif provider == "sentence-transformers":
            self._impl = SentenceTransformerProvider(model or "all-MiniLM-L6-v2")
        else:
            self._impl = HashEmbeddingProvider(dim=384)
            
    def embed(self, text: str) -> list[float]:
        return self._impl.embed(text)
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]
    
    @property
    def dimension(self) -> int:
        return self._impl.dimension()


class MemoryManager:
    """Manages agent memory with vector search.
    
    Features:
    - Add memories with automatic embedding
    - Semantic search for relevant memories
    - Memory importance scoring
    - Context window management
    
    Example:
        memory = MemoryManager()
        memory.add("Python is a programming language")
        memory.add("Java runs on the JVM")
        
        results = memory.search("What is Python?")
        print(results[0].content)
    """
    
    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
        max_memories: int = 1000,
        persist_path: str | None = None,
    ):
        """Initialize memory manager.
        
        Args:
            embedding_model: Embedding model to use
            max_memories: Maximum memories to retain
            persist_path: Optional path to SQLite file for persistence
        """
        self._embedding_model = embedding_model or EmbeddingModel()
        self._vector_store = VectorStore(persist_path=persist_path)
        self._max_memories = max_memories
        self._memories: dict[str, Memory] = {}
        
        # Rehydrate Memory objects from vector store items
        for item_id, item_data in self._vector_store.items.items():
            if isinstance(item_data, dict):
                memory = Memory(
                    id=item_data.get("id", item_id),
                    content=item_data.get("content", ""),
                    embedding=self._vector_store.vectors.get(item_id),
                    created_at=datetime.fromisoformat(item_data.get("created_at", datetime.now(timezone.utc).isoformat())),
                    access_count=item_data.get("access_count", 0),
                    importance=item_data.get("importance", 1.0),
                    tags=item_data.get("tags", []),
                    metadata=item_data.get("metadata", {}),
                )
                self._memories[item_id] = memory
                # Update vector store items to be the actual Memory object
                self._vector_store.items[item_id] = memory
    
    def add(
        self,
        content: str,
        tags: list[str] | None = None,
        importance: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        """Add a memory.
        
        Args:
            content: Memory content
            tags: Optional tags
            importance: Importance score (0-1)
            metadata: Additional metadata
            
        Returns:
            Created memory
        """
        # Generate embedding
        embedding = self._embedding_model.embed(content)
        
        # Create memory
        memory = Memory(
            content=content,
            embedding=embedding,
            tags=tags or [],
            importance=importance,
            metadata=metadata or {},
        )
        
        # Store
        self._memories[memory.id] = memory
        self._vector_store.add(memory.id, embedding, memory)
        
        # Enforce limit
        self._enforce_limit()
        
        return memory
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[tuple[Memory, float]]:
        """Search for relevant memories.
        
        Args:
            query: Search query
            top_k: Number of results
            min_score: Minimum similarity score
            
        Returns:
            List of (memory, score) tuples
        """
        # Generate query embedding
        query_embedding = self._embedding_model.embed(query)
        
        # Search
        results = self._vector_store.similarity_search(query_embedding, top_k)
        
        # Filter by min_score and update access count
        filtered = []
        for memory, score in results:
            if score >= min_score:
                memory.access_count += 1
                filtered.append((memory, score))
        
        return filtered
    
    def get(self, memory_id: str) -> Memory | None:
        """Get memory by ID."""
        return self._memories.get(memory_id)
    
    def remove(self, memory_id: str) -> bool:
        """Remove a memory."""
        if memory_id in self._memories:
            del self._memories[memory_id]
            self._vector_store.remove(memory_id)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all memories."""
        self._memories.clear()
        self._vector_store = VectorStore()
    
    def _enforce_limit(self) -> None:
        """Remove oldest/least important memories if over limit."""
        while len(self._memories) > self._max_memories:
            # Find least important memory
            eviction_candidate_id = min(
                self._memories.keys(),
                key=lambda x: (
                    self._memories[x].importance,
                    self._memories[x].access_count,
                    self._memories[x].created_at,
                ),
            )
            self.remove(eviction_candidate_id)
    
    def get_context(
        self,
        query: str,
        max_tokens: int = 2000,
    ) -> str:
        """Get relevant context for a query.
        
        Builds context from relevant memories up to a token limit.
        
        Note:
            Token counts are estimated using a simple character-based
            heuristic (approximately 4 characters per token). Actual
            tokenization depends on the model/tokenizer in use (e.g.,
            GPT-style tokenizers) and may differ significantly. This
            method should not be relied on for strict token budgeting.
        """
        results = self.search(query, top_k=10)
        
        context_parts = []
        total_tokens = 0
        
        for memory, _score in results:
            # Approximate token count assuming ~4 characters per token.
            # This is a heuristic and may differ from the true count
            # produced by a specific tokenizer (e.g., GPT-3/4).
            tokens = len(memory.content) // CHARS_PER_TOKEN_ESTIMATE
            
            if total_tokens + tokens > max_tokens:
                break
            
            context_parts.append(memory.content)
            total_tokens += tokens
        
        return "\n\n".join(context_parts)
    
    def __len__(self) -> int:
        return len(self._memories)


class ContextManager:
    """Manages conversation context window.
    
    Features:
    - Automatic context window management
    - Message summarization
    - Important message preservation
    
    Example:
        ctx = ContextManager(max_tokens=4000)
        ctx.add_message("user", "Hello")
        ctx.add_message("assistant", "Hi there!")
        
        messages = ctx.get_messages()
    """
    
    def __init__(
        self,
        max_tokens: int = 4000,
        system_prompt: str = "",
    ):
        """Initialize context manager.
        
        Args:
            max_tokens: Maximum context tokens
            system_prompt: System prompt (always included)
        """
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self._messages: list[dict[str, str]] = []
        self._summaries: list[str] = []
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to context.
        
        Args:
            role: "user" or "assistant"
            content: Message content
        """
        self._messages.append({"role": role, "content": content})
        self._enforce_limit()
    
    def add_system_message(self, content: str) -> None:
        """Add a system message."""
        self._messages.insert(0, {"role": "system", "content": content})
    
    def get_messages(self) -> list[dict[str, str]]:
        """Get all messages for LLM."""
        messages = []
        
        # Add system prompt first
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # Add summaries
        for summary in self._summaries:
            messages.append({"role": "system", "content": f"[Summary]: {summary}"})
        
        # Add messages
        messages.extend(self._messages)
        
        return messages
    
    def get_token_count(self) -> int:
        """Estimate current token count."""
        total = len(self.system_prompt) // CHARS_PER_TOKEN_ESTIMATE
        
        for summary in self._summaries:
            total += len(summary) // CHARS_PER_TOKEN_ESTIMATE
        
        for msg in self._messages:
            total += len(msg["content"]) // CHARS_PER_TOKEN_ESTIMATE
        
        return total
    
    def _enforce_limit(self) -> None:
        """Remove old messages if over token limit."""
        while self.get_token_count() > self.max_tokens and len(self._messages) > 2:
            # Remove oldest message (not system)
            removed = self._messages.pop(0)
            
            # Optionally summarize removed messages
            if len(self._summaries) < 5:  # Limit summaries
                self._summaries.append(f"Previous conversation about: {removed['content'][:100]}...")
    
    def summarize_context(self) -> str:
        """Create a summary of the current context."""
        if not self._messages:
            return ""
        
        # Simple summarization
        # In production, use an LLM for better summaries
        first_msg = self._messages[0]["content"] if self._messages else ""
        last_msg = self._messages[-1]["content"] if self._messages else ""
        
        return f"Conversation from '{first_msg[:50]}...' to '{last_msg[:50]}...'"
    
    def clear(self) -> None:
        """Clear all messages."""
        self._messages = []
        self._summaries = []
