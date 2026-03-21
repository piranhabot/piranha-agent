'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Cloud, Server, Key, Plus, Trash2, RefreshCw, CheckCircle, XCircle, Zap } from 'lucide-react';

const API_BASE = 'http://localhost:8080/api';

interface LLMProvider {
  id: string;
  name: string;
  type: 'local' | 'cloud';
  model: string;
  api_base?: string;
  api_key?: string;
  status: 'active' | 'inactive' | 'error';
  is_default: boolean;
}

export default function LLMProvidersPage() {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newProvider, setNewProvider] = useState<Partial<LLMProvider>>({
    type: 'local',
    status: 'active'
  });

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      const response = await axios.get(`${API_BASE}/llm/providers`);
      setProviders(response.data.providers || getMockProviders());
      setLoading(false);
    } catch (error) {
      console.error('Failed to load providers:', error);
      setProviders(getMockProviders());
      setLoading(false);
    }
  };

  const handleAddProvider = async () => {
    try {
      await axios.post(`${API_BASE}/llm/providers`, newProvider);
      setShowAddModal(false);
      setNewProvider({ type: 'local', status: 'active' });
      loadProviders();
    } catch (error) {
      console.error('Failed to add provider:', error);
    }
  };

  const handleDeleteProvider = async (id: string) => {
    if (!confirm('Delete this provider?')) return;
    
    try {
      await axios.delete(`${API_BASE}/llm/providers/${id}`);
      loadProviders();
    } catch (error) {
      console.error('Failed to delete provider:', error);
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      await axios.put(`${API_BASE}/llm/providers/${id}/default`);
      loadProviders();
    } catch (error) {
      console.error('Failed to set default:', error);
    }
  };

  const handleTestConnection = async (provider: LLMProvider) => {
    try {
      const response = await axios.post(`${API_BASE}/llm/providers/${provider.id}/test`);
      alert(`Connection ${response.data.success ? 'successful' : 'failed'}`);
    } catch (error) {
      alert('Connection failed');
    }
  };

  const stats = {
    total: providers.length,
    local: providers.filter(p => p.type === 'local').length,
    cloud: providers.filter(p => p.type === 'cloud').length,
    active: providers.filter(p => p.status === 'active').length
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Zap className="w-10 h-10" />
            LLM Providers
          </h1>
          <p className="text-piranha-300">
            Manage local and cloud LLM providers in one place
          </p>
        </div>

        {/* Navigation */}
        <div className="mb-6 flex gap-4">
          <a href="/" className="text-piranha-300 hover:text-white transition-colors">
            ← Back to Dashboard
          </a>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Zap}
            title="Total Providers"
            value={stats.total}
            color="blue"
          />
          <StatCard
            icon={Server}
            title="Local LLMs"
            value={stats.local}
            color="green"
          />
          <StatCard
            icon={Cloud}
            title="Cloud LLMs"
            value={stats.cloud}
            color="purple"
          />
          <StatCard
            icon={CheckCircle}
            title="Active"
            value={stats.active}
            color="yellow"
          />
        </div>

        {/* Providers Grid */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">Configured Providers</h2>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-piranha-600 hover:bg-piranha-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Provider
            </button>
          </div>

          {loading ? (
            <p className="text-piranha-400 text-center py-8">Loading providers...</p>
          ) : providers.length === 0 ? (
            <div className="text-center py-12">
              <Cloud className="w-16 h-16 text-piranha-600 mx-auto mb-4" />
              <p className="text-piranha-300 text-lg mb-4">No LLM providers configured</p>
              <p className="text-piranha-400 text-sm">
                Add your first provider to start using LLMs
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {providers.map((provider) => (
                <ProviderCard
                  key={provider.id}
                  provider={provider}
                  onDelete={() => handleDeleteProvider(provider.id)}
                  onSetDefault={() => handleSetDefault(provider.id)}
                  onTest={() => handleTestConnection(provider)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Quick Setup Guide */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mt-8">
          <h2 className="text-xl font-bold text-white mb-4">Quick Setup Guide</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Local LLM */}
            <div className="bg-piranha-900/50 rounded-lg p-4 border border-piranha-700">
              <h3 className="text-green-400 font-bold mb-2 flex items-center gap-2">
                <Server className="w-5 h-5" />
                Local LLM (Ollama)
              </h3>
              <ol className="text-piranha-300 text-sm space-y-2 list-decimal list-inside">
                <li>Install Ollama: <code className="bg-piranha-800 px-2 py-0.5 rounded">ollama.ai</code></li>
                <li>Pull a model: <code className="bg-piranha-800 px-2 py-0.5 rounded">ollama pull llama3:latest</code></li>
                <li>Start Ollama: <code className="bg-piranha-800 px-2 py-0.5 rounded">ollama serve</code></li>
                <li>Add provider in UI (auto-detected)</li>
              </ol>
            </div>

            {/* Cloud LLM */}
            <div className="bg-piranha-900/50 rounded-lg p-4 border border-piranha-700">
              <h3 className="text-purple-400 font-bold mb-2 flex items-center gap-2">
                <Cloud className="w-5 h-5" />
                Cloud LLM Providers
              </h3>
              <ol className="text-piranha-300 text-sm space-y-2 list-decimal list-inside">
                <li>Get API key from provider</li>
                <li>Click "Add Provider"</li>
                <li>Select provider type</li>
                <li>Enter API key</li>
                <li>Test connection</li>
              </ol>
            </div>
          </div>
        </div>
      </div>

      {/* Add Provider Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-piranha-800 border border-piranha-700 rounded-xl p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold text-white mb-4">Add LLM Provider</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-piranha-300 text-sm mb-2">Type</label>
                <div className="flex gap-4">
                  <button
                    onClick={() => setNewProvider({...newProvider, type: 'local'})}
                    className={`flex-1 px-4 py-2 rounded-lg font-semibold transition-colors ${
                      newProvider.type === 'local'
                        ? 'bg-green-600 text-white'
                        : 'bg-piranha-700 text-piranha-300'
                    }`}
                  >
                    <Server className="w-4 h-4 inline mr-2" />
                    Local
                  </button>
                  <button
                    onClick={() => setNewProvider({...newProvider, type: 'cloud'})}
                    className={`flex-1 px-4 py-2 rounded-lg font-semibold transition-colors ${
                      newProvider.type === 'cloud'
                        ? 'bg-purple-600 text-white'
                        : 'bg-piranha-700 text-piranha-300'
                    }`}
                  >
                    <Cloud className="w-4 h-4 inline mr-2" />
                    Cloud
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-piranha-300 text-sm mb-2">Provider Name</label>
                <input
                  type="text"
                  value={newProvider.name || ''}
                  onChange={(e) => setNewProvider({...newProvider, name: e.target.value})}
                  placeholder="e.g., My Ollama, Claude API"
                  className="w-full bg-piranha-900/50 border border-piranha-700 rounded-lg px-4 py-2 text-white placeholder-piranha-500 focus:outline-none focus:border-piranha-500"
                />
              </div>

              <div>
                <label className="block text-piranha-300 text-sm mb-2">Model</label>
                <select
                  value={newProvider.model || ''}
                  onChange={(e) => setNewProvider({...newProvider, model: e.target.value})}
                  className="w-full bg-piranha-900/50 border border-piranha-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-piranha-500"
                >
                  <option value="">Select model</option>
                  {newProvider.type === 'local' ? (
                    <>
                      <option value="ollama/llama3:latest">Llama 3 (Ollama)</option>
                      <option value="ollama/mistral:latest">Mistral (Ollama)</option>
                      <option value="ollama/codellama:latest">Code Llama (Ollama)</option>
                    </>
                  ) : (
                    <>
                      <option value="anthropic/claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                      <option value="openai/gpt-4">GPT-4</option>
                      <option value="openai/gpt-3.5-turbo">GPT-3.5 Turbo</option>
                      <option value="huggingface/meta-llama/Llama-2-70b">Llama 2 70B</option>
                      <option value="openrouter/meta-llama/llama-3-70b-instruct">Llama 3 70B (OpenRouter)</option>
                    </>
                  )}
                </select>
              </div>

              {newProvider.type === 'cloud' && (
                <>
                  <div>
                    <label className="block text-piranha-300 text-sm mb-2">API Base URL</label>
                    <input
                      type="text"
                      value={newProvider.api_base || ''}
                      onChange={(e) => setNewProvider({...newProvider, api_base: e.target.value})}
                      placeholder="https://api.anthropic.com"
                      className="w-full bg-piranha-900/50 border border-piranha-700 rounded-lg px-4 py-2 text-white placeholder-piranha-500 focus:outline-none focus:border-piranha-500"
                    />
                  </div>

                  <div>
                    <label className="block text-piranha-300 text-sm mb-2">
                      <Key className="w-4 h-4 inline mr-1" />
                      API Key
                    </label>
                    <input
                      type="password"
                      value={newProvider.api_key || ''}
                      onChange={(e) => setNewProvider({...newProvider, api_key: e.target.value})}
                      placeholder="sk-..."
                      className="w-full bg-piranha-900/50 border border-piranha-700 rounded-lg px-4 py-2 text-white placeholder-piranha-500 focus:outline-none focus:border-piranha-500"
                    />
                  </div>
                </>
              )}
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 bg-piranha-700 hover:bg-piranha-600 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAddProvider}
                className="flex-1 bg-piranha-600 hover:bg-piranha-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
              >
                Add Provider
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon: Icon, title, value, color }: {
  icon: any;
  title: string;
  value: number | string;
  color: string;
}) {
  const colorClasses = {
    blue: 'bg-blue-500/20 text-blue-400',
    green: 'bg-green-500/20 text-green-400',
    red: 'bg-red-500/20 text-red-400',
    yellow: 'bg-yellow-500/20 text-yellow-400',
    purple: 'bg-purple-500/20 text-purple-400',
  };

  return (
    <div className="bg-piranha-800/50 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      <p className="text-piranha-300 text-sm mb-1">{title}</p>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  );
}

function ProviderCard({ provider, onDelete, onSetDefault, onTest }: {
  provider: LLMProvider;
  onDelete: () => void;
  onSetDefault: () => void;
  onTest: () => void;
}) {
  return (
    <div className={`bg-piranha-900/50 rounded-xl border p-5 ${
      provider.is_default ? 'border-green-700' : 'border-piranha-700'
    }`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {provider.type === 'local' ? (
            <Server className="w-5 h-5 text-green-400" />
          ) : (
            <Cloud className="w-5 h-5 text-purple-400" />
          )}
          <h3 className="text-white font-bold">{provider.name}</h3>
        </div>
        {provider.is_default && (
          <span className="bg-green-600/20 text-green-400 text-xs px-2 py-1 rounded font-semibold">
            DEFAULT
          </span>
        )}
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-piranha-400">Type:</span>
          <span className="text-white capitalize">{provider.type}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-piranha-400">Model:</span>
          <span className="text-white font-mono text-xs">{provider.model}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-piranha-400">Status:</span>
          <span className={`text-xs px-2 py-1 rounded font-semibold ${
            provider.status === 'active'
              ? 'bg-green-600/20 text-green-400'
              : provider.status === 'error'
              ? 'bg-red-600/20 text-red-400'
              : 'bg-piranha-600/20 text-piranha-400'
          }`}>
            {provider.status.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={onTest}
          className="flex-1 bg-piranha-600/20 hover:bg-piranha-600/30 text-piranha-300 px-3 py-2 rounded-lg text-sm font-semibold transition-colors"
        >
          Test
        </button>
        {!provider.is_default && (
          <button
            onClick={onSetDefault}
            className="flex-1 bg-green-600/20 hover:bg-green-600/30 text-green-400 px-3 py-2 rounded-lg text-sm font-semibold transition-colors"
          >
            Set Default
          </button>
        )}
        <button
          onClick={onDelete}
          className="bg-red-600/20 hover:bg-red-600/30 text-red-400 px-3 py-2 rounded-lg transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// Mock data for demo
function getMockProviders(): LLMProvider[] {
  return [
    { id: '1', name: 'Ollama Local', type: 'local', model: 'ollama/llama3:latest', status: 'active', is_default: true },
    { id: '2', name: 'Claude API', type: 'cloud', model: 'anthropic/claude-3-5-sonnet', api_base: 'https://api.anthropic.com', api_key: 'sk-...', status: 'active', is_default: false },
    { id: '3', name: 'OpenAI GPT-4', type: 'cloud', model: 'openai/gpt-4', api_base: 'https://api.openai.com', api_key: 'sk-...', status: 'active', is_default: false },
    { id: '4', name: 'Hugging Face', type: 'cloud', model: 'huggingface/meta-llama/Llama-2-70b', api_base: 'https://api-inference.huggingface.co', api_key: 'hf_...', status: 'inactive', is_default: false },
    { id: '5', name: 'OpenRouter', type: 'cloud', model: 'openrouter/meta-llama/llama-3-70b-instruct', api_base: 'https://openrouter.ai/api', api_key: 'sk-or-...', status: 'active', is_default: false },
  ];
}
