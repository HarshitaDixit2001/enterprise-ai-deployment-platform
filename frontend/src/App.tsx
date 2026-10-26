
import { useCallback, useEffect, useState, type FormEvent } from 'react'
import {
  Activity,
  AlertCircle,
  BarChart3,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  ClipboardCheck,
  Clock3,
  Cloud,
  Database,
  Gauge,
  RefreshCw,
  ShieldCheck,
  Workflow,
  Zap,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './App.css'

async function fetchApi<T>(url: string): Promise<T> {
  const response = await fetch(`/api${url}`)

  if (!response.ok) {
    throw new Error(`API request failed (${response.status}): ${url}`)
  }

  return (await response.json()) as T
}

type Page =
  | 'Overview'
  | 'Use Cases'
  | 'Evaluations'
  | 'Release Governance'
  | 'Audit History'
  | 'Observability'

type Navigation = {
  label: Page
  icon: typeof Workflow
}

const navigation: Navigation[] = [
  { label: 'Overview', icon: Workflow },
  { label: 'Use Cases', icon: Database },
  { label: 'Evaluations', icon: BarChart3 },
  { label: 'Release Governance', icon: ShieldCheck },
  { label: 'Audit History', icon: ClipboardCheck },
  { label: 'Observability', icon: Activity },
]

type HealthResponse = {
  status?: string
  service?: string
  [key: string]: unknown
}

type UseCase = {
  use_case_id: string
  name: string
  business_objective: string
  risk_level: 'low' | 'medium' | 'high'
  evaluation_dataset: string
  requires_human_approval: boolean
  criteria?: {
    min_task_success_rate: number
    max_latency_ms: number
    max_cost_per_task: number
    min_safety_score: number
  }
}

type EvaluationSummary = {
  ready?: boolean
  reports?: Record<string, {
    status?: string
    dataset?: string
    dataset_size?: number
    metrics?: Record<string, unknown>
    error_rate?: number
    incorrect_case_count?: number
    comparisons?: unknown
  }>
  missing_reports?: string[]
  limitations?: string[]
}


type ApiState<T> = {
  data: T | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

const useApi = <T,>(url: string) => {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await fetchApi<T>(url)
      setData(result)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Unable to load data',
      )
    } finally {
      setLoading(false)
    }
  }, [url])

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      setLoading(true)
      setError(null)

      try {
        const result = await fetchApi<T>(url)
        if (!cancelled) setData(result)
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : 'Unable to load data',
          )
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    void load()

    return () => {
      cancelled = true
    }
  }, [url])

  return { data, loading, error, refresh }
}


function formatPercent(value: unknown): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return 'â€”'
  return `${(value * 100).toFixed(1)}%`
}

function formatNumber(value: unknown): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return 'â€”'
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 2,
  }).format(value)
}

function StatusDot({ status }: { status: string }) {
  const normalized = status.toLowerCase()
  const healthy = ['healthy', 'ready', 'running', 'available', 'approved'].includes(normalized)

  return (
    <span className={`status-dot ${healthy ? 'is-healthy' : 'is-warning'}`}>
      <span />
      {status}
    </span>
  )
}

function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
  tone = 'blue',
}: {
  label: string
  value: string
  detail: string
  icon: typeof Activity
  tone?: 'blue' | 'green' | 'purple' | 'amber'
}) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span className="metric-label">{label}</span>
        <span className={`metric-icon tone-${tone}`}>
          <Icon size={19} />
        </span>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-detail">{detail}</div>
    </article>
  )
}

function LoadingState() {
  return <div className="empty-state">Loading live dataâ€¦</div>
}

function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry: () => void
}) {
  return (
    <div className="inline-error">
      <AlertCircle size={18} />
      <span>{message}</span>
      <button className="text-button" onClick={onRetry}>Retry</button>
    </div>
  )
}

