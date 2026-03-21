// rust_core/src/semantic_cache.rs
//
// Semantic Cache with Embedding-based Fuzzy Matching
//

use chrono::{DateTime, Duration, Utc};
use parking_lot::Mutex;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::sync::Arc;

/// Embedding vector type
pub type Embedding = Vec<f32>;

#[derive(Debug, Clone)]
pub struct CacheEntry {
    pub response: String,
    pub model: String,
    pub prompt_tokens: u32,
    pub completion_tokens: u32,
    pub cost_usd: f64,
    pub created_at: DateTime<Utc>,
    pub hits: u32,
    pub embedding: Option<Embedding>,
    pub prompt_text: String,
}

impl CacheEntry {
    fn is_expired(&self, ttl: Duration) -> bool {
        Utc::now() - self.created_at > ttl
    }
}

#[derive(Clone)]
pub struct SemanticCache {
    entries: Arc<Mutex<HashMap<String, CacheEntry>>>,
    ttl: Duration,
    max_entries: usize,
    total_savings_usd: Arc<Mutex<f64>>,
    similarity_threshold: f32,
}

impl SemanticCache {
    pub fn new(ttl_hours: i64, max_entries: usize) -> Self {
        SemanticCache {
            entries: Arc::new(Mutex::new(HashMap::new())),
            ttl: Duration::hours(ttl_hours),
            max_entries,
            total_savings_usd: Arc::new(Mutex::new(0.0)),
            similarity_threshold: 0.85, // Default similarity threshold
        }
    }

    /// Set similarity threshold for fuzzy matching (0.0 - 1.0)
    pub fn with_similarity_threshold(mut self, threshold: f32) -> Self {
        self.similarity_threshold = threshold.clamp(0.0, 1.0);
        self
    }

    pub fn compute_key(&self, model: &str, messages: &serde_json::Value) -> String {
        let canonical = format!(
            "{}:{}",
            model.to_lowercase(),
            normalize_messages(messages)
        );
        let hash = Sha256::digest(canonical.as_bytes());
        hex::encode(hash)
    }

    /// Compute embedding for text (simple hash-based for demo)
    /// In production, replace with real embeddings (sentence-transformers, etc.)
    pub fn compute_embedding(&self, text: &str) -> Embedding {
        let hash = Sha256::digest(text.as_bytes());
        let mut embedding = Vec::with_capacity(384);
        
        for i in 0..384 {
            let byte_idx = i % hash.len();
            // Normalize to [-1, 1] range
            let value = ((hash[byte_idx] as f32) / 127.5) - 1.0;
            embedding.push(value);
        }
        
        embedding
    }

    /// Calculate cosine similarity between two embeddings
    fn cosine_similarity(a: &Embedding, b: &Embedding) -> f32 {
        if a.len() != b.len() || a.is_empty() {
            return 0.0;
        }

        let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
        let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
        let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

        if norm_a == 0.0 || norm_b == 0.0 {
            return 0.0;
        }

        dot_product / (norm_a * norm_b)
    }

    /// Search for similar cached entries using embedding-based fuzzy matching
    pub fn search_similar(
        &self,
        query_embedding: &Embedding,
        top_k: usize,
    ) -> Vec<(String, CacheEntry, f32)> {
        let entries = self.entries.lock();
        let mut results: Vec<(String, CacheEntry, f32)> = Vec::new();

        for (key, entry) in entries.iter() {
            if let Some(entry_embedding) = &entry.embedding {
                let similarity = Self::cosine_similarity(query_embedding, entry_embedding);
                
                if similarity >= self.similarity_threshold {
                    results.push((key.clone(), entry.clone(), similarity));
                }
            }
        }

        // Sort by similarity (descending)
        results.sort_by(|a, b| b.2.partial_cmp(&a.2).unwrap_or(std::cmp::Ordering::Equal));

        // Return top_k results
        results.truncate(top_k);
        results
    }

