import { CheckCircle, XCircle, Activity } from 'lucide-react'

function AgentCard({ agent }) {
  const Icon = agent.icon || Activity
  const isHealthy = agent.status === 'healthy'

  return (
    <div className={`agent-card status-${agent.status}`}>
      <div className="agent-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            background: isHealthy ? agent.color + '20' : '#ef444420',
            color: isHealthy ? agent.color : '#ef4444',
            padding: '0.5rem',
            borderRadius: '8px',
            display: 'flex'
          }}>
            <Icon size={24} />
          </div>
          <h3 className="agent-name">{agent.name}</h3>
        </div>
        <span className={`status-badge ${agent.status}`}>
          <span className="status-indicator"></span>
          {isHealthy ? 'Online' : 'Offline'}
        </span>
      </div>

      {agent.data ? (
        <div className="agent-info">
          <div className="info-row">
            <span className="info-label">Port</span>
            <span className="info-value">{agent.port}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Redis</span>
            <span className="info-value" style={{ color: agent.data.redis === 'connected' ? '#10b981' : '#ef4444' }}>
              {agent.data.redis || 'unknown'}
            </span>
          </div>
          {agent.data.ai_service && (
            <div className="info-row">
              <span className="info-label">AI Service</span>
              <span className="info-value" style={{ color: agent.data.ai_service === 'enabled' ? '#10b981' : '#6b7280' }}>
                {agent.data.ai_service}
              </span>
            </div>
          )}
          {agent.data.vision_service && (
            <div className="info-row">
              <span className="info-label">Vision</span>
              <span className="info-value" style={{ color: agent.data.vision_service === 'enabled' ? '#10b981' : '#6b7280' }}>
                {agent.data.vision_service}
              </span>
            </div>
          )}
          {agent.data.stored_sessions !== undefined && (
            <div className="info-row">
              <span className="info-label">Sessions</span>
              <span className="info-value">{agent.data.stored_sessions}</span>
            </div>
          )}
          {agent.data.total_validations !== undefined && (
            <div className="info-row">
              <span className="info-label">Validations</span>
              <span className="info-value">{agent.data.total_validations}</span>
            </div>
          )}
          <div className="info-row">
            <span className="info-label">Environment</span>
            <span className="info-value">{agent.data.environment || 'N/A'}</span>
          </div>
        </div>
      ) : (
        <div className="agent-info">
          <div className="alert alert-error">
            <XCircle size={20} />
            <span>{agent.error || 'Connection failed'}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentCard
