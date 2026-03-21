import { useState } from 'react'
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow'
import 'reactflow/dist/style.css'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://localhost:8000/api'

// Event type colors for nodes
const EVENT_COLORS = {
  LlmCall: { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' },
  CacheHit: { bg: '#dcfce7', border: '#22c55e', text: '#166534' },
  SkillInvoked: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
  SkillCompleted: { bg: '#dcfce7', border: '#22c55e', text: '#166534' },
  GuardrailCheck: { bg: '#f3e8ff', border: '#a855f7', text: '#6b21a8' },
  GuardrailBlocked: { bg: '#fee2e2', border: '#ef4444', text: '#991b1b' },
  AgentSpawn: { bg: '#ffe4e6', border: '#fb7185', text: '#9f1239' },
  AgentCompleted: { bg: '#e0e7ff', border: '#6366f1', text: '#3730a3' },
  AgentFailed: { bg: '#fee2e2', border: '#dc2626', text: '#991b1b' },
  BudgetAlert: { bg: '#ffedd5', border: '#f97316', text: '#9a3412' },
}

const getEventStyle = (eventType) => {
  const colors = EVENT_COLORS[eventType] || { bg: '#f1f5f9', border: '#64748b', text: '#334155' }
  return {
    backgroundColor: colors.bg,
    border: `2px solid ${colors.border}`,
    color: colors.text,
    borderRadius: '8px',
    padding: '10px',
    minWidth: '200px',
  }
}

// Custom node component
const EventNode = ({ data }) => {
  const style = getEventStyle(data.event_type)
  return (
    <div style={style}>
      <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
        {data.icon} #{data.sequence} {data.event_type}
      </div>
      <div style={{ fontSize: '12px' }}>
        <div>Agent: {data.agent_id}...</div>
        <div>Tokens: {data.tokens}</div>
        <div>Cost: ${data.cost_usd?.toFixed(6)}</div>
      </div>
    </div>
  )
}

const nodeTypes = {
  eventNode: EventNode,
}

function App() {
  const [sessionId, setSessionId] = useState('')
  const [dbPath, setDbPath] = useState(':memory:')
  const [nodes, setNodes] = useState([])
  const [edges, setEdges] = useState([])
  const [costSummary, setCostSummary] = useState(null)
  const [status, setStatus] = useState('')
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [targetSequence, setTargetSequence] = useState(0)
  const [rollbackResult, setRollbackResult] = useState(null)

  const loadTrace = async () => {
    if (!sessionId) {
      setStatus('✗ Please enter a Session ID')
      return
    }
    
    try {
      setStatus('Loading trace...')
      
      // Load events for React Flow
      const eventsResponse = await axios.get(`${API_BASE}/trace/${sessionId}/events`, {
        params: { db_path: dbPath }
      })
      
      // Position nodes vertically
      const rawNodes = eventsResponse.data.nodes.map((node, index) => ({
        ...node,
        position: { x: 50, y: index * 180 }, // Vertical spacing
        data: {
          ...node.data,
          icon: getEventIcon(node.data.event_type),
        }
      }))
      
      // Create edges connecting nodes in sequence
      const edges = []
      for (let i = 0; i < rawNodes.length - 1; i++) {
        edges.push({
          id: `edge-${i}-${i+1}`,
          source: rawNodes[i].id,
          target: rawNodes[i+1].id,
          type: 'bezier',
          animated: true,
          style: { 
            stroke: '#3b82f6', 
            strokeWidth: 3,
            strokeDasharray: '5,5',
          },
          markerEnd: {
            type: 'arrowclosed',
            color: '#3b82f6',
            width: 20,
            height: 20,
          },
        })
      }
      
      setNodes(rawNodes)
      setEdges(edges)
      
      // Load cost data
      const costResponse = await axios.get(`${API_BASE}/trace/${sessionId}/costs`, {
        params: { db_path: dbPath }
      })
      
      setCostData(costResponse.data.data)
      setCostSummary(costResponse.data.summary)
      
      setStatus(`✓ Loaded ${rawNodes.length} events`)
    } catch (error) {
      if (error.response?.status === 404) {
        setStatus(`✗ No trace found for session: ${sessionId}`)
      } else {
        setStatus(`✗ Error: ${error.message}`)
      }
    }
  }

  const handleRollback = async () => {
    if (!sessionId || !agentId) {
      setStatus('✗ Please enter Session ID and Agent ID')
      return
    }
    
    try {
      setStatus('Rolling back...')
      const response = await axios.post(`${API_BASE}/trace/rollback`, {
        session_id: sessionId,
        agent_id: agentId,
        target_sequence: parseInt(targetSequence),
        db_path: dbPath
      })
      setRollbackResult(response.data)
      setStatus(`✓ ${response.data.status}`)
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message
      setStatus(`✗ Rollback failed: ${errorMsg}`)
    }
  }

  const getEventIcon = (eventType) => {
    const icons = {
      LlmCall: '🤖',
      CacheHit: '💾',
      SkillInvoked: '🛠️',
      SkillCompleted: '✅',
      GuardrailCheck: '🛡️',
      GuardrailBlocked: '🚫',
      AgentSpawn: '👶',
      AgentCompleted: '🏁',
      AgentFailed: '❌',
      BudgetAlert: '⚠️',
    }
    return icons[eventType] || '📝'
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🐍 Piranha Time-Travel Debugger</h1>
        <p>Load agent traces, visualize events, analyze costs, and rollback to previous states</p>
      </header>

      <div className="main-content">
        {/* Left Panel - Controls */}
        <div className="panel control-panel">
          <h3>📥 Load Trace</h3>
          <div className="form-group">
            <label>Session ID</label>
            <input
              type="text"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
              placeholder="550e8400-e29b-41d4-a716-446655440000"
            />
          </div>
          <div className="form-group">
            <label>Database Path</label>
            <input
              type="text"
              value={dbPath}
              onChange={(e) => setDbPath(e.target.value)}
              placeholder=":memory: or /path/to/db.sqlite"
            />
          </div>
          <button onClick={loadTrace} className="btn-primary">Load Trace</button>
          <div className="status">{status}</div>

          <h3>⏪ Rollback</h3>
          <div className="form-group">
            <label>Agent ID</label>
            <input
              type="text"
              value={agentId}
              onChange={(e) => setAgentId(e.target.value)}
              placeholder="660e8400-e29b-41d4-a716-446655440000"
            />
          </div>
          <div className="form-group">
            <label>Target Sequence</label>
            <input
              type="number"
              value={targetSequence}
              onChange={(e) => setTargetSequence(e.target.value)}
              min="0"
            />
          </div>
          <button onClick={handleRollback} className="btn-danger">Rollback</button>
          
          {rollbackResult && (
            <div className="rollback-result">
              <h4>Snapshot:</h4>
              <pre>{JSON.stringify(rollbackResult.snapshot, null, 2)}</pre>
            </div>
          )}
        </div>

        {/* Center Panel - React Flow */}
        <div className="panel flow-panel">
          <h3>📊 Event Timeline</h3>
          <div className="react-flow-container">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
              fitView
              attributionPosition="bottom-left"
            >
              <Background />
              <Controls />
              <MiniMap />
            </ReactFlow>
          </div>
        </div>

        {/* Right Panel - Cost Analysis */}
        <div className="panel cost-panel">
          <h3>💰 Cost Analysis</h3>
          {costSummary ? (
            <div className="cost-summary">
              <div className="stat">
                <span className="stat-label">LLM Calls:</span>
                <span className="stat-value">{costSummary.llm_calls}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Cache Hits:</span>
                <span className="stat-value">{costSummary.cache_hits}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Total Cost:</span>
                <span className="stat-value">${costSummary.total_cost?.toFixed(6)}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Est. Savings:</span>
                <span className="stat-value">${costSummary.estimated_savings?.toFixed(6)}</span>
              </div>
            </div>
          ) : (
            <p className="no-data">No cost data available</p>
          )}

          <h3>Cost Timeline</h3>
          {costData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={costData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="sequence" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="cumulative_cost" stroke="#8884d8" name="Cumulative Cost" />
                <Line type="monotone" dataKey="cost" stroke="#82ca9d" name="Event Cost" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No cost timeline data</p>
          )}

          {selectedEvent && (
            <div className="event-details">
              <h3>🔍 Event Details</h3>
              <pre>{JSON.stringify(selectedEvent, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