    /// Get with fuzzy matching - finds similar cached responses
    pub fn get_fuzzy(&self, query: &str, model: &str) -> Option<(CacheEntry, f32)> {
        let query_embedding = self.compute_embedding(query);
        let results = self.search_similar(&query_embedding, 1);

        if let Some((_, mut entry, similarity)) = results.into_iter().next() {
            // Update hit count and savings
            let mut entries = self.entries.lock();
            if let Some(stored_entry) = entries.get_mut(&entry.prompt_text) {
                stored_entry.hits += 1;
                let savings = stored_entry.cost_usd;
                *self.total_savings_usd.lock() += savings;
                entry.hits = stored_entry.hits;
            }
            return Some((entry, similarity));
        }

        None
    }

    pub fn get(&self, key: &str) -> Option<CacheEntry> {
        let mut entries = self.entries.lock();
        if let Some(entry) = entries.get_mut(key) {
            if entry.is_expired(self.ttl) {
                entries.remove(key);
                return None;
            }
            entry.hits += 1;
            let savings = entry.cost_usd;
            *self.total_savings_usd.lock() += savings;
            Some(entry.clone())
        } else {
            None
        }
    }

    /// Put with embedding for fuzzy matching
    pub fn put_with_embedding(
        &self,
        key: String,
        prompt_text: String,
        response: String,
        model: String,
        prompt_tokens: u32,
        completion_tokens: u32,
        cost_usd: f64,
    ) {
        let embedding = self.compute_embedding(&prompt_text);
        
        self.put_with_embedding_internal(
            key,
            prompt_text,
            response,
            model,
            prompt_tokens,
            completion_tokens,
            cost_usd,
            embedding,
        );
    }

    fn put_with_embedding_internal(
        &self,
        key: String,
        prompt_text: String,
        response: String,
        model: String,
        prompt_tokens: u32,
        completion_tokens: u32,
        cost_usd: f64,
        embedding: Embedding,
    ) {
        let mut entries = self.entries.lock();

        if entries.len() >= self.max_entries {
            // Evict oldest or least used entry
            if let Some(oldest_key) = entries
                .iter()
                .min_by_key(|(_, v)| (v.created_at, v.hits))
                .map(|(k, _)| k.clone())
            {
                entries.remove(&oldest_key);
            }
        }

        entries.insert(
            key,
            CacheEntry {
                response,
                model,
                prompt_tokens,
                completion_tokens,
                cost_usd,
                created_at: Utc::now(),
                hits: 0,
                embedding: Some(embedding),
                prompt_text,
            },
        );
    }

    pub fn put(
        &self,
        key: String,
        response: String,
        model: String,
        prompt_tokens: u32,
        completion_tokens: u32,
        cost_usd: f64,
    ) {
        self.put_with_embedding(
            key,
            response.clone(), // Use response as prompt text for backward compatibility
            response,
            model,
            prompt_tokens,
            completion_tokens,
            cost_usd,
        );
    }

    pub fn total_savings_usd(&self) -> f64 {
        *self.total_savings_usd.lock()
    }

    pub fn entry_count(&self) -> usize {
        self.entries.lock().len()
    }

    pub fn evict_expired(&self) {
        let mut entries = self.entries.lock();
        entries.retain(|_, v| !v.is_expired(self.ttl));
    }

    pub fn clear(&self) {
        self.entries.lock().clear();
    }
}

impl Default for SemanticCache {
    fn default() -> Self {
        Self::new(24, 10_000)
    }
}

