'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Database, TrendingUp, DollarSign, Clock, Trash2, RefreshCw, Save } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const API_BASE = 'http://localhost:8080/api';

interface CacheStats {
  entry_count: number;
  hit_count: number;
  miss_count: number;
  hit_rate: number;
  total_savings_usd: number;
  ttl_hours: number;
  max_entries: number;
}

interface CacheEntry {
  key: string;
  response: string;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: number;
  hits: number;
  created_at: string;
}

export default function CachePage() {
  const [stats, setStats] = useState<CacheStats | null>(null);
  const [entries, setEntries] = useState<CacheEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadCacheData();
    
    if (autoRefresh) {
      const interval = setInterval(loadCacheData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadCacheData = async () => {
    try {
      const [statsRes, entriesRes] = await Promise.all([
        axios.get(`${API_BASE}/cache/stats`),
        axios.get(`${API_BASE}/cache/entries`)
      ]);
      
      setStats(statsRes.data);
      setEntries(entriesRes.data.entries || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load cache data:', error);
      // Use mock data for demo
      setStats(getMockStats());
      setEntries(getMockEntries());
      setLoading(false);
    }
  };

  const handleClearCache = async () => {
    if (!confirm('Clear all cache entries?')) return;
    
    try {
      await axios.delete(`${API_BASE}/cache/clear`);
      loadCacheData();
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  };

  const hitRateData = stats ? [
    { name: 'Hits', value: stats.hit_count, color: '#22c55e' },
    { name: 'Misses', value: stats.miss_count, color: '#ef4444' }
  ] : [];

  const savingsData = stats ? [
    { name: 'Savings', value: parseFloat(stats.total_savings_usd.toFixed(4)), color: '#22c55e' },
    { name: 'Spent', value: 0.05, color: '#3b82f6' } // Mock spent
  ] : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Database className="w-10 h-10" />
            Semantic Cache Dashboard
          </h1>
          <p className="text-piranha-300">
            Monitor cache performance, hit rates, and cost savings
          </p>
        </div>

        {/* Navigation */}
        <div className="mb-6 flex gap-4">
          <a href="/" className="text-piranha-300 hover:text-white transition-colors">
            ← Back to Dashboard
          </a>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Database}
            title="Cache Entries"
            value={stats?.entry_count || 0}
            subtitle={`Max: ${stats?.max_entries || 10000}`}
            color="blue"
          />
          <StatCard
            icon={TrendingUp}
            title="Hit Rate"
            value={stats ? `${((stats.hit_count / (stats.hit_count + stats.miss_count)) * 100).toFixed(1)}%` : '0%'}
            subtitle={`${stats?.hit_count || 0} hits / ${stats?.miss_count || 0} misses`}
            color="green"
          />
          <StatCard
            icon={DollarSign}
            title="Total Savings"
            value={stats ? `$${stats.total_savings_usd.toFixed(4)}` : '$0.0000'}
            subtitle="From cache hits"
            color="yellow"
          />
          <StatCard
            icon={Clock}
            title="TTL"
            value={`${stats?.ttl_hours || 24}h`}
            subtitle="Time to live"
            color="purple"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Hit Rate Pie Chart */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Cache Hit Rate
            </h2>
            <div className="h-64">
              {hitRateData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={hitRateData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {hitRateData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-piranha-400 text-center py-8">No cache data yet</p>
              )}
            </div>
          </div>

          {/* Savings Chart */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Cost Savings
            </h2>
            <div className="h-64">
              {savingsData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={savingsData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                    />
                    <Bar dataKey="value" fill="#22c55e" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-piranha-400 text-center py-8">No savings data yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Save className="w-5 h-5" />
              Cache Entries ({entries.length})
            </h2>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 text-piranha-300">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded bg-piranha-700 border-piranha-600 text-piranha-600"
                />
                Auto-refresh (5s)
              </label>
              <button
                onClick={loadCacheData}
                className="text-piranha-300 hover:text-white flex items-center gap-1"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <button
                onClick={handleClearCache}
                className="text-red-400 hover:text-red-300 flex items-center gap-1"
              >
                <Trash2 className="w-4 h-4" />
                Clear Cache
              </button>
            </div>
          </div>
        </div>

        {/* Cache Entries Table */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
          {loading ? (
            <p className="text-piranha-400 text-center py-8">Loading cache entries...</p>
          ) : entries.length === 0 ? (
            <p className="text-piranha-400 text-center py-8">No cache entries</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-piranha-700">
                    <th className="text-left text-piranha-300 font-semibold py-3 px-4">Key</th>
                    <th className="text-left text-piranha-300 font-semibold py-3 px-4">Model</th>
                    <th className="text-left text-piranha-300 font-semibold py-3 px-4">Tokens</th>
                    <th className="text-left text-piranha-300 font-semibold py-3 px-4">Hits</th>
                    <th className="text-left text-piranha-300 font-semibold py-3 px-4">Cost</th>
                    <th className="text-left text-piranha-300 font-semibold py-3 px-4">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.slice(0, 20).map((entry, index) => (
                    <tr key={index} className="border-b border-piranha-800 hover:bg-piranha-800/30">
                      <td className="py-3 px-4 text-white font-mono text-sm truncate max-w-xs">
                        {entry.key.substring(0, 20)}...
                      </td>
                      <td className="py-3 px-4 text-piranha-300">{entry.model}</td>
                      <td className="py-3 px-4 text-piranha-300">
                        {entry.prompt_tokens} / {entry.completion_tokens}
                      </td>
                      <td className="py-3 px-4">
                        <span className="bg-green-600/20 text-green-400 text-xs px-2 py-1 rounded font-semibold">
                          {entry.hits}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-green-400 font-semibold">
                        ${entry.cost_usd.toFixed(4)}
                      </td>
                      <td className="py-3 px-4 text-piranha-400 text-sm">
                        {new Date(entry.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {entries.length > 20 && (
                <p className="text-piranha-400 text-center py-4 text-sm">
                  Showing 20 of {entries.length} entries
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, title, value, subtitle, color }: {
  icon: any;
  title: string;
  value: number | string;
  subtitle?: string;
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
      {subtitle && <p className="text-piranha-400 text-xs mt-2">{subtitle}</p>}
    </div>
  );
}

// Mock data for demo
function getMockStats(): CacheStats {
  return {
    entry_count: 156,
    hit_count: 423,
    miss_count: 89,
    hit_rate: 0.826,
    total_savings_usd: 2.4567,
    ttl_hours: 24,
    max_entries: 10000
  };
}

function getMockEntries(): CacheEntry[] {
  return Array.from({ length: 50 }, (_, i) => ({
    key: `cache-key-${i}-${Math.random().toString(36).substring(7)}`,
    response: `Cached response ${i}`,
    model: 'llama3',
    prompt_tokens: Math.floor(Math.random() * 100) + 10,
    completion_tokens: Math.floor(Math.random() * 50) + 5,
    cost_usd: Math.random() * 0.001,
    hits: Math.floor(Math.random() * 20),
    created_at: new Date(Date.now() - Math.random() * 86400000).toISOString()
  }));
}
