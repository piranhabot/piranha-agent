'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Filter, Download, RefreshCw, Search, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8080/api';

interface Event {
  id: string;
  sequence: number;
  event_type: string;
  timestamp: string;
  agent_id: string;
  session_id: string;
  payload: any;
}

export default function EventTimelinePage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEvents();

    if (autoRefresh) {
      const interval = setInterval(loadEvents, 3000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE}/events/timeline`);
      
      // Use real events from API
      if (response.data && response.data.events && response.data.events.length > 0) {
        setEvents(response.data.events);
      } else {
        // No events yet - show empty state
        setEvents([]);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to load events:', err);
      setError('Failed to connect to API. Make sure the server is running on port 8080.');
      setEvents([]);
      setLoading(false);
    }
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(events, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `events-timeline-${new Date().toISOString()}.json`;
    link.click();
  };

  const filteredEvents = events.filter(event => {
    const matchesFilter = filter === 'all' || event.event_type === filter;
    const matchesSearch = searchQuery === '' || 
                         event.agent_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         event.event_type.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const eventTypes = Array.from(new Set(events.map(e => e.event_type)));

  const getEventIcon = (eventType: string) => {
    if (eventType.includes('LlmCall')) return <Activity className="w-4 h-4 text-blue-400" />;
    if (eventType.includes('Cache')) return <CheckCircle className="w-4 h-4 text-green-400" />;
    if (eventType.includes('Error') || eventType.includes('Failed')) return <XCircle className="w-4 h-4 text-red-400" />;
    if (eventType.includes('Warning')) return <AlertCircle className="w-4 h-4 text-yellow-400" />;
    return <Activity className="w-4 h-4 text-piranha-400" />;
  };

  const getEventColor = (eventType: string) => {
    if (eventType.includes('LlmCall')) return 'border-blue-700 bg-blue-900/20';
    if (eventType.includes('Cache')) return 'border-green-700 bg-green-900/20';
    if (eventType.includes('Error') || eventType.includes('Failed')) return 'border-red-700 bg-red-900/20';
    if (eventType.includes('Warning')) return 'border-yellow-700 bg-yellow-900/20';
    return 'border-piranha-700 bg-piranha-900/20';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-piranha-900 via-piranha-800 to-piranha-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Activity className="w-10 h-10" />
            Event Timeline
          </h1>
          <p className="text-piranha-300">
            Real-time event stream with filtering and search
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
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex flex-wrap gap-4 flex-1">
              {/* Search */}
              <div className="relative flex-1 min-w-[250px]">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-piranha-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search events..."
                  className="w-full bg-piranha-900/50 border border-piranha-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-piranha-500 focus:outline-none focus:border-piranha-500"
                />
              </div>

              {/* Filter */}
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="bg-piranha-900/50 border border-piranha-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-piranha-500"
              >
                <option value="all">All Events ({events.length})</option>
                {eventTypes.map(type => (
                  <option key={type} value={type}>{type} ({events.filter(e => e.event_type === type).length})</option>
                ))}
              </select>
            </div>

            <div className="flex gap-2">
              <label className="flex items-center gap-2 text-piranha-300">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded bg-piranha-700 border-piranha-600 text-piranha-600"
                />
                Auto-refresh (3s)
              </label>
              <button
                onClick={loadEvents}
                className="text-piranha-300 hover:text-white p-2 hover:bg-piranha-700 rounded transition-colors"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
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

        {/* Timeline */}
        <div className="bg-piranha-800/30 backdrop-blur-sm rounded-xl border border-piranha-700 p-6">
          {loading ? (
            <p className="text-piranha-400 text-center py-8">Loading events...</p>
          ) : error ? (
            <div className="text-center py-8">
              <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
              <p className="text-red-300 mb-4">{error}</p>
              <button
                onClick={loadEvents}
                className="px-6 py-2 bg-piranha-600 hover:bg-piranha-500 text-white rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : filteredEvents.length === 0 ? (
            <p className="text-piranha-400 text-center py-8">No events found</p>
          ) : (
            <div className="space-y-4">
              {filteredEvents.slice(0, 100).map((event, index) => (
                <EventCard
                  key={event.id}
                  event={event}
                  index={index}
                  onClick={() => setSelectedEvent(event)}
                  colorClass={getEventColor(event.event_type)}
                  icon={getEventIcon(event.event_type)}
                />
              ))}
              {filteredEvents.length > 100 && (
                <p className="text-piranha-400 text-center py-4 text-sm">
                  Showing 100 of {filteredEvents.length} events
                </p>
              )}
            </div>
          )}
        </div>

        {/* Event Detail Modal */}
        {selectedEvent && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-piranha-800 border border-piranha-700 rounded-xl p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-white">Event Details</h2>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="text-piranha-400 hover:text-white"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <DetailItem label="Event Type" value={selectedEvent.event_type} />
                  <DetailItem label="Sequence" value={`#${selectedEvent.sequence}`} />
                  <DetailItem label="Agent ID" value={selectedEvent.agent_id} />
                  <DetailItem label="Session ID" value={selectedEvent.session_id} />
                  <DetailItem 
                    label="Timestamp" 
                    value={new Date(selectedEvent.timestamp).toLocaleString()} 
                  />
                </div>

                <div>
                  <h3 className="text-white font-bold mb-2">Payload</h3>
                  <pre className="bg-piranha-950 border border-piranha-700 rounded-lg p-4 text-piranha-300 text-sm overflow-x-auto">
                    {JSON.stringify(selectedEvent.payload, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function EventCard({ event, index, onClick, colorClass, icon }: {
  event: Event;
  index: number;
  onClick: () => void;
  colorClass: string;
  icon: React.ReactNode;
}) {
  return (
    <div
      onClick={onClick}
      className={`border rounded-lg p-4 cursor-pointer hover:border-piranha-500 transition-colors ${colorClass}`}
    >
      <div className="flex items-start gap-3">
        <div className="mt-1">{icon}</div>
        
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className="bg-piranha-600 text-white text-xs font-bold px-2 py-1 rounded">
              #{event.sequence}
            </span>
            <span className="text-white font-semibold">{event.event_type}</span>
            <span className="text-piranha-400 text-xs flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(event.timestamp).toLocaleString()}
            </span>
          </div>
          
          <div className="text-piranha-300 text-sm">
            <div>Agent: <span className="font-mono">{event.agent_id}</span></div>
            <div>Session: <span className="font-mono">{event.session_id}</span></div>
          </div>
        </div>
        
        <div className="text-piranha-400 text-xs">
          Click for details →
        </div>
      </div>

      {/* Empty State */}
      {events.length === 0 && !loading && !error && (
        <div className="text-center py-20">
          <Activity className="w-20 h-20 text-piranha-500 mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-semibold text-white mb-2">No Events Yet</h3>
          <p className="text-piranha-300 mb-4">
            Events will appear here as your agents execute tasks
          </p>
          <button
            onClick={loadEvents}
            className="px-6 py-2 bg-piranha-600 hover:bg-piranha-500 text-white rounded-lg transition-colors"
          >
            Refresh
          </button>
        </div>
      )}
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