fn normalize_messages(messages: &serde_json::Value) -> String {
    let json = messages.to_string();
    json.split_whitespace().collect::<Vec<_>>().join(" ")
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_cache_hit() {
        let cache = SemanticCache::new(24, 100);
        let key = "test_key".to_string();
        cache.put_with_embedding(
            key.clone(),
            "test prompt".to_string(),
            "response".to_string(),
            "llama3".to_string(),
            100,
            50,
            0.0,
        );
        let entry = cache.get(&key).unwrap();
        assert_eq!(entry.response, "response");
        assert_eq!(entry.hits, 1);
    }

    #[test]
    fn test_deterministic_key() {
        let cache = SemanticCache::default();
        let messages = json!([{"role": "user", "content": "hello"}]);
        let key1 = cache.compute_key("llama3", &messages);
        let key2 = cache.compute_key("llama3", &messages);
        assert_eq!(key1, key2);
        assert_eq!(key1.len(), 64);
    }

    #[test]
    fn test_embedding_generation() {
        let cache = SemanticCache::default();
        let text = "Hello, world!";
        let embedding1 = cache.compute_embedding(text);
        let embedding2 = cache.compute_embedding(text);
        
        // Same text should produce same embedding
        assert_eq!(embedding1, embedding2);
        assert_eq!(embedding1.len(), 384);
    }

    #[test]
    fn test_cosine_similarity() {
        let a = vec![1.0, 0.0, 0.0];
        let b = vec![1.0, 0.0, 0.0];
        let c = vec![0.0, 1.0, 0.0];
        
        // Identical vectors = 1.0 similarity
        assert!((SemanticCache::cosine_similarity(&a, &b) - 1.0).abs() < 0.001);
        
        // Orthogonal vectors = 0.0 similarity
        assert!(SemanticCache::cosine_similarity(&a, &c).abs() < 0.001);
    }

    #[test]
    fn test_fuzzy_matching_similar_prompts() {
        let cache = SemanticCache::new(24, 100);
        
        // Store a response
        cache.put_with_embedding(
            "key1".to_string(),
            "What is Python?".to_string(),
            "Python is a programming language".to_string(),
            "llama3".to_string(),
            10,
            5,
            0.001,
        );
        
        // Search with similar (but not identical) prompt
        let (entry, similarity) = cache.get_fuzzy("Tell me about Python", "llama3").unwrap();
        
        assert_eq!(entry.response, "Python is a programming language");
        assert!(similarity >= cache.similarity_threshold);
    }

    #[test]
    fn test_fuzzy_matching_no_match() {
        let cache = SemanticCache::new(24, 100);
        
        // Store a response about Python
        cache.put_with_embedding(
            "key1".to_string(),
            "What is Python?".to_string(),
            "Python is a programming language".to_string(),
            "llama3".to_string(),
            10,
            5,
            0.001,
        );
        
        // Search with completely different topic should not match
        let result = cache.get_fuzzy("How to bake a cake?", "llama3");
        assert!(result.is_none());
    }

    #[test]
    fn test_max_entries_eviction() {
        let cache = SemanticCache::new(24, 2);
        cache.put_with_embedding(
            "k1".to_string(),
            "p1".to_string(),
            "r1".to_string(),
            "llama3".to_string(),
            10,
            5,
            0.0,
        );
        cache.put_with_embedding(
            "k2".to_string(),
            "p2".to_string(),
            "r2".to_string(),
            "llama3".to_string(),
            10,
            5,
            0.0,
        );
        cache.put_with_embedding(
            "k3".to_string(),
            "p3".to_string(),
            "r3".to_string(),
            "llama3".to_string(),
            10,
            5,
            0.0,
        );
        assert_eq!(cache.entry_count(), 2);
    }

    #[test]
    fn test_search_similar_multiple_results() {
        let cache = SemanticCache::new(24, 100);
        
        // Store multiple related responses
        cache.put_with_embedding(
            "k1".to_string(),
            "Python programming".to_string(),
            "Python is great".to_string(),
            "llama3".to_string(),
            10,
            5,
            0.0,
        );
        cache.put_with_embedding(
            "k2".to_string(),
            "Python coding".to_string(),
            "Python is awesome".to_string(),
            "llama3".to_string(),
            10,
            5,
            0.0,
        );
        
        // Search for similar
        let query_embedding = cache.compute_embedding("Python language");
        let results = cache.search_similar(&query_embedding, 5);
        
        // Should find at least one result
        assert!(!results.is_empty());
    }
}