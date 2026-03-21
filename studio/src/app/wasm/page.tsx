'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, CheckCircle, XCircle, Clock, Code, AlertTriangle } from 'lucide-react';

const API_BASE = 'http://localhost:8080/api';

interface WasmExecution {
  id: string;
  type: string;
  timestamp: string;
  data: {
    function_name: string;
    execution_time_ms: number;
    success: boolean;
    output?: string;
    error?: string;
  };
}

export default function WasmPage() {
  const [executions, setExecutions] = useState<WasmExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [filter, setFilter] = useState<'all' | 'success' | 'failed'>('all');

  useEffect(() => {
    loadExecutions();
    
    if (autoRefresh) {
      const interval = setInterval(loadExecutions, 3000); // Refresh every 3 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadExecutions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/wasm`);
      setExecutions(response.data.executions || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load Wasm executions:', error);
      setLoading(false);
    }
  };

  const filteredExecutions = executions.filter(exec => {
    if (filter === 'all') return true;
    if (filter === 'success') return exec.data.success;
    if (filter === 'failed') return !exec.data.success;
    return true;
  });

  const stats = {
    total: executions.length,
    successful: executions.filter(e => e.data.success).length,
    failed: executions.filter(e => !e.data.success).length,
    avgTime: executions.length > 0
      ? Math.round(executions
          .filter(e => e.data.success)
          .reduce((sum, e) => sum + e.data.execution_time_ms, 0) / executions.filter(e => e.data.success).length)
      : 0
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Code className="w-10 h-10" />
            WasmTime Execution Logs
          </h1>
          <p className="text-piranha-300">
            Real-time tracking of WebAssembly sandbox executions
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
            icon={Activity}
            title="Total Executions"
            value={stats.total}
            color="blue"
          />
          <StatCard
            icon={CheckCircle}
            title="Successful"
            value={stats.successful}
            color="green"
          />
          <StatCard
            icon={XCircle}
            title="Failed"
            value={stats.failed}
            color="red"
          />
          <StatCard
            icon={Clock}
            title="Avg Time (ms)"
            value={stats.avgTime}
            color="yellow"
          />
        </div>

        {/* Controls */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="text-xl font-bold text-white">Execution History</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                    filter === 'all'
                      ? 'bg-piranha-600 text-white'
                      : 'bg-piranha-700 text-piranha-300 hover:bg-piranha-600'
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setFilter('success')}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                    filter === 'success'
                      ? 'bg-green-600 text-white'
                      : 'bg-piranha-700 text-piranha-300 hover:bg-piranha-600'
                  }`}
                >
                  Success
                </button>
                <button
                  onClick={() => setFilter('failed')}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                    filter === 'failed'
                      ? 'bg-red-600 text-white'
                      : 'bg-piranha-700 text-piranha-300 hover:bg-piranha-600'
                  }`}
                >
                  Failed
                </button>
              </div>
            </div>
            
            <label className="flex items-center gap-2 text-piranha-300">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded bg-piranha-700 border-piranha-600 text-piranha-600"
              />
              Auto-refresh (3s)
            </label>
          </div>
        </div>

        {/* Execution List */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
          {loading ? (
            <p className="text-piranha-400 text-center py-8">Loading executions...</p>
          ) : filteredExecutions.length === 0 ? (
            <p className="text-piranha-400 text-center py-8">
              {filter === 'all' 
                ? 'No Wasm executions yet' 
                : `No ${filter} executions`}
            </p>
          ) : (
            <div className="space-y-4">
              {filteredExecutions.map((exec, index) => (
                <ExecutionCard
                  key={exec.id}
                  execution={exec}
                  rank={filteredExecutions.length - index}
                />
              ))}
            </div>
          )}
        </div>
      </div>
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

function ExecutionCard({ execution, rank }: { 
  execution: WasmExecution; 
  rank: number;
}) {
  const isSuccess = execution.data.success;
  
  return (
    <div className={`bg-piranha-900/50 rounded-lg border p-4 ${
      isSuccess ? 'border-piranha-700' : 'border-red-700/50'
    }`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1">
          <div className={`mt-1 ${isSuccess ? 'text-green-400' : 'text-red-400'}`}>
            {isSuccess ? <CheckCircle className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="bg-piranha-600 text-white text-xs font-bold px-2 py-1 rounded">
                #{rank}
              </span>
              <span className="text-white font-semibold">
                {execution.data.function_name}
              </span>
              <span className={`text-xs px-2 py-1 rounded font-semibold ${
                isSuccess 
                  ? 'bg-green-600/20 text-green-400' 
                  : 'bg-red-600/20 text-red-400'
              }`}>
                {isSuccess ? 'SUCCESS' : 'FAILED'}
              </span>
            </div>
            
            {execution.data.output && (
              <p className="text-piranha-300 text-sm mb-2 font-mono bg-piranha-950/50 p-2 rounded">
                {execution.data.output}
              </p>
            )}
            
            {execution.data.error && (
              <div className="bg-red-950/50 border border-red-700/50 rounded p-2 mb-2">
                <p className="text-red-400 text-sm font-mono">
                  Error: {execution.data.error}
                </p>
              </div>
            )}
            
            <div className="flex items-center gap-4 text-xs text-piranha-400">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {execution.data.execution_time_ms}ms
              </span>
              <span>
                {new Date(execution.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