function OverviewPage({
  health,
  readiness,
  metrics,
  summary,
  useCases,
  refreshAll,
}: {
  health: ApiState<HealthResponse>
  readiness: ApiState<HealthResponse>
  metrics: ApiState<Record<string, unknown>>
  summary: ApiState<EvaluationSummary>
  useCases: ApiState<UseCase[]>
  refreshAll: () => void
}) {
  const reports = summary.data?.reports ?? {}
  const availableReports = Object.entries(reports).filter(
    ([, report]) => report.status === 'available',
  )
  const baseline = reports.baseline
  const baselineMetrics = baseline?.metrics ?? {}

  const categoryAccuracy = baselineMetrics.category_accuracy
  const priorityAccuracy = baselineMetrics.priority_accuracy
  const taskSuccess = baselineMetrics.task_success_rate
  const totalCases = baseline?.dataset_size

  const chartData = [
    { name: 'Task success', value: typeof taskSuccess === 'number' ? taskSuccess * 100 : 0, available: typeof taskSuccess === 'number' },
    { name: 'Category', value: typeof categoryAccuracy === 'number' ? categoryAccuracy * 100 : 0, available: typeof categoryAccuracy === 'number' },
    { name: 'Priority', value: typeof priorityAccuracy === 'number' ? priorityAccuracy * 100 : 0, available: typeof priorityAccuracy === 'number' },
  ]

  const healthStatus = health.data?.status ?? (health.error ? 'unavailable' : 'loading')
  const readinessStatus = readiness.data?.status ?? (readiness.error ? 'unavailable' : 'loading')
  const metricEntries = metrics.data ? Object.entries(metrics.data) : []

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">PLATFORM OVERVIEW</div>
          <h1>AI deployment command center</h1>
          <p>Evaluate quality, review release readiness, and monitor platform health.</p>
        </div>
        <button className="secondary-button" onClick={refreshAll}>
          <RefreshCw size={16} /> Refresh data
        </button>
      </div>

      <section className="metric-grid">
        <MetricCard
          label="Service health"
          value={health.loading ? 'â€¦' : healthStatus}
          detail={health.error ? 'API not reachable' : 'GET /health'}
          icon={Activity}
          tone="green"
        />
        <MetricCard
          label="Readiness"
          value={readiness.loading ? 'â€¦' : readinessStatus}
          detail="Production readiness checks"
          icon={ShieldCheck}
          tone="purple"
        />
        <MetricCard
          label="Registered use cases"
          value={useCases.loading ? 'â€¦' : useCases.data ? String(useCases.data.length) : 'â€”'}
          detail="Current in-memory registry"
          icon={Workflow}
          tone="blue"
        />
        <MetricCard
          label="Evaluation reports"
          value={summary.loading ? 'â€¦' : String(availableReports.length)}
          detail={summary.data?.ready ? 'All configured reports available' : 'Based on report files found'}
          icon={BarChart3}
          tone="amber"
        />
      </section>

      <section className="dashboard-grid">
        <article className="panel performance-panel">
          <div className="panel-heading">
            <div>
              <h2>Evaluation performance</h2>
              <p>Baseline report Â· values from the backend</p>
            </div>
            <span className="subtle-tag">
              <Database size={14} /> {baseline?.dataset ?? 'Dataset unavailable'}
            </span>
          </div>

          {summary.loading ? <LoadingState /> : summary.error ? (
            <ErrorState message={summary.error} onRetry={() => void summary.refresh()} />
          ) : chartData.some((item) => item.available) ? (
            <>
              <div className="chart-summary">
                <div>
                  <span className="small-label">Task success rate</span>
                  <strong>{formatPercent(taskSuccess)}</strong>
                </div>
                <div>
                  <span className="small-label">Evaluation cases</span>
                  <strong>{formatNumber(totalCases)}</strong>
                </div>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 12, right: 12, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e8edf4" />
                    <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: '#697586', fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fill: '#697586', fontSize: 12 }} />
                    <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Score']} />
                    <Bar dataKey="value" fill="#5277e8" radius={[6, 6, 0, 0]} maxBarSize={54}>
                      {chartData.map((item) => (
                        <Cell key={item.name} fill={item.available ? '#5277e8' : '#e6ebf2'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="chart-footnote">
                Missing report metrics are shown as unavailable, not as measured zeroes.
              </p>
            </>
          ) : (
            <div className="empty-state large-empty">
              <BarChart3 size={28} />
              <strong>No baseline metrics available</strong>
              <span>Generate the baseline report to display real evaluation results here.</span>
            </div>
          )}
        </article>

        <article className="panel health-panel">
          <div className="panel-heading">
            <div>
              <h2>Platform checks</h2>
              <p>Live service endpoints</p>
            </div>
            <span className="panel-heading-icon"><Gauge size={19} /></span>
          </div>

          <div className="check-list">
            <div className="check-row">
              <span className="check-icon"><Activity size={17} /></span>
              <div className="check-copy">
                <strong>API service</strong>
                <span>{health.data?.service ?? 'Backend health endpoint'}</span>
              </div>
              <StatusDot status={healthStatus} />
            </div>
            <div className="check-row">
              <span className="check-icon"><ShieldCheck size={17} /></span>
              <div className="check-copy">
                <strong>Readiness checks</strong>
                <span>Dependency and configuration checks</span>
              </div>
              <StatusDot status={readinessStatus} />
            </div>
            <div className="check-row">
              <span className="check-icon"><BarChart3 size={17} /></span>
              <div className="check-copy">
                <strong>Evaluation service</strong>
                <span>Report availability</span>
              </div>
              <StatusDot status={summary.data?.ready ? 'available' : 'review'} />
            </div>
          </div>

          {(health.error || readiness.error || summary.error) && (
            <div className="health-notice">
              <AlertCircle size={16} />
              Some checks could not be loaded. Start the backend and retry.
            </div>
          )}
        </article>
      </section>

      <section className="dashboard-grid lower-grid">
        <article className="panel use-cases-panel">
          <div className="panel-heading">
            <div>
              <h2>Registered use cases</h2>
              <p>Business objectives and risk classification</p>
            </div>
            <span className="subtle-tag">{useCases.data?.length ?? 0} total</span>
          </div>

          {useCases.loading ? <LoadingState /> : useCases.error ? (
            <ErrorState message={useCases.error} onRetry={() => void useCases.refresh()} />
          ) : useCases.data?.length ? (
            <div className="use-case-list">
              {useCases.data.slice(0, 4).map((item) => (
                <div className="use-case-row" key={item.use_case_id}>
                  <div className="use-case-symbol"><Workflow size={17} /></div>
                  <div className="use-case-copy">
                    <strong>{item.name}</strong>
                    <span>{item.use_case_id} Â· {item.evaluation_dataset}</span>
                  </div>
                  <span className={`risk-badge risk-${item.risk_level}`}>{item.risk_level} risk</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state large-empty">
              <Workflow size={28} />
              <strong>No use cases registered</strong>
              <span>Register a use case to start evaluating candidates and release criteria.</span>
            </div>
          )}
        </article>

        <article className="panel metrics-panel">
          <div className="panel-heading">
            <div>
              <h2>Request metrics</h2>
              <p>Snapshot from the monitoring endpoint</p>
            </div>
            <span className="panel-heading-icon"><Zap size={19} /></span>
          </div>

          {metrics.loading ? <LoadingState /> : metrics.error ? (
            <ErrorState message={metrics.error} onRetry={() => void metrics.refresh()} />
          ) : metricEntries.length ? (
            <div className="raw-metric-list">
              {metricEntries.slice(0, 8).map(([key, value]) => (
                <div className="raw-metric-row" key={key}>
                  <span>{key.replaceAll('_', ' ')}</span>
                  <strong>{typeof value === 'number' ? formatNumber(value) : String(value)}</strong>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state large-empty">
              <Gauge size={28} />
              <strong>No request metrics reported</strong>
              <span>The backend has not exposed any metric values yet.</span>
            </div>
          )}
        </article>
      </section>

      {summary.data?.limitations && summary.data.limitations.length > 0 && (
        <section className="notice-panel">
          <CircleHelp size={19} />
          <div>
            <strong>Evaluation context</strong>
            <p>{summary.data.limitations[0]}</p>
          </div>
        </section>
      )}
    </>
  )
}


function UseCasesPage({ useCases }: { useCases: ApiState<UseCase[]> }) {
  const [form, setForm] = useState({
    use_case_id: 'customer-feedback-assistant',
    name: 'Customer Feedback Assistant',
    business_objective: 'Classify customer feedback and prioritize follow-up.',
    risk_level: 'medium' as UseCase['risk_level'],
    evaluation_dataset: 'customer_feedback_v1',
    min_task_success_rate: '0.9',
    max_latency_ms: '2000',
    max_cost_per_task: '0.05',
    min_safety_score: '0.95',
    requires_human_approval: true,
  })
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  function updateForm<K extends keyof typeof form>(
    key: K,
    value: (typeof form)[K],
  ) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    setSuccessMessage(null)

    if (form.risk_level === 'high' && !form.requires_human_approval) {
      setFormError('High-risk use cases must require human approval.')
      return
    }

    const payload = {
      use_case_id: form.use_case_id.trim(),
      name: form.name.trim(),
      business_objective: form.business_objective.trim(),
      risk_level: form.risk_level,
      evaluation_dataset: form.evaluation_dataset.trim(),
      criteria: {
        min_task_success_rate: Number(form.min_task_success_rate),
        max_latency_ms: Number(form.max_latency_ms),
        max_cost_per_task: Number(form.max_cost_per_task),
        min_safety_score: Number(form.min_safety_score),
      },
      requires_human_approval: form.requires_human_approval,
    }

    if (
      !payload.use_case_id ||
      !payload.name ||
      !payload.business_objective ||
      !payload.evaluation_dataset
    ) {
      setFormError('Please complete all required fields.')
      return
    }

    if (
      !Number.isFinite(payload.criteria.min_task_success_rate) ||
      payload.criteria.min_task_success_rate < 0 ||
      payload.criteria.min_task_success_rate > 1 ||
      !Number.isFinite(payload.criteria.max_latency_ms) ||
      payload.criteria.max_latency_ms < 0 ||
      !Number.isFinite(payload.criteria.max_cost_per_task) ||
      payload.criteria.max_cost_per_task < 0 ||
      !Number.isFinite(payload.criteria.min_safety_score) ||
      payload.criteria.min_safety_score < 0 ||
      payload.criteria.min_safety_score > 1
    ) {
      setFormError('Enter valid thresholds. Rates must be between 0 and 1; latency and cost cannot be negative.')
      return
    }

    setSubmitting(true)

    try {
      const response = await fetch('/api/use-cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const result: unknown = await response.json().catch(() => null)

      if (!response.ok) {
        const body = result as { detail?: unknown } | null
        const detail = body?.detail
        const message =
          typeof detail === 'string'
            ? detail
            : detail
              ? JSON.stringify(detail)
              : `Registration failed (${response.status}).`
        throw new Error(message)
      }

      setSuccessMessage('Use case registered successfully.')
      await useCases.refresh()
    } catch (err) {
      setFormError(
        err instanceof Error ? err.message : 'Unable to register the use case.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">REGISTRY</div>
          <h1>Use cases</h1>
          <p>Register AI use cases and define measurable release criteria.</p>
        </div>
      </div>

      <section className="panel full-panel registration-panel">
        <div className="panel-heading">
          <div>
            <h2>Register a use case</h2>
            <p>Details are submitted to the platform API.</p>
          </div>
        </div>

        <form className="registration-form" onSubmit={handleSubmit}>
          <div className="registration-grid">
            <label className="registration-field">
              Use-case ID
              <input
                required
                minLength={1}
                maxLength={100}
                value={form.use_case_id}
                onChange={(event) => updateForm('use_case_id', event.target.value)}
                placeholder="customer-feedback-assistant"
              />
            </label>

            <label className="registration-field">
              Use-case name
              <input
                required
                maxLength={150}
                value={form.name}
                onChange={(event) => updateForm('name', event.target.value)}
                placeholder="Customer Feedback Assistant"
              />
            </label>

            <label className="registration-field registration-field-wide">
              Business objective
              <textarea
                required
                maxLength={1000}
                rows={3}
                value={form.business_objective}
                onChange={(event) => updateForm('business_objective', event.target.value)}
                placeholder="Describe the business problem this AI system addresses."
              />
            </label>

            <label className="registration-field">
              Risk level
              <select
                value={form.risk_level}
                onChange={(event) =>
                  updateForm('risk_level', event.target.value as UseCase['risk_level'])
                }
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>

            <label className="registration-field">
              Evaluation dataset
              <input
                required
                maxLength={150}
                value={form.evaluation_dataset}
                onChange={(event) => updateForm('evaluation_dataset', event.target.value)}
                placeholder="customer_feedback_v1"
              />
            </label>
          </div>

          <div className="registration-subheading">
            <h3>Acceptance criteria</h3>
            <p>Set the thresholds this use case should meet.</p>
          </div>

          <div className="registration-grid registration-grid-four">
            <label className="registration-field">
              Minimum task success
              <input
                required
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={form.min_task_success_rate}
                onChange={(event) => updateForm('min_task_success_rate', event.target.value)}
              />
              <span className="field-hint">0 to 1 (e.g. 0.90 = 90%)</span>
            </label>

            <label className="registration-field">
              Maximum latency (ms)
              <input
                required
                type="number"
                min="0"
                step="1"
                value={form.max_latency_ms}
                onChange={(event) => updateForm('max_latency_ms', event.target.value)}
              />
            </label>

            <label className="registration-field">
              Maximum cost per task (USD)
              <input
                required
                type="number"
                min="0"
                step="0.001"
                value={form.max_cost_per_task}
                onChange={(event) => updateForm('max_cost_per_task', event.target.value)}
              />
            </label>

            <label className="registration-field">
              Minimum safety score
              <input
                required
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={form.min_safety_score}
                onChange={(event) => updateForm('min_safety_score', event.target.value)}
              />
              <span className="field-hint">0 to 1</span>
            </label>
          </div>

          <label className="approval-option">
            <input
              type="checkbox"
              checked={form.requires_human_approval}
              onChange={(event) =>
                updateForm('requires_human_approval', event.target.checked)
              }
            />
            <span>
              <strong>Require human approval</strong>
              <span>Require a human approval step before a release can proceed.</span>
            </span>
          </label>

          {form.risk_level === 'high' && !form.requires_human_approval && (
            <p className="form-notice">
              High-risk use cases must require human approval.
            </p>
          )}

          {formError && (
            <div className="form-feedback form-feedback-error" role="alert">
              <AlertCircle size={18} />
              <span>{formError}</span>
            </div>
          )}

          {successMessage && (
            <div className="form-feedback form-feedback-success" role="status">
              <CheckCircle2 size={18} />
              <span>{successMessage}</span>
            </div>
          )}

          <div className="registration-actions">
            <button className="primary-button" type="submit" disabled={submitting}>
              {submitting ? 'Registeringâ€¦' : 'Register use case'}
            </button>
          </div>
        </form>
      </section>

      <section className="panel full-panel">
        <div className="panel-heading">
          <div>
            <h2>Registered use cases</h2>
            <p>Data from GET /use-cases</p>
          </div>
          <span className="subtle-tag">{useCases.data?.length ?? 0} registered</span>
        </div>

        {useCases.loading ? <LoadingState /> : useCases.error ? (
          <ErrorState
            message={useCases.error}
            onRetry={() => void useCases.refresh()}
          />
        ) : useCases.data?.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Use case</th>
                  <th>Risk</th>
                  <th>Dataset</th>
                  <th>Task success target</th>
                  <th>Latency limit</th>
                  <th>Human approval</th>
                </tr>
              </thead>
              <tbody>
                {useCases.data.map((item) => (
                  <tr key={item.use_case_id}>
                    <td>
                      <strong>{item.name}</strong>
                      <span className="table-secondary">{item.use_case_id}</span>
                    </td>
                    <td>
                      <span className={`risk-badge risk-${item.risk_level}`}>
                        {item.risk_level}
                      </span>
                    </td>
                    <td>{item.evaluation_dataset}</td>
                    <td>{formatPercent(item.criteria?.min_task_success_rate)}</td>
                    <td>
                      {item.criteria
                        ? `${formatNumber(item.criteria.max_latency_ms)} ms`
                        : 'â€”'}
                    </td>
                    <td>{item.requires_human_approval ? 'Required' : 'Not required'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state large-empty">
            <Workflow size={28} />
            <strong>No registered use cases</strong>
            <span>Register your first use case using the form above.</span>
          </div>
        )}
      </section>
    </>
  )
}


function EvaluationsPage({ summary }: { summary: ApiState<EvaluationSummary> }) {
  const reports = summary.data?.reports ?? {}
  const [selectedReport, setSelectedReport] = useState<string | null>(null)
  const [reportDetails, setReportDetails] = useState<Record<string, unknown> | null>(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [reportError, setReportError] = useState<string | null>(null)

  const openReport = async (name: string) => {
    setSelectedReport(name)
    setReportDetails(null)
    setReportError(null)
    setReportLoading(true)

    try {
      const data = await fetchApi<Record<string, unknown>>(`/evaluations/reports/${name}`)
      setReportDetails(data)
    } catch (error) {
      setReportError(error instanceof Error ? error.message : 'Unable to load report.')
    } finally {
      setReportLoading(false)
    }
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">QUALITY & VALIDATION</div>
          <h1>Evaluations</h1>
          <p>Review evaluation reports, inspect failures, and understand limitations.</p>
        </div>
      </div>

      <section className="metric-grid evaluation-status-grid">
        <MetricCard label="Available reports" value={String(Object.values(reports).filter((r) => r.status === 'available').length)} detail="Report files found and parsed" icon={CheckCircle2} tone="green" />
        <MetricCard label="Missing reports" value={String(summary.data?.missing_reports?.length ?? 0)} detail="Configured reports not found" icon={Database} tone="amber" />
        <MetricCard label="Evaluation readiness" value={summary.data?.ready ? 'Ready' : 'Review'} detail="Based on configured report availability" icon={ShieldCheck} tone="purple" />
      </section>

      <section className="panel full-panel">
        <div className="panel-heading">
          <div>
            <h2>Evaluation reports</h2>
            <p>Select a report card to inspect its full results.</p>
          </div>
        </div>

        {summary.loading ? <LoadingState /> : summary.error ? (
          <ErrorState message={summary.error} onRetry={() => void summary.refresh()} />
        ) : Object.keys(reports).length ? (
          <div className="report-grid">
            {Object.entries(reports).map(([name, report]) => (
              <button
                type="button"
                className={`report-card report-card-button${selectedReport === name ? ' selected' : ''}`}
                key={name}
                onClick={() => void openReport(name)}
                disabled={report.status !== 'available'}
                aria-pressed={selectedReport === name}
              >
                <div className="report-card-top">
                  <span className="report-icon"><BarChart3 size={20} /></span>
                  <StatusDot status={report.status ?? 'unknown'} />
                </div>
                <h3>{name.replaceAll('_', ' ')}</h3>
                <p>{report.dataset || ('path' in report ? String(report.path ?? '') : '') || 'Report details unavailable'}</p>
                <div className="report-meta">
                  <span>Dataset size</span>
                  <strong>{formatNumber(report.dataset_size)}</strong>
                </div>
                {report.incorrect_case_count !== undefined && (
                  <div className="report-meta">
                    <span>Incorrect cases</span>
                    <strong>{formatNumber(report.incorrect_case_count)}</strong>
                  </div>
                )}
                {report.error_rate !== undefined && (
                  <div className="report-meta">
                    <span>Error rate</span>
                    <strong>{formatPercent(report.error_rate)}</strong>
                  </div>
                )}
                <span className="report-open-hint">Click to view details →</span>
              </button>
            ))}
          </div>
        ) : (
          <div className="empty-state large-empty">
            <BarChart3 size={28} />
            <strong>No evaluation reports found</strong>
            <span>Run the project's evaluation scripts to generate reports.</span>
          </div>
        )}
      </section>

      {selectedReport && (
        <section className="panel full-panel report-detail-panel">
          <div className="panel-heading">
            <div>
              <h2>{selectedReport.replaceAll('_', ' ')} details</h2>
              <p>Full contents of the selected report file</p>
            </div>
            <button type="button" className="secondary-button" onClick={() => {
              setSelectedReport(null)
              setReportDetails(null)
              setReportError(null)
            }}>
              Close details
            </button>
          </div>

          {reportLoading ? <LoadingState /> : reportError ? (
            <ErrorState message={reportError} onRetry={() => void openReport(selectedReport)} />
          ) : reportDetails ? (
<div className="report-readable">
  {typeof reportDetails.metrics === 'object' && reportDetails.metrics !== null && (
    <>
      <div className="metric-grid">
        {Object.entries(reportDetails.metrics as Record<string, unknown>)
          .filter(([key, value]) =>
            ['task_success_rate', 'category_accuracy', 'priority_accuracy'].includes(key)
            && typeof value === 'number'
          )
          .map(([key, value]) => (
            <MetricCard
              key={key}
              label={key.replaceAll('_', ' ')}
              value={`${((value as number) * 100).toFixed(1)}%`}
              detail="Evaluation metric"
              icon={BarChart3}
              tone="purple"
            />
          ))}
      </div>

      <section className="report-detail-section">
        <h3>Failed cases</h3>
        {Array.isArray((reportDetails.metrics as Record<string, unknown>).failed_case_ids)
          && ((reportDetails.metrics as Record<string, unknown>).failed_case_ids as string[]).length > 0 ? (
            <div className="report-failed-cases">
              {((reportDetails.metrics as Record<string, unknown>).failed_case_ids as string[]).map((caseId) => (
                <span key={caseId}>{caseId}</span>
              ))}
            </div>
          ) : <p>No failed cases recorded.</p>}
      </section>
    </>
  )}

  {Array.isArray(reportDetails.limitations) && (
    <section className="report-detail-section">
      <h3>Report limitations</h3>
      <ul className="limitations-list">
        {(reportDetails.limitations as string[]).map((item) => <li key={item}>{item}</li>)}
      </ul>
    </section>
  )}

  <details>
    <summary>View raw report JSON</summary>
    <pre className="report-json">{JSON.stringify(reportDetails, null, 2)}</pre>
  </details>
</div>          ) : null}
        </section>
      )}

      {summary.data?.limitations && summary.data.limitations.length > 0 && (
        <section className="panel full-panel">
          <div className="panel-heading">
            <div><h2>Known limitations</h2><p>Important context for interpreting evaluation results</p></div>
          </div>
          <ul className="limitations-list">
            {summary.data.limitations.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </section>
      )}
    </>
  )
}


function GovernancePage({ useCases }: { useCases: ApiState<UseCase[]> }) {
  type Prediction = {
    case_id: string
    predicted_category: string
    predicted_priority: string
    latency_ms: number
    cost_usd: number
    safety_score?: number
  }

  type ReleaseResult = {
    candidate_id: string
    decision: 'approved' | 'rejected'
    reasons: string[]
    checks: Record<string, boolean>
    evaluated_metrics: Record<string, number | null>
  }

  type PolicyResult = {
    candidate_id: string
    decision: 'permitted' | 'blocked'
    reasons: string[]
    checks: Record<string, boolean>
  }

  const [selectedId, setSelectedId] = useState('')
  const [candidateId, setCandidateId] = useState('candidate-v1')
  const [predictionsJson, setPredictionsJson] = useState('')
  const [humanApproval, setHumanApproval] = useState(false)
  const [releaseResult, setReleaseResult] = useState<ReleaseResult | null>(null)
  const [policyResult, setPolicyResult] = useState<PolicyResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [releaseLoading, setReleaseLoading] = useState(false)
  const [policyLoading, setPolicyLoading] = useState(false)

  const useCaseId =
    selectedId || useCases.data?.[0]?.use_case_id || ''

  async function postApi<T>(url: string, payload: unknown): Promise<T> {
    const response = await fetch(`/api${url}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    const body: unknown = await response.json().catch(() => null)

    if (!response.ok) {
      const detail =
        typeof body === 'object' && body !== null && 'detail' in body
          ? body.detail
          : null

      throw new Error(
        typeof detail === 'string'
          ? detail
          : detail
            ? JSON.stringify(detail)
            : `Request failed (${response.status}).`,
      )
    }

    return body as T
  }

  async function handleReleaseDecision() {
    setError(null)
    setReleaseResult(null)
    setPolicyResult(null)

    if (!useCaseId) {
      setError('Select a registered use case first.')
      return
    }

    if (!candidateId.trim()) {
      setError('Enter a candidate ID.')
      return
    }

    let predictions: Prediction[]

    try {
      const parsed: unknown = JSON.parse(predictionsJson)

      if (!Array.isArray(parsed) || parsed.length === 0) {
        throw new Error('Predictions must be a non-empty JSON array.')
      }

      predictions = parsed as Prediction[]
    } catch (err) {
      setError(
        err instanceof Error
          ? `Invalid predictions JSON: ${err.message}`
          : 'Invalid predictions JSON.',
      )
      return
    }

    setReleaseLoading(true)

    try {
      const result = await postApi<ReleaseResult>(
        `/evaluations/${encodeURIComponent(useCaseId)}/release-decision`,
        {
          candidate_id: candidateId.trim(),
          predictions,
        },
      )

      setReleaseResult(result)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to evaluate the release candidate.',
      )
    } finally {
      setReleaseLoading(false)
    }
  }

  async function handlePolicyCheck() {
    setError(null)
    setPolicyResult(null)

    if (!useCaseId || !candidateId.trim()) {
      setError('Select a use case and enter a candidate ID.')
      return
    }

    setPolicyLoading(true)

    try {
      const result = await postApi<PolicyResult>(
        `/deployments/${encodeURIComponent(useCaseId)}/policy-check`,
        {
          candidate_id: candidateId.trim(),
          human_approval_granted: humanApproval,
        },
      )

      setPolicyResult(result)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to check deployment policy.',
      )
    } finally {
      setPolicyLoading(false)
    }
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">POLICY & CONTROL</div>
          <h1>Release governance</h1>
          <p>
            Evaluate candidate quality, record release decisions, and check
            deployment policy.
          </p>
        </div>
      </div>

      <section className="notice-panel">
        <ShieldCheck size={21} />
        <div>
          <strong>Governed workflow</strong>
          <p>
            Evaluate a candidate first. Then check deployment policy using
            the same candidate ID. Required human approval must be granted.
            This workflow does not deploy software.
          </p>
        </div>
      </section>

      {useCases.loading ? (
        <LoadingState />
      ) : useCases.error ? (
        <ErrorState
          message={useCases.error}
          onRetry={() => void useCases.refresh()}
        />
      ) : !useCases.data?.length ? (
        <section className="panel full-panel">
          <div className="empty-state">
            Register a use case before evaluating release candidates.
          </div>
        </section>
      ) : (
        <>
          <section className="panel full-panel">
            <div className="panel-heading">
              <div>
                <h2>Governance configuration</h2>
                <p>Requirements from the registered use cases</p>
              </div>
            </div>

            <div className="governance-list">
              {useCases.data.map((item) => (
                <article className="governance-card" key={item.use_case_id}>
                  <div className="governance-title">
                    <div>
                      <h3>{item.name}</h3>
                      <span>{item.use_case_id}</span>
                    </div>
                    <span className={`risk-badge risk-${item.risk_level}`}>
                      {item.risk_level} risk
                    </span>
                  </div>

                  <p>{item.business_objective}</p>

                  <div className="criteria-grid">
                    <div>
                      <span>Minimum task success</span>
                      <strong>
                        {formatPercent(item.criteria?.min_task_success_rate)}
                      </strong>
                    </div>
                    <div>
                      <span>Maximum latency</span>
                      <strong>
                        {item.criteria
                          ? `${formatNumber(item.criteria.max_latency_ms)} ms`
                          : 'â€”'}
                      </strong>
                    </div>
                    <div>
                      <span>Maximum cost / task</span>
                      <strong>
                        {item.criteria
                          ? `$${formatNumber(item.criteria.max_cost_per_task)}`
                          : 'â€”'}
                      </strong>
                    </div>
                    <div>
                      <span>Minimum safety score</span>
                      <strong>
                        {formatPercent(item.criteria?.min_safety_score)}
                      </strong>
                    </div>
                  </div>

                  <div className="governance-footer">
                    <span>
                      <ShieldCheck size={15} />
                      {item.requires_human_approval
                        ? 'Human approval required'
                        : 'Human approval not required by configuration'}
                    </span>
                    <span>
                      <Database size={15} />
                      {item.evaluation_dataset}
                    </span>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="panel full-panel governance-workflow">
            <div className="panel-heading">
              <div>
                <h2>Release decision</h2>
                <p>
                  Submit candidate predictions for backend evaluation against
                  the registered acceptance criteria.
                </p>
              </div>
            </div>

            <div className="governance-form">
              <label className="registration-field">
                Use case
                <select
                  value={useCaseId}
                  onChange={(event) => {
                    setSelectedId(event.target.value)
                    setReleaseResult(null)
                    setPolicyResult(null)
                    setError(null)
                  }}
                >
                  {useCases.data.map((item) => (
                    <option key={item.use_case_id} value={item.use_case_id}>
                      {item.name} ({item.use_case_id})
                    </option>
                  ))}
                </select>
              </label>

              <label className="registration-field">
                Candidate ID
                <input
                  required
                  maxLength={100}
                  value={candidateId}
                  onChange={(event) => setCandidateId(event.target.value)}
                  placeholder="candidate-v1"
                />
                <span className="field-hint">
                  Use the same candidate ID for the release decision and
                  policy check.
                </span>
              </label>

              <label className="registration-field">
                Candidate predictions (JSON array)
               <textarea
  rows={7}
  value={predictionsJson}
  onChange={(event) => setPredictionsJson(event.target.value)}
  placeholder={'Paste the candidate predictions JSON array here'}
  disabled={releaseLoading || policyLoading}
/>
                <span className="field-hint">
                  Supply one prediction for every case in the configured
                  dataset, with each actual case ID exactly once. Use
                  predictions produced by your candidate; the example
                  illustrates the schema, not actual dataset values.
                </span>
              </label>

              <div className="registration-actions">
                <button
                  className="primary-button"
                  type="button"
                  disabled={releaseLoading || policyLoading}
                  onClick={() => void handleReleaseDecision()}
                >
                  {releaseLoading ? 'Evaluatingâ€¦' : 'Evaluate release candidate'}
                </button>
              </div>
            </div>

            {releaseResult && (
              <div className="governance-result" aria-live="polite">
                <div className="governance-result-heading">
                  <div>
                    <span className="field-hint">Release decision</span>
                    <h3>{releaseResult.candidate_id}</h3>
                  </div>
                  <span
                    className={`risk-badge ${
                      releaseResult.decision === 'approved'
                        ? 'risk-low'
                        : 'risk-high'
                    }`}
                  >
                    {releaseResult.decision.toUpperCase()}
                  </span>
                </div>

                <h4>Acceptance checks</h4>
                <div className="governance-checks">
                  {Object.entries(releaseResult.checks).map(([name, passed]) => (
                    <div className="governance-check" key={name}>
                      <span>{name.replaceAll('_', ' ')}</span>
                      <strong className={passed ? 'check-pass' : 'check-fail'}>
                        {passed ? 'PASS' : 'FAIL'}
                      </strong>
                    </div>
                  ))}
                </div>

                <h4>Evaluated metrics</h4>
                <div className="governance-checks">
                  {Object.entries(releaseResult.evaluated_metrics).map(
                    ([name, value]) => (
                      <div className="governance-check" key={name}>
                        <span>{name.replaceAll('_', ' ')}</span>
                        <strong>
                          {value === null ? 'N/A' : formatNumber(value)}
                        </strong>
                      </div>
                    ),
                  )}
                </div>

                <h4>Decision reasons</h4>
                {releaseResult.reasons.length ? (
                  <ul className="governance-reasons">
                    {releaseResult.reasons.map((reason, index) => (
                      <li key={`${index}-${reason}`}>{reason}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No rejection reasons returned by the backend.</p>
                )}
              </div>
            )}
          </section>

          <section className="panel full-panel governance-workflow">
            <div className="panel-heading">
              <div>
                <h2>Deployment policy check</h2>
                <p>
                  Check whether the candidate satisfies release-gate and
                  human-approval requirements. This does not deploy software.
                </p>
              </div>
            </div>

            <div className="governance-form">
              <div className="governance-candidate-summary">
                <span>Selected candidate</span>
                <strong>{candidateId.trim() || 'No candidate ID entered'}</strong>
                <span>Use case: {useCaseId}</span>
              </div>

              <label className="approval-option">
                <input
                  type="checkbox"
                  checked={humanApproval}
                  onChange={(event) => setHumanApproval(event.target.checked)}
                />
                <span>
                  <strong>Human approval granted</strong>
                  <span>
                    Check this only when an authorized human has actually
                    approved this candidate.
                  </span>
                </span>
              </label>

              <div className="registration-actions">
                <button
                  className="primary-button"
                  type="button"
                  disabled={policyLoading || releaseLoading}
                  onClick={() => void handlePolicyCheck()}
                >
                  {policyLoading ? 'Checking policyâ€¦' : 'Check deployment policy'}
                </button>
              </div>
            </div>

            {policyResult && (
              <div className="governance-result" aria-live="polite">
                <div className="governance-result-heading">
                  <div>
                    <span className="field-hint">Policy result</span>
                    <h3>{policyResult.candidate_id}</h3>
                  </div>
                  <span
                    className={`risk-badge ${
                      policyResult.decision === 'permitted'
                        ? 'risk-low'
                        : 'risk-high'
                    }`}
                  >
                    {policyResult.decision.toUpperCase()}
                  </span>
                </div>

                <h4>Policy checks</h4>
                <div className="governance-checks">
                  {Object.entries(policyResult.checks).map(([name, passed]) => (
                    <div className="governance-check" key={name}>
                      <span>{name.replaceAll('_', ' ')}</span>
                      <strong className={passed ? 'check-pass' : 'check-fail'}>
                        {passed ? 'PASS' : 'FAIL'}
                      </strong>
                    </div>
                  ))}
                </div>

                <h4>Policy explanation</h4>
                {policyResult.reasons.length ? (
                  <ul className="governance-reasons">
                    {policyResult.reasons.map((reason, index) => (
                      <li key={`${index}-${reason}`}>{reason}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No policy blockers returned by the backend.</p>
                )}
              </div>
            )}
          </section>
        </>
      )}

      {error && (
        <div className="form-feedback form-feedback-error" role="alert">
          {error}
        </div>
      )}
    </>
  )
}




function HistoryPage({ useCases }: { useCases: ApiState<UseCase[]> }) {
  const [selectedId, setSelectedId] = useState('')
  const [history, setHistory] = useState<unknown[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const effectiveSelectedId =
  selectedId || useCases.data?.[0]?.use_case_id || ''
  useEffect(() => {
    if (!effectiveSelectedId) {
      return
    }
    let cancelled = false
    const loadHistory = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await fetchApi<
          unknown[] | { value?: unknown[]; Count?: number }
        >(
          `/evaluations/${encodeURIComponent(effectiveSelectedId)}/history`,
        )
        const records = Array.isArray(data)
          ? data
          : Array.isArray(data.value)
            ? data.value
            : []
        if (!cancelled) {
          setHistory(records)
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setHistory([])
          setError(
            err instanceof Error ? err.message : 'Unable to load history',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }
    void loadHistory()
    return () => {
      cancelled = true
    }
  }, [effectiveSelectedId, refreshKey])


  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">AUDIT &amp; TRACEABILITY</div>
          <h1>Release history</h1>
          <p>Inspect recorded release decisions for a registered use case.</p>
        </div>

        <div className="select-wrap">
          <label htmlFor="history-use-case">Use case</label>
          <select
            id="history-use-case"
            value={effectiveSelectedId}
            onChange={(event) => {
              setSelectedId(event.target.value)
              setHistory(null)
            }}
          >
            <option value="">Select a use case</option>
            {useCases.data?.map((item) => (
              <option key={item.use_case_id} value={item.use_case_id}>
                {item.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <section className="panel full-panel">
        <div className="panel-heading">
          <div>
            <h2>Recorded release decisions</h2>
            <p>Data from the use-case release history endpoint</p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={() => setRefreshKey((key) => key + 1)}
            disabled={loading || !effectiveSelectedId}
          >
            Refresh history
          </button>
        </div>

        {useCases.loading || loading ? (
          <LoadingState />
        ) : useCases.error ? (
          <ErrorState
            message={useCases.error}
            onRetry={() => void useCases.refresh()}
          />
        ) : error ? (
          <ErrorState
            message={error}
            onRetry={() => setRefreshKey((key) => key + 1)}
          />
        ) : !effectiveSelectedId ? (
          <div className="empty-state large-empty">
            <ClipboardCheck size={28} />
            <strong>No use case selected</strong>
            <span>
              Register or select a use case to inspect its release history.
            </span>
          </div>
        ) : history === null ? (
          <LoadingState />
        ) : history.length > 0 ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Decision</th>
                  <th>Reasons</th>
                  <th>Checks</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item, index) => {
                  const record = item as Record<string, unknown>
                  const checks = record.checks as
                    | Record<string, boolean>
                    | undefined

                  return (
                    <tr
                      key={`${String(record.candidate_id ?? 'candidate')}-${index}`}
                    >
                      <td>
                        <strong>
                          {String(record.candidate_id ?? 'â€”')}
                        </strong>
                      </td>

                      <td>
                        <span
                          className={`decision-badge ${
                            record.decision === 'approved'
                              ? 'decision-approved'
                              : 'decision-rejected'
                          }`}
                        >
                          {String(record.decision ?? 'unknown')}
                        </span>
                      </td>

                      <td>
                        {Array.isArray(record.reasons)
                          ? record.reasons.map(String).join('; ') ||
                            'No reasons recorded'
                          : 'â€”'}
                      </td>

                      <td>
                        {checks
                          ? Object.entries(checks)
                              .map(
                                ([key, value]) =>
                                  `${key.replaceAll('_', ' ')}: ${
                                    value ? 'pass' : 'fail'
                                  }`,
                              )
                              .join(' Â· ')
                          : 'â€”'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state large-empty">
            <ClipboardCheck size={28} />
            <strong>No release decisions yet</strong>
            <span>
              Run a release evaluation to create the first record.
            </span>
          </div>
        )}
      </section>
    </>
  )
}


function ObservabilityPage({
  health,
  readiness,
  metrics,
  evaluationHealth,
  refreshAll,
}: {
  health: ApiState<HealthResponse>
  readiness: ApiState<HealthResponse>
  metrics: ApiState<Record<string, unknown>>
  evaluationHealth: ApiState<HealthResponse>
  refreshAll: () => void
}) {
  const entries = metrics.data ? Object.entries(metrics.data) : []

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">RELIABILITY & MONITORING</div>
          <h1>Observability</h1>
          <p>Service status, evaluation health, readiness, and request metrics.</p>
        </div>
        <button className="secondary-button" onClick={refreshAll}><RefreshCw size={16} /> Refresh data</button>
      </div>
      <section className="metric-grid">
        <MetricCard label="API health" value={health.data?.status ?? (health.error ? 'Unavailable' : 'Loadingâ€¦')} detail="GET /health" icon={Activity} tone="green" />
        <MetricCard label="Readiness" value={readiness.data?.status ?? (readiness.error ? 'Unavailable' : 'Loadingâ€¦')} detail="GET /ready" icon={ShieldCheck} tone="purple" />
        <MetricCard label="Evaluation health" value={evaluationHealth.data?.status ?? (evaluationHealth.error ? 'Unavailable' : 'Loadingâ€¦')} detail="GET /evaluations/health" icon={BarChart3} tone="blue" />
        <MetricCard label="Metric fields" value={metrics.data ? String(entries.length) : 'â€”'} detail="Values exposed by GET /metrics" icon={Gauge} tone="amber" />
      </section>
      <section className="panel full-panel">
        <div className="panel-heading">
          <div><h2>Metrics snapshot</h2><p>Live response from GET /metrics</p></div>
          <span className="subtle-tag"><Clock3 size={14} /> On demand</span>
        </div>
        {metrics.loading ? <LoadingState /> : metrics.error ? (
          <ErrorState message={metrics.error} onRetry={() => void metrics.refresh()} />
        ) : entries.length ? (
          <div className="metrics-table">
            {entries.map(([key, value]) => (
              <div className="metrics-table-row" key={key}>
                <div className="metrics-key"><Gauge size={16} /><span>{key.replaceAll('_', ' ')}</span></div>
                <strong>{typeof value === 'number' ? formatNumber(value) : String(value)}</strong>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state large-empty"><Gauge size={28} /><strong>No metrics available</strong><span>The monitoring endpoint returned no metric fields.</span></div>
        )}
      </section>
      <section className="panel full-panel">
        <div className="panel-heading"><div><h2>Health check responses</h2><p>Inspect current status and returned details</p></div></div>
        <div className="health-response-grid">
          {[['API health', health], ['Readiness', readiness], ['Evaluation health', evaluationHealth]].map(([label, state]) => {
            const item = state as ApiState<HealthResponse>
            return (
              <article className="health-response-card" key={label as string}>
                <div className="health-response-heading"><strong>{label as string}</strong><StatusDot status={item.data?.status ?? (item.error ? 'unavailable' : 'loading')} /></div>
                {item.error ? <p>{item.error}</p> : <pre>{item.data ? JSON.stringify(item.data, null, 2) : 'Waiting for responseâ€¦'}</pre>}
              </article>
            )
          })}
        </div>
      </section>
    </>
  )
}

function App() {
  const [page, setPage] = useState<Page>('Overview')
  const health = useApi<HealthResponse>('/health')
  const readiness = useApi<HealthResponse>('/ready')
  const metrics = useApi<Record<string, unknown>>('/metrics')
  const summary = useApi<EvaluationSummary>('/evaluations/summary')
  const useCases = useApi<UseCase[]>('/use-cases')
  const evaluationHealth = useApi<HealthResponse>('/evaluations/health')

  const refreshAll = useCallback(() => {
  void health.refresh()
  void readiness.refresh()
  void metrics.refresh()
  void summary.refresh()
  void useCases.refresh()
  void evaluationHealth.refresh()
}, [
  health,
  readiness,
  metrics,
  summary,
  useCases,
  evaluationHealth,
])

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Workflow size={22} /></div>
          <div className="brand-copy">
            <strong>Orbit AI</strong>
            <span>DEPLOYMENT PLATFORM</span>
          </div>
        </div>

        <div className="workspace-label">WORKSPACE</div>
        <nav className="sidebar-nav" aria-label="Main navigation">
          {navigation.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-item ${page === label ? 'active' : ''}`}
              onClick={() => setPage(label)}
            >
              <Icon size={18} strokeWidth={1.9} />
              <span>{label}</span>
              {label === 'Overview' && <span className="nav-active-indicator" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-spacer" />

        <div className="sidebar-status">
          <div className="sidebar-status-top">
            <span className="status-light" />
            <strong>Local environment</strong>
          </div>
          <p>Connected to your FastAPI service through the Vite proxy.</p>
          <div className="environment-line"><span>API target</span><code>127.0.0.1:8000</code></div>
        </div>

        <div className="sidebar-footer">
          <div className="avatar">AI</div>
          <div><strong>Platform workspace</strong><span>Developer mode</span></div>
          <ChevronDown size={16} />
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs"><span>Platform</span><span className="breadcrumb-separator">/</span><strong>{page}</strong></div>
          <div className="topbar-right">
            <span className="environment-badge"><span /> LOCAL DEVELOPMENT</span>
            <button className="icon-button" aria-label="Refresh dashboard data" onClick={refreshAll}><RefreshCw size={17} /></button>
          </div>
        </header>

        <div className="page-content">
          {page === 'Overview' && (
            <OverviewPage
              health={health}
              readiness={readiness}
              metrics={metrics}
              summary={summary}
              useCases={useCases}
              refreshAll={refreshAll}
            />
          )}
          {page === 'Use Cases' && <UseCasesPage useCases={useCases} />}
          {page === 'Evaluations' && <EvaluationsPage summary={summary} />}
          {page === 'Release Governance' && <GovernancePage useCases={useCases} />}
          {page === 'Audit History' && <HistoryPage useCases={useCases} />}
          {page === 'Observability' && (
            <ObservabilityPage
              health={health}
              readiness={readiness}
              metrics={metrics}
              evaluationHealth={evaluationHealth}
              refreshAll={refreshAll}
            />
          )}

          <footer className="page-footer">
            <span>Orbit AI Â· Enterprise AI Deployment &amp; Evaluation Platform</span>
            <span><Cloud size={14} /> Local API integration</span>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default App
