'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Database, Clock, Trash2, Plus } from 'lucide-react';

const API_BASE = 'http://localhost:8080/api';

interface Memory {
  id: string;
  content: string;
  created_at: string;
  access_count: number;
  importance: number;
  tags: string[];
  score?: number;
}

export default function MemoryPage() {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Memory[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [newMemory, setNewMemory] = useState('');
  const [newTags, setNewTags] = useState('');
  const [loading, setLoading] = useState(true);

  // Load memories on mount
  useEffect(() => {
    loadMemories();
    const interval = setInterval(loadMemories, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadMemories = async () => {
    try {
      const response = await axios.get(`${API_BASE}/memory`);
      setMemories(response.data.memories || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load memories:', error);
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    try {
      const response = await axios.post(`${API_BASE}/memory/search`, {
        query: searchQuery,
        top_k: 10
      });
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddMemory = async () => {
    if (!newMemory.trim()) return;

    try {
      await axios.post(`${API_BASE}/memory`, {
        content: newMemory,
        tags: newTags.split(',').map(t => t.trim()).filter(t => t)
      });
      setNewMemory('');
      setNewTags('');
      loadMemories();
    } catch (error) {
      console.error('Failed to add memory:', error);
    }
  };

  const handleDeleteMemory = async (id: string) => {
    try {
      await axios.delete(`${API_BASE}/memory/${id}`);
      loadMemories();
    } catch (error) {
      console.error('Failed to delete memory:', error);
    }
  };

  const handleClearAll = async () => {
    if (!confirm('Clear all memories?')) return;
    
    try {
      await axios.delete(`${API_BASE}/memory/clear`);
      loadMemories();
    } catch (error) {
      console.error('Failed to clear memories:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Database className="w-10 h-10" />
            Memory Search
          </h1>
          <p className="text-piranha-300">
            Semantic search through agent memories with vector embeddings
          </p>
        </div>

        {/* Add Memory Card */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Plus className="w-5 h-5" />
            Add New Memory
          </h2>
          <div className="space-y-4">
            <textarea
              value={newMemory}
              onChange={(e) => setNewMemory(e.target.value)}
              placeholder="Enter memory content..."
              className="w-full bg-piranha-900/50 border border-piranha-700 rounded-lg p-3 text-white placeholder-piranha-500 focus:outline-none focus:border-piranha-500"
              rows={3}
            />
            <div className="flex gap-4">
              <input
                type="text"
                value={newTags}
                onChange={(e) => setNewTags(e.target.value)}
                placeholder="Tags (comma-separated)"
                className="flex-1 bg-piranha-900/50 border border-piranha-700 rounded-lg p-3 text-white placeholder-piranha-500 focus:outline-none focus:border-piranha-500"
              />
              <button
                onClick={handleAddMemory}
                className="bg-piranha-600 hover:bg-piranha-500 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                Add Memory
              </button>
            </div>
          </div>
        </div>

        {/* Search Card */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Search className="w-5 h-5" />
            Semantic Search
          </h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search memories (e.g., 'Python programming')"
              className="flex-1 bg-piranha-900/50 border border-piranha-700 rounded-lg p-3 text-white placeholder-piranha-500 focus:outline-none focus:border-piranha-500"
            />
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="bg-piranha-600 hover:bg-piranha-500 disabled:bg-piranha-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4">
              Search Results ({searchResults.length})
            </h2>
            <div className="space-y-3">
              {searchResults.map((result, index) => (
                <MemoryCard
                  key={result.id}
                  memory={result}
                  rank={index + 1}
                  onDelete={handleDeleteMemory}
                />
              ))}
            </div>
          </div>
        )}

        {/* All Memories */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Database className="w-5 h-5" />
              All Memories ({memories.length})
            </h2>
            <button
              onClick={handleClearAll}
              className="text-red-400 hover:text-red-300 text-sm flex items-center gap-1"
            >
              <Trash2 className="w-4 h-4" />
              Clear All
            </button>
          </div>
          
          {loading ? (
            <p className="text-piranha-400 text-center py-8">Loading memories...</p>
          ) : memories.length === 0 ? (
            <p className="text-piranha-400 text-center py-8">No memories yet</p>
          ) : (
            <div className="space-y-3">
              {memories.map((memory) => (
                <MemoryCard
                  key={memory.id}
                  memory={memory}
                  onDelete={handleDeleteMemory}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MemoryCard({ memory, rank, onDelete }: { 
  memory: Memory; 
  rank?: number;
  onDelete: (id: string) => void;
}) {
  return (
    <div className="bg-piranha-900/50 rounded-lg border border-piranha-700 p-4 hover:border-piranha-500 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {rank && (
              <span className="bg-piranha-600 text-white text-xs font-bold px-2 py-1 rounded">
                #{rank}
              </span>
            )}
            {memory.score !== undefined && (
              <span className="bg-green-600/20 text-green-400 text-xs font-semibold px-2 py-1 rounded">
                {(memory.score * 100).toFixed(1)}% match
              </span>
            )}
            <span className="text-piranha-400 text-xs flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(memory.created_at).toLocaleString()}
            </span>
          </div>
          
          <p className="text-white mb-3">{memory.content}</p>
          
          {memory.tags && memory.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {memory.tags.map((tag, index) => (
                <span
                  key={index}
                  className="bg-piranha-700/50 text-piranha-300 text-xs px-2 py-1 rounded"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
          
          <div className="mt-3 text-xs text-piranha-400">
            Accessed: {memory.access_count} times • Importance: {(memory.importance * 100).toFixed(0)}%
          </div>
        </div>
        
        <button
          onClick={() => onDelete(memory.id)}
          className="text-red-400 hover:text-red-300 p-2 hover:bg-red-500/20 rounded transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
