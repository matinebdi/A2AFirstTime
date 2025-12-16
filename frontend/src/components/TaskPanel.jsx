import { useState } from 'react'
import { Send, Loader } from 'lucide-react'

const SAMPLE_TASKS = [
  {
    name: 'Fill Registration Form',
    task: 'Fill the registration form with username and email',
    context: '{"page": "registration"}'
  },
  {
    name: 'Analyze UI',
    task: 'Analyze the current page UI and detect all interactive elements',
    context: '{"page": "dashboard"}'
  },
  {
    name: 'Validate Form',
    task: 'Validate that all form fields are correctly filled',
    context: '{"form": "contact"}'
  }
]

function TaskPanel({ onExecute, loading }) {
  const [task, setTask] = useState('')
  const [context, setContext] = useState('{}')
  const [priority, setPriority] = useState('normal')
  const [executing, setExecuting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!task.trim()) return

    setExecuting(true)
    await onExecute(task, context, priority)
    setExecuting(false)
  }

  const loadSample = (sample) => {
    setTask(sample.task)
    setContext(sample.context)
  }

  return (
    <div className="task-panel">
      <h2>Execute Task</h2>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {SAMPLE_TASKS.map((sample, i) => (
          <button
            key={i}
            className="refresh-btn"
            onClick={() => loadSample(sample)}
            style={{ fontSize: '0.875rem' }}
          >
            {sample.name}
          </button>
        ))}
      </div>

      <form className="task-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="task">Task Description</label>
          <textarea
            id="task"
            className="form-textarea"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Enter the task you want the agents to execute..."
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="context">Context (JSON)</label>
          <textarea
            id="context"
            className="form-textarea"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder='{"key": "value"}'
            style={{ minHeight: '80px' }}
          />
        </div>

        <div className="form-group">
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            className="form-input"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
          >
            <option value="low">Low</option>
            <option value="normal">Normal</option>
            <option value="high">High</option>
          </select>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={executing || loading}
        >
          {executing ? (
            <>
              <Loader size={20} className="spinner" />
              Executing...
            </>
          ) : (
            <>
              <Send size={20} />
              Execute Task
            </>
          )}
        </button>
      </form>
    </div>
  )
}

export default TaskPanel
