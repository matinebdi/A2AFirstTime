import { useState, useEffect } from 'react'
import axios from 'axios'
import { Activity, Cpu, RefreshCw, Send, CheckCircle, XCircle } from 'lucide-react'
import AgentCard from './components/AgentCard'
import TaskPanel from './components/TaskPanel'
import ResponsePanel from './components/ResponsePanel'

const AGENTS = [
  { name: 'orchestrator', port: 8000, icon: Activity, color: '#10b981' },
  { name: 'decision', port: 8001, icon: Cpu, color: '#3b82f6' },
  { name: 'vision', port: 8002, icon: Activity, color: '#8b5cf6' },
  { name: 'form', port: 8003, icon: Activity, color: '#f59e0b' },
  { name: 'validation', port: 8004, icon: CheckCircle, color: '#06b6d4' },
]

function App() {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [error, setError] = useState(null)

  // Fetch agent health status
  const fetchAgentStatus = async () => {
    setLoading(true)
    const agentStatuses = await Promise.all(
      AGENTS.map(async (agent) => {
        try {
          const res = await axios.get(`http://localhost:${agent.port}/health`, {
            timeout: 3000
          })
          return {
            ...agent,
            status: 'healthy',
            data: res.data
          }
        } catch (err) {
          return {
            ...agent,
            status: 'unhealthy',
            data: null,
            error: err.message
          }
        }
      })
    )
    setAgents(agentStatuses)
    setLoading(false)
  }

  // Execute task
  const executeTask = async (task, context, priority) => {
    setError(null)
    setResponse(null)

    try {
      const res = await axios.post('http://localhost:8000/execute', {
        task,
        context: context ? JSON.parse(context) : {},
        priority
      })
      setResponse({
        type: 'success',
        data: res.data
      })
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
      setResponse({
        type: 'error',
        data: err.response?.data || { error: err.message }
      })
    }
  }

  useEffect(() => {
    fetchAgentStatus()
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchAgentStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  const healthyCount = agents.filter(a => a.status === 'healthy').length

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div>
            <h1 className="header-title">A2A Multi-Agent System</h1>
            <p className="header-subtitle">
              Agent-to-Agent Protocol Dashboard | {healthyCount}/{agents.length} Agents Online
            </p>
          </div>
          <button
            className="refresh-btn"
            onClick={fetchAgentStatus}
            disabled={loading}
          >
            <RefreshCw size={18} className={loading ? 'spinner' : ''} />
            Refresh
          </button>
        </div>
      </header>

      <div className="container">
        {/* Agent Status Grid */}
        <div className="agent-grid">
          {agents.map((agent) => (
            <AgentCard key={agent.name} agent={agent} />
          ))}
        </div>

        {/* Task Execution Panel */}
        <TaskPanel
          onExecute={executeTask}
          loading={loading}
        />

        {/* Response Display */}
        {response && (
          <ResponsePanel response={response} error={error} />
        )}
      </div>
    </div>
  )
}

export default App
