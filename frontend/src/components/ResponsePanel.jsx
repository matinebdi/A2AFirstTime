import { CheckCircle, XCircle, Info } from 'lucide-react'

function ResponsePanel({ response, error }) {
  if (!response) return null

  const isSuccess = response.type === 'success'

  return (
    <div className="response-panel">
      <h3>Response</h3>

      {isSuccess ? (
        <div className="alert alert-success">
          <CheckCircle size={20} />
          <span>Task dispatched successfully!</span>
        </div>
      ) : (
        <div className="alert alert-error">
          <XCircle size={20} />
          <span>Error: {error || 'Task execution failed'}</span>
        </div>
      )}

      <div className="response-content">
        <pre className="response-json">
          {JSON.stringify(response.data, null, 2)}
        </pre>
      </div>

      {isSuccess && response.data.sent_to && (
        <div className="alert alert-info" style={{ marginTop: '1rem' }}>
          <Info size={20} />
          <span>Task sent to <strong>{response.data.sent_to}</strong> agent for processing</span>
        </div>
      )}
    </div>
  )
}

export default ResponsePanel
