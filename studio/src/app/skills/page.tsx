'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Tool, Download, Trash2, Search, Star, Activity, CheckCircle, XCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8080/api';

interface Skill {
  id: string;
  name: string;
  description: string;
  category: string;
  installed: boolean;
  usage_count: number;
  parameters_schema?: any;
  permissions?: string[];
}

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'installed' | 'available'>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  useEffect(() => {
    loadSkills();
  }, []);

  const loadSkills = async () => {
    try {
      const response = await axios.get(`${API_BASE}/skills`);
      setSkills(response.data.skills || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load skills:', error);
      // Use mock data for demo
      setSkills(getMockSkills());
      setLoading(false);
    }
  };

  const handleInstall = async (skillId: string) => {
    try {
      await axios.post(`${API_BASE}/skills/${skillId}/install`);
      loadSkills();
    } catch (error) {
      console.error('Failed to install skill:', error);
    }
  };

  const handleUninstall = async (skillId: string) => {
    try {
      await axios.delete(`${API_BASE}/skills/${skillId}/uninstall`);
      loadSkills();
    } catch (error) {
      console.error('Failed to uninstall skill:', error);
    }
  };

  const filteredSkills = skills.filter(skill => {
    const matchesSearch = skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         skill.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filter === 'all' || 
                         (filter === 'installed' && skill.installed) ||
                         (filter === 'available' && !skill.installed);
    const matchesCategory = categoryFilter === 'all' || skill.category === categoryFilter;
    
    return matchesSearch && matchesFilter && matchesCategory;
  });

  const categories = Array.from(new Set(skills.map(s => s.category)));
  
  const stats = {
    total: skills.length,
    installed: skills.filter(s => s.installed).length,
    available: skills.filter(s => !s.installed).length,
    totalUsage: skills.reduce((sum, s) => sum + s.usage_count, 0)
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Tool className="w-10 h-10" />
            Skills Marketplace
          </h1>
          <p className="text-piranha-300">
            Browse, install, and manage 46+ Claude Skills
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
            icon={Tool}
            title="Total Skills"
            value={stats.total}
            color="blue"
          />
          <StatCard
            icon={CheckCircle}
            title="Installed"
            value={stats.installed}
            color="green"
          />
          <StatCard
            icon={Download}
            title="Available"
            value={stats.available}
            color="yellow"
          />
          <StatCard
            icon={Activity}
            title="Total Usage"
            value={stats.totalUsage}
            color="purple"
          />
        </div>

        {/* Controls */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6 mb-8">
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex flex-wrap gap-4 flex-1">
              {/* Search */}
              <div className="relative flex-1 min-w-[300px]">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-piranha-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search skills..."
                  className="w-full bg-piranha-900/50 border border-piranha-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-piranha-500 focus:outline-none focus:border-piranha-500"
                />
              </div>

              {/* Filter by Status */}
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
                className="bg-piranha-900/50 border border-piranha-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-piranha-500"
              >
                <option value="all">All Skills</option>
                <option value="installed">Installed</option>
                <option value="available">Available</option>
              </select>

              {/* Filter by Category */}
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-piranha-900/50 border border-piranha-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-piranha-500"
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Skills Grid */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
          {loading ? (
            <p className="text-piranha-400 text-center py-8">Loading skills...</p>
          ) : filteredSkills.length === 0 ? (
            <p className="text-piranha-400 text-center py-8">No skills found</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredSkills.map((skill) => (
                <SkillCard
                  key={skill.id}
                  skill={skill}
                  onInstall={() => handleInstall(skill.id)}
                  onUninstall={() => handleUninstall(skill.id)}
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

function SkillCard({ skill, onInstall, onUninstall }: {
  skill: Skill;
  onInstall: () => void;
  onUninstall: () => void;
}) {
  return (
    <div className={`bg-piranha-900/50 rounded-xl border p-5 hover:border-piranha-500 transition-colors ${
      skill.installed ? 'border-green-700/50' : 'border-piranha-700'
    }`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Tool className="w-5 h-5 text-piranha-400" />
          <h3 className="text-white font-bold text-lg">{skill.name}</h3>
        </div>
        <span className={`text-xs px-2 py-1 rounded font-semibold ${
          skill.installed
            ? 'bg-green-600/20 text-green-400'
            : 'bg-piranha-600/20 text-piranha-400'
        }`}>
          {skill.installed ? 'INSTALLED' : 'AVAILABLE'}
        </span>
      </div>

      <p className="text-piranha-300 text-sm mb-3 line-clamp-2">{skill.description}</p>

      <div className="flex items-center gap-2 mb-3">
        <span className="bg-piranha-700/50 text-piranha-300 text-xs px-2 py-1 rounded">
          {skill.category}
        </span>
        {skill.usage_count > 0 && (
          <span className="text-piranha-400 text-xs flex items-center gap-1">
            <Activity className="w-3 h-3" />
            {skill.usage_count} uses
          </span>
        )}
      </div>

      {skill.permissions && skill.permissions.length > 0 && (
        <div className="mb-4">
          <p className="text-piranha-400 text-xs mb-1">Permissions:</p>
          <div className="flex flex-wrap gap-1">
            {skill.permissions.map((perm, idx) => (
              <span key={idx} className="bg-piranha-800 text-piranha-400 text-xs px-2 py-0.5 rounded">
                {perm}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-2">
        {skill.installed ? (
          <button
            onClick={onUninstall}
            className="flex-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 px-4 py-2 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Uninstall
          </button>
        ) : (
          <button
            onClick={onInstall}
            className="flex-1 bg-piranha-600 hover:bg-piranha-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            Install
          </button>
        )}
      </div>
    </div>
  );
}

// Mock data for demo
function getMockSkills(): Skill[] {
  return [
    { id: '1', name: 'docx', description: 'Create, edit, and analyze Word documents', category: 'Document', installed: true, usage_count: 150, permissions: ['file_write'] },
    { id: '2', name: 'pdf', description: 'Extract text, merge, split PDFs', category: 'Document', installed: true, usage_count: 200, permissions: ['file_read'] },
    { id: '3', name: 'pptx', description: 'Create PowerPoint presentations', category: 'Document', installed: false, usage_count: 0, permissions: ['file_write'] },
    { id: '4', name: 'xlsx', description: 'Excel spreadsheet analysis', category: 'Document', installed: true, usage_count: 180, permissions: ['file_read', 'file_write'] },
    { id: '5', name: 'frontend-design', description: 'React + Tailwind + shadcn/ui designs', category: 'Development', installed: true, usage_count: 320, permissions: [] },
    { id: '6', name: 'mcp-builder', description: 'Build MCP servers for API integration', category: 'Development', installed: false, usage_count: 0, permissions: ['network_write'] },
    { id: '7', name: 'test-driven-development', description: 'TDD methodology implementation', category: 'Development', installed: true, usage_count: 95, permissions: [] },
    { id: '8', name: 'code-review', description: 'Code quality review', category: 'Development', installed: true, usage_count: 210, permissions: [] },
    { id: '9', name: 'deep-research', description: 'Multi-step autonomous research', category: 'Research', installed: false, usage_count: 0, permissions: ['network_read'] },
    { id: '10', name: 'root-cause-tracing', description: 'Error tracing and analysis', category: 'Research', installed: false, usage_count: 0, permissions: [] },
    { id: '11', name: 'canvas-design', description: 'Visual art creation (PNG/PDF)', category: 'Creative', installed: true, usage_count: 75, permissions: ['file_write'] },
    { id: '12', name: 'brand-guidelines', description: 'Apply brand colors/typography', category: 'Creative', installed: false, usage_count: 0, permissions: [] },
    { id: '13', name: 'internal-comms', description: 'Status reports, newsletters', category: 'Communication', installed: true, usage_count: 120, permissions: [] },
    { id: '14', name: 'article-extractor', description: 'Web article extraction', category: 'Communication', installed: false, usage_count: 0, permissions: ['network_read'] },
    { id: '15', name: 'csv-data-summarizer', description: 'CSV analysis and insights', category: 'Data', installed: true, usage_count: 160, permissions: ['file_read'] },
    { id: '16', name: 'postgres', description: 'Safe SQL queries', category: 'Data', installed: false, usage_count: 0, permissions: ['network_read'] },
  ];
}
