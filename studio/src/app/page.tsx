'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Users, FileText, DollarSign, Zap, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const API_BASE = 'http://localhost:8080/api';

interface Agent {
  id: string;
  name: string;
  model: string;
  status: 'idle' | 'busy' | 'offline';
  tokens_used: number;
  cost_usd: number;
  tasks_completed: number;
  last_active: string;
}

interface Task {
  id: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  agent_id: string | null;
  created_at: string;
  completed_at: string | null;
  tokens_used: number;
  cost_usd: number;
}

interface Metrics {
  active_agents: number;
  idle_agents: number;
  busy_agents: number;
  pending_tasks: number;
  running_tasks: number;
  total_tokens: number;
  total_cost_usd: number;
  uptime_seconds: number;
}

export default function Dashboard() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const [agentsRes, tasksRes, metricsRes] = await Promise.all([
        axios.get(`${API_BASE}/agents`),
        axios.get(`${API_BASE}/tasks`),
        axios.get(`${API_BASE}/metrics`),
      ]);

      setAgents(agentsRes.data.agents);
      setTasks(tasksRes.data.tasks);
      setMetrics(metricsRes.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to connect to Piranha Studio server');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-piranha-900 to-piranha-700">
        <div className="text-white text-center">
          <Activity className="w-16 h-16 mx-auto mb-4 animate-pulse" />
          <h1 className="text-2xl font-bold">Loading Piranha Studio...</h1>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-piranha-900 to-piranha-700">
        <div className="text-white text-center bg-red-500/20 p-8 rounded-lg">
          <AlertCircle className="w-16 h-16 mx-auto mb-4" />
          <h1 className="text-2xl font-bold">Error</h1>
          <p>{error}</p>
          <p className="mt-4 text-sm">Make sure Piranha Studio server is running on port 8080</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900">
      {/* Header */}
      <header className="bg-piranha-900/50 backdrop-blur-sm border-b border-piranha-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                🐟 Piranha Studio
              </h1>
              <p className="text-piranha-300 mt-1">Real-Time Agent Monitoring</p>
            </div>
            <div className="flex items-center gap-6">
              <nav className="flex gap-4 flex-wrap">
                <a href="/" className="text-piranha-300 hover:text-white transition-colors">
                  Dashboard
                </a>
                <a href="/memory" className="text-piranha-300 hover:text-white transition-colors">
                  Memory Search
                </a>
                <a href="/wasm" className="text-piranha-300 hover:text-white transition-colors">
                  Wasm Logs
                </a>
                <a href="/skills" className="text-piranha-300 hover:text-white transition-colors">
                  Skills
                </a>
                <a href="/cache" className="text-piranha-300 hover:text-white transition-colors">
                  Cache
                </a>
                <a href="/guardrails" className="text-piranha-300 hover:text-white transition-colors">
                  Guardrails
                </a>
                <a href="/llm-providers" className="text-piranha-300 hover:text-white transition-colors">
                  LLM Providers
                </a>
              </nav>
              <div className="h-10 w-px bg-piranha-700"></div>
              <div className="text-right">
                <p className="text-piranha-300 text-sm">Uptime</p>
                <p className="text-white font-mono">
                  {metrics ? formatUptime(metrics.uptime_seconds) : '--:--:--'}
                </p>
              </div>
              <div className="h-10 w-px bg-piranha-700"></div>
              <div className="text-right">
                <p className="text-piranha-300 text-sm">Status</p>
                <p className="text-green-400 font-semibold">● Online</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            icon={Users}
            title="Active Agents"
            value={metrics?.active_agents || 0}
            subtitle={`${metrics?.idle_agents || 0} idle, ${metrics?.busy_agents || 0} busy`}
            color="blue"
          />
          <MetricCard
            icon={FileText}
            title="Tasks"
            value={(tasks?.length || 0)}
            subtitle={`${metrics?.pending_tasks || 0} pending, ${metrics?.running_tasks || 0} running`}
            color="purple"
          />
          <MetricCard
            icon={Zap}
            title="Tokens Used"
            value={formatNumber(metrics?.total_tokens || 0)}
            subtitle="Total tokens"
            color="yellow"
          />
          <MetricCard
            icon={DollarSign}
            title="Total Cost"
            value={`$${(metrics?.total_cost_usd || 0).toFixed(4)}`}
            subtitle="USD"
            color="green"
          />
        </div>

        {/* Agents and Tasks */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Agents List */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Agents
            </h2>
            <div className="space-y-3">
              {agents.length === 0 ? (
                <p className="text-piranha-400 text-center py-8">No agents registered</p>
              ) : (
                agents.map((agent) => (
                  <AgentCard key={agent.id} agent={agent} />
                ))
              )}
            </div>
          </div>

          {/* Tasks List */}
          <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Recent Tasks
            </h2>
            <div className="space-y-3">
              {tasks.length === 0 ? (
                <p className="text-piranha-400 text-center py-8">No tasks</p>
              ) : (
                tasks.slice(-10).reverse().map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))
              )}
            </div>
          </div>
        </div>

        {/* Cost Chart */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            Cost Overview
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={agents.map(a => ({ name: a.name, cost: a.cost_usd }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                />
                <Bar dataKey="cost" fill="#0EA5E9" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-piranha-700 mt-8">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-piranha-400">
          <p>Piranha Studio v0.4.0 - Real-Time Agent Monitoring</p>
        </div>
      </footer>
    </div>
  );
}

function MetricCard({ icon: Icon, title, value, subtitle, color }: {
  icon: any;
  title: string;
  value: string | number;
  subtitle: string;
  color: string;
}) {
  const colorClasses = {
    blue: 'bg-blue-500/20 text-blue-400',
    purple: 'bg-purple-500/20 text-purple-400',
    yellow: 'bg-yellow-500/20 text-yellow-400',
    green: 'bg-green-500/20 text-green-400',
  };

  return (
    <div className="bg-piranha-800/50 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      <p className="text-piranha-300 text-sm mb-1">{title}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-piranha-400 text-xs mt-2">{subtitle}</p>
    </div>
  );
}

function AgentCard({ agent }: { agent: Agent }) {
  const statusColors = {
    idle: 'bg-green-500',
    busy: 'bg-yellow-500',
    offline: 'bg-red-500',
  };

  return (
    <div className="bg-piranha-900/50 rounded-lg border border-piranha-700 p-4 hover:border-piranha-500 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${statusColors[agent.status]}`}></div>
          <div>
            <p className="text-white font-semibold">{agent.name}</p>
            <p className="text-piranha-400 text-sm">{agent.model}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-piranha-300 text-sm">${agent.cost_usd.toFixed(4)}</p>
          <p className="text-piranha-400 text-xs">{agent.tokens_used} tokens</p>
        </div>
      </div>
    </div>
  );
}

function TaskCard({ task }: { task: Task }) {
  const statusColors = {
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500',
    running: 'bg-blue-500/20 text-blue-400 border-blue-500',
    completed: 'bg-green-500/20 text-green-400 border-green-500',
    failed: 'bg-red-500/20 text-red-400 border-red-500',
  };

  return (
    <div className="bg-piranha-900/50 rounded-lg border border-piranha-700 p-4">
      <div className="flex items-center justify-between mb-2">
        <p className="text-white text-sm truncate flex-1">{task.description}</p>
        <span className={`px-2 py-1 rounded text-xs border ${statusColors[task.status]}`}>
          {task.status}
        </span>
      </div>
      <div className="flex items-center gap-4 text-xs text-piranha-400">
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {new Date(task.created_at).toLocaleTimeString()}
        </span>
        {task.tokens_used > 0 && (
          <span>{task.tokens_used} tokens</span>
        )}
        {task.cost_usd > 0 && (
          <span>${task.cost_usd.toFixed(4)}</span>
        )}
      </div>
    </div>
  );
}

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
}

function formatUptime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}
