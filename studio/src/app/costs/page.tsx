'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { DollarSign, TrendingUp, BarChart3, Calendar, Download, PieChart } from 'lucide-react';
// import recharts components - reserved for future charts

const API_BASE = 'http://localhost:8080/api';

interface CostData {
  total_cost: number;
  total_tokens: number;
  llm_calls: number;
  cache_hits: number;
  cache_savings: number;
  daily_breakdown: any[];
  agent_breakdown: any[];
  model_breakdown: any[];
  projection: number;
}

export default function CostAnalyticsPage() {
  const [costData, setCostData] = useState<CostData | null>(null);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadCostData();

    if (autoRefresh) {
      const interval = setInterval(loadCostData, 10000);
      return () => clearInterval(interval);
    }
  }, [timeRange, autoRefresh]);

  const loadCostData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/costs/analytics`, {
        params: { range: timeRange }
      });
      setCostData(response.data);
    } catch (error) {
      console.error('Failed to load cost data:', error);
      setCostData(getMockCostData());
    }
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(costData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `cost-analytics-${timeRange}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (!costData) return null;

  const savingsRate = costData.cache_savings > 0 
    ? ((costData.cache_savings / (costData.total_cost + costData.cache_savings)) * 100).toFixed(1)
    : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <DollarSign className="w-10 h-10" />
            Advanced Cost Analytics
          </h1>
          <p className="text-piranha-300">
            Comprehensive cost tracking, trends, and optimization insights
          </p>
        </div>

        {/* Navigation */}
        <div className="mb-6 flex gap-4">
          <a href="/" className="text-piranha-300 hover:text-white transition-colors">
            ← Back to Dashboard
          </a>
        </div>

        {/* Controls */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex gap-2">
              <button
                onClick={() => setTimeRange('7d')}
                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                  timeRange === '7d'
                    ? 'bg-piranha-600 text-white'
                    : 'bg-piranha-700 text-piranha-300'
                }`}
              >
                7 Days
              </button>
              <button
                onClick={() => setTimeRange('30d')}
                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                  timeRange === '30d'
                    ? 'bg-piranha-600 text-white'
                    : 'bg-piranha-700 text-piranha-300'
                }`}
              >
                30 Days
              </button>
              <button
                onClick={() => setTimeRange('90d')}
                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                  timeRange === '90d'
                    ? 'bg-piranha-600 text-white'
                    : 'bg-piranha-700 text-piranha-300'
                }`}
              >
                90 Days
              </button>
            </div>
            
            <div className="flex gap-4">
              <label className="flex items-center gap-2 text-piranha-300">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded bg-piranha-700 border-piranha-600 text-piranha-600"
                />
                Auto-refresh (10s)
              </label>
              <button
                onClick={handleExport}
                className="bg-piranha-600 hover:bg-piranha-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={DollarSign}
            title="Total Cost"
            value={`$${costData.total_cost.toFixed(4)}`}
            subtitle={`Projected: $${costData.projection.toFixed(4)}`}
            color="green"
          />
          <StatCard
            icon={TrendingUp}
            title="Total Tokens"
            value={costData.total_tokens.toLocaleString()}
            subtitle={`${costData.llm_calls} LLM calls`}
            color="blue"
          />
          <StatCard
            icon={PieChart}
            title="Cache Savings"
            value={`$${costData.cache_savings.toFixed(4)}`}
            subtitle={`${savingsRate}% savings rate`}
            color="yellow"
          />
          <StatCard
            icon={BarChart3}
            title="Cache Hits"
            value={costData.cache_hits}
            subtitle="Reduced LLM calls"
            color="purple"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Cost Trend */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Cost Trend
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={costData.daily_breakdown}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                  />
                  <Area type="monotone" dataKey="cost" stroke="#22c55e" fill="#22c55e" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Token Usage */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Daily Token Usage
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={costData.daily_breakdown}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                  />
                  <Bar dataKey="tokens" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Agent Breakdown */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              Cost by Agent
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie
                    data={costData.agent_breakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: $${value.toFixed(4)}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="cost"
                  >
                    {costData.agent_breakdown.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={['#3b82f6', '#22c55e', '#eab308', '#ef4444', '#a855f7'][index % 5]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                  />
                  <Legend />
                </RechartsPie>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Model Breakdown */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              Cost by Model
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie
                    data={costData.model_breakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: $${value.toFixed(4)}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="cost"
                  >
                    {costData.model_breakdown.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={['#3b82f6', '#22c55e', '#eab308', '#ef4444', '#a855f7'][index % 5]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                  />
                  <Legend />
                </RechartsPie>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Optimization Tips */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Optimization Recommendations
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <OptimizationTip
              title="Enable Semantic Cache"
              description="Increase cache hit rate to reduce LLM costs by up to 50%"
              impact="High"
              color="green"
            />
            <OptimizationTip
              title="Use Local LLMs"
              description="Switch to Ollama for non-critical tasks to save cloud costs"
              impact="Medium"
              color="yellow"
            />
            <OptimizationTip
              title="Optimize Prompts"
              description="Reduce token usage by optimizing prompt templates"
              impact="Medium"
              color="blue"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, title, value, subtitle, color }: {
  icon: any;
  title: string;
  value: string | number;
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

function OptimizationTip({ title, description, impact, color }: {
  title: string;
  description: string;
  impact: string;
  color: string;
}) {
  const colorClasses = {
    green: 'border-green-700 bg-green-900/20',
    yellow: 'border-yellow-700 bg-yellow-900/20',
    blue: 'border-blue-700 bg-blue-900/20',
  };

  return (
    <div className={`border rounded-lg p-4 ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-white font-bold">{title}</h3>
        <span className={`text-xs px-2 py-1 rounded font-semibold ${
          impact === 'High' ? 'bg-green-600/20 text-green-400' : 'bg-yellow-600/20 text-yellow-400'
        }`}>
          {impact} Impact
        </span>
      </div>
      <p className="text-piranha-300 text-sm">{description}</p>
    </div>
  );
}

// Mock data for demo
function getMockCostData(): CostData {
  const daily_breakdown = Array.from({ length: 7 }, (_, i) => ({
    date: new Date(Date.now() - (6 - i) * 86400000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    cost: Number(((i + 1) * 0.0017).toFixed(4)),
    tokens: 5000 + (i * 913)
  }));

  return {
    total_cost: 0.0567,
    total_tokens: 125000,
    llm_calls: 450,
    cache_hits: 180,
    cache_savings: 0.0234,
    projection: 0.08,
    daily_breakdown,
    agent_breakdown: [
      { name: 'researcher', cost: 0.0234 },
      { name: 'writer', cost: 0.0189 },
      { name: 'reviewer', cost: 0.0144 }
    ],
    model_breakdown: [
      { name: 'llama3', cost: 0.0 },
      { name: 'claude-3-5-sonnet', cost: 0.0345 },
      { name: 'gpt-4', cost: 0.0222 }
    ]
  };
}
