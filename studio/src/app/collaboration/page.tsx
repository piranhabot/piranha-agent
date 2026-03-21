'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, MessageSquare, GitBranch, Clock, Play, CheckCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8080/api';

interface Collaboration {
  id: string;
  task_id: string;
  description: string;
  status: string;
  agents: Array<{
    id: string;
    name: string;
    role: string;
    status: string;
    messages_sent: number;
  }>;
  conversation: Array<{
    sender: string;
    content: string;
    role: string;
    timestamp: string;
  }>;
  created_at: string;
  completed_at?: string;
}

export default function CollaborationPage() {
  const [collaborations, setCollaborations] = useState<Collaboration[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCollab, setSelectedCollab] = useState<Collaboration | null>(null);

  useEffect(() => {
    loadCollaborations();
  }, []);

  const loadCollaborations = async () => {
    try {
      const response = await axios.get(`${API_BASE}/collaborations`);
      setCollaborations(response.data.collaborations || getMockCollaborations());
      setLoading(false);
    } catch (error) {
      console.error('Failed to load collaborations:', error);
      setCollaborations(getMockCollaborations());
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Users className="w-10 h-10" />
            Multi-Agent Collaboration
          </h1>
          <p className="text-piranha-300">
            View and manage multi-agent collaboration sessions
          </p>
        </div>

        {/* Navigation */}
        <div className="mb-6 flex gap-4">
          <a href="/" className="text-piranha-300 hover:text-white transition-colors">
            ← Back to Dashboard
          </a>
        </div>

        {/* Collaborations List */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
          {loading ? (
            <p className="text-piranha-400 text-center py-8">Loading collaborations...</p>
          ) : collaborations.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-16 h-16 text-piranha-600 mx-auto mb-4" />
              <p className="text-piranha-300 text-lg mb-4">No collaboration sessions</p>
              <p className="text-piranha-400 text-sm">
                Create a multi-agent task to see collaboration here
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {collaborations.map((collab) => (
                <CollaborationCard
                  key={collab.id}
                  collaboration={collab}
                  onClick={() => setSelectedCollab(collab)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Collaboration Detail Modal */}
        {selectedCollab && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-piranha-800 border border-piranha-700 rounded-xl p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-white">Collaboration Details</h2>
                <button
                  onClick={() => setSelectedCollab(null)}
                  className="text-piranha-400 hover:text-white"
                >
                  ✕
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Agents */}
                <div>
                  <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Participating Agents
                  </h3>
                  <div className="space-y-3">
                    {selectedCollab.agents.map((agent, index) => (
                      <div key={index} className="bg-piranha-900/50 border border-piranha-700 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <p className="text-white font-semibold">{agent.name}</p>
                            <p className="text-piranha-400 text-sm">{agent.role}</p>
                          </div>
                          <span className={`text-xs px-2 py-1 rounded font-semibold ${
                            agent.status === 'idle'
                              ? 'bg-green-600/20 text-green-400'
                              : 'bg-blue-600/20 text-blue-400'
                          }`}>
                            {agent.status.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-piranha-400 text-xs">
                          Messages: {agent.messages_sent}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Conversation */}
                <div>
                  <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5" />
                    Conversation History
                  </h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {selectedCollab.conversation.map((msg, index) => (
                      <div key={index} className="bg-piranha-900/50 border border-piranha-700 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-white font-semibold text-sm">{msg.sender}</span>
                          <span className="text-piranha-400 text-xs">({msg.role})</span>
                          <span className="text-piranha-500 text-xs ml-auto">
                            {new Date(msg.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-piranha-300 text-sm">{msg.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Task Info */}
              <div className="mt-6 pt-6 border-t border-piranha-700">
                <div className="grid grid-cols-2 gap-4">
                  <DetailItem label="Task ID" value={selectedCollab.task_id} />
                  <DetailItem label="Status" value={selectedCollab.status} />
                  <DetailItem label="Created" value={new Date(selectedCollab.created_at).toLocaleString()} />
                  {selectedCollab.completed_at && (
                    <DetailItem label="Completed" value={new Date(selectedCollab.completed_at).toLocaleString()} />
                  )}
                </div>
                <div className="mt-4">
                  <p className="text-piranha-400 text-sm mb-1">Description</p>
                  <p className="text-white">{selectedCollab.description}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function CollaborationCard({ collaboration, onClick }: {
  collaboration: Collaboration;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className="bg-piranha-900/50 border border-piranha-700 rounded-xl p-5 cursor-pointer hover:border-piranha-500 transition-colors"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {collaboration.status === 'completed' ? (
            <CheckCircle className="w-6 h-6 text-green-400" />
          ) : (
            <Play className="w-6 h-6 text-blue-400" />
          )}
          <div>
            <h3 className="text-white font-bold text-lg">{collaboration.description}</h3>
            <p className="text-piranha-400 text-sm">Task: {collaboration.task_id}</p>
          </div>
        </div>
        <span className={`text-xs px-3 py-1 rounded font-semibold ${
          collaboration.status === 'completed'
            ? 'bg-green-600/20 text-green-400'
            : 'bg-blue-600/20 text-blue-400'
        }`}>
          {collaboration.status.toUpperCase()}
        </span>
      </div>

      <div className="flex items-center gap-6 text-sm text-piranha-300">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4" />
          <span>{collaboration.agents.length} agents</span>
        </div>
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4" />
          <span>{collaboration.conversation.length} messages</span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4" />
          <span>{new Date(collaboration.created_at).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-piranha-400 text-sm mb-1">{label}</p>
      <p className="text-white font-mono text-sm">{value}</p>
    </div>
  );
}

// Mock data for demo
function getMockCollaborations(): Collaboration[] {
  return [
    {
      id: 'collab-1',
      task_id: 'task-1',
      description: 'Write article about AI',
      status: 'completed',
      agents: [
        { id: '1', name: 'researcher', role: 'researcher', status: 'idle', messages_sent: 5 },
        { id: '2', name: 'writer', role: 'writer', status: 'idle', messages_sent: 3 },
        { id: '3', name: 'reviewer', role: 'reviewer', status: 'idle', messages_sent: 2 }
      ],
      conversation: [
        { sender: 'system', content: 'Please execute: Write article about AI', role: 'system', timestamp: new Date().toISOString() },
        { sender: 'researcher', content: '[researcher] Completed: Research phase', role: 'researcher', timestamp: new Date().toISOString() },
        { sender: 'writer', content: '[writer] Completed: Writing phase', role: 'writer', timestamp: new Date().toISOString() },
        { sender: 'reviewer', content: '[reviewer] Completed: Review phase', role: 'reviewer', timestamp: new Date().toISOString() }
      ],
      created_at: new Date(Date.now() - 3600000).toISOString(),
      completed_at: new Date().toISOString()
    },
    {
      id: 'collab-2',
      task_id: 'task-2',
      description: 'Build web scraper',
      status: 'running',
      agents: [
        { id: '4', name: 'coder', role: 'coder', status: 'busy', messages_sent: 2 },
        { id: '5', name: 'tester', role: 'tester', status: 'idle', messages_sent: 0 }
      ],
      conversation: [
        { sender: 'system', content: 'Please execute: Build web scraper', role: 'system', timestamp: new Date().toISOString() },
        { sender: 'coder', content: '[coder] Starting implementation', role: 'coder', timestamp: new Date().toISOString() }
      ],
      created_at: new Date().toISOString()
    }
  ];
}
