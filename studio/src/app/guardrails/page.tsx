'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, AlertTriangle, CheckCircle, DollarSign, Clock, Save, RefreshCw, type LucideIcon } from 'lucide-react';

const API_BASE = 'http://localhost:8080/api';

interface GuardrailsConfig {
  token_budget: number;
  max_tokens_per_request: number;
  enable_content_filter: boolean;
  blocked_actions: string[];
  warning_threshold: number;
}

interface GuardrailsStats {
  total_checks: number;
  allowed: number;
  warned: number;
  blocked: number;
  token_usage: number;
  budget_remaining: number;
}

export default function GuardrailsPage() {
  const [config, setConfig] = useState<GuardrailsConfig>({
    token_budget: 100000,
    max_tokens_per_request: 5000,
    enable_content_filter: true,
    blocked_actions: [],
    warning_threshold: 80
  });

  const [stats, setStats] = useState<GuardrailsStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadGuardrailsData();

    if (autoRefresh) {
      const interval = setInterval(loadGuardrailsData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadGuardrailsData = async () => {
    try {
      const [configRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE}/guardrails`),
        axios.get(`${API_BASE}/guardrails/stats`)
      ]);
      
      setConfig(configRes.data);
      setStats(statsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load guardrails data:', error);
      // Use mock data for demo
      setConfig(getMockConfig());
      setStats(getMockStats());
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`${API_BASE}/guardrails`, config);
      alert('Guardrails configuration saved!');
    } catch (error) {
      console.error('Failed to save guardrails:', error);
      alert('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleAction = (action: string) => {
    setConfig(prev => ({
      ...prev,
      blocked_actions: prev.blocked_actions.includes(action)
        ? prev.blocked_actions.filter(a => a !== action)
        : [...prev.blocked_actions, action]
    }));
  };

  const budgetPercentage = stats
    ? ((stats.token_usage / config.token_budget) * 100).toFixed(1)
    : '0';

  const budgetColor =
    stats && parseFloat(budgetPercentage) > config.warning_threshold
      ? 'text-red-400'
      : 'text-green-400';

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Shield className="w-10 h-10" />
            Guardrails Configuration
          </h1>
          <p className="text-piranha-300">
            Configure safety guardrails, token budgets, and permissions
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
            icon={Shield}
            title="Total Checks"
            value={stats?.total_checks || 0}
            color="blue"
          />
          <StatCard
            icon={CheckCircle}
            title="Allowed"
            value={stats?.allowed || 0}
            color="green"
          />
          <StatCard
            icon={AlertTriangle}
            title="Warned"
            value={stats?.warned || 0}
            color="yellow"
          />
          <StatCard
            icon={AlertTriangle}
            title="Blocked"
            value={stats?.blocked || 0}
            color="red"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Token Budget */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Token Budget
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-piranha-300 text-sm mb-2">
                  Total Budget: {config.token_budget.toLocaleString()} tokens
                </label>
                <input
                  type="range"
                  min="10000"
                  max="1000000"
                  step="10000"
                  value={config.token_budget}
                  onChange={(e) => setConfig({...config, token_budget: parseInt(e.target.value)})}
                  className="w-full h-2 bg-piranha-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              {stats && (
                <div className="bg-piranha-900/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-piranha-300 text-sm">Usage</span>
                    <span className={`font-bold ${budgetColor}`}>
                      {budgetPercentage}%
                    </span>
                  </div>
                  <div className="w-full bg-piranha-700 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${
                        parseFloat(budgetPercentage) > config.warning_threshold
                          ? 'bg-red-500'
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${budgetPercentage}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between mt-2 text-xs text-piranha-400">
                    <span>Used: {stats.token_usage.toLocaleString()}</span>
                    <span>Remaining: {stats.budget_remaining.toLocaleString()}</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Request Limits */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Request Limits
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-piranha-300 text-sm mb-2">
                  Max Tokens per Request: {config.max_tokens_per_request.toLocaleString()}
                </label>
                <input
                  type="range"
                  min="1000"
                  max="50000"
                  step="500"
                  value={config.max_tokens_per_request}
                  onChange={(e) => setConfig({...config, max_tokens_per_request: parseInt(e.target.value)})}
                  className="w-full h-2 bg-piranha-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-piranha-300 text-sm mb-2">
                  Warning Threshold: {config.warning_threshold}%
                </label>
                <input
                  type="range"
                  min="50"
                  max="95"
                  step="5"
                  value={config.warning_threshold}
                  onChange={(e) => setConfig({...config, warning_threshold: parseInt(e.target.value)})}
                  className="w-full h-2 bg-piranha-700 rounded-lg appearance-none cursor-pointer"
                />
                <p className="text-piranha-400 text-xs mt-1">
                  Alert when budget usage exceeds this percentage
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Blocked Actions */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Blocked Actions
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {[
              'network_read',
              'network_write',
              'file_read',
              'file_write',
              'code_execution',
              'spawn_sub_agent',
              'external_api',
              'cache_access'
            ].map((action) => (
              <button
                key={action}
                onClick={() => handleToggleAction(action)}
                className={`p-3 rounded-lg border font-semibold transition-colors ${
                  config.blocked_actions.includes(action)
                    ? 'bg-red-600/20 border-red-700 text-red-400'
                    : 'bg-piranha-900/50 border-piranha-700 text-piranha-300 hover:border-piranha-500'
                }`}
              >
                {action.replaceAll('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Content Filter */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white mb-1">Content Filtering</h2>
              <p className="text-piranha-300 text-sm">
                Enable automatic content filtering for unsafe requests
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.enable_content_filter}
                onChange={(e) => setConfig({...config, enable_content_filter: e.target.checked})}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-piranha-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-piranha-600"></div>
            </label>
          </div>
        </div>

        {/* Save Button */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-piranha-300">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded bg-piranha-700 border-piranha-600 text-piranha-600"
                />
                Auto-refresh stats (5s)
              </label>
              <button
                onClick={loadGuardrailsData}
                className="text-piranha-300 hover:text-white flex items-center gap-1"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
            </div>
            
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-piranha-600 hover:bg-piranha-500 disabled:bg-piranha-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
            >
              <Save className="w-5 h-5" />
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, title, value, color }: {
  icon: LucideIcon;
  title: string;
  value: number | string;
  color: string;
}) {
  const colorClasses = {
    blue: 'bg-blue-500/20 text-blue-400',
    green: 'bg-green-500/20 text-green-400',
    red: 'bg-red-500/20 text-red-400',
    yellow: 'bg-yellow-500/20 text-yellow-400',
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

// Mock data for demo
function getMockConfig(): GuardrailsConfig {
  return {
    token_budget: 100000,
    max_tokens_per_request: 5000,
    enable_content_filter: true,
    blocked_actions: ['file_write', 'code_execution'],
    warning_threshold: 80
  };
}

function getMockStats(): GuardrailsStats {
  return {
    total_checks: 1250,
    allowed: 1180,
    warned: 45,
    blocked: 25,
    token_usage: 67500,
    budget_remaining: 32500
  };
}
