import { useEffect, useState } from 'react'
import { getDashboard } from '../services/dashboard.js'
import ArticleCard from '../components/ArticleCard.jsx'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch((e) => setError(e.friendlyMessage || e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div><span className="spinner" /> Loading dashboard…</div>
  if (error) return <div className="alert alert-error">{error}</div>
  if (!data) return null

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>

      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Total Articles</div>
          <div className="metric-value">{data.total_articles}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Approved</div>
          <div className="metric-value" style={{ color: 'var(--c-success)' }}>{data.approved_articles}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Pending Approval</div>
          <div className="metric-value" style={{ color: 'var(--c-warning)' }}>{data.pending_approvals}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Drafts</div>
          <div className="metric-value">{data.draft_articles}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Active Users</div>
          <div className="metric-value">{data.active_users}</div>
        </div>
      </div>

      <section>
        <h2>Most Viewed</h2>
        <div className="card-grid">
          {data.most_viewed?.length
            ? data.most_viewed.map((a) => <ArticleCard key={a.id} article={a} />)
            : <div className="empty">No approved articles yet.</div>}
        </div>
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Recent Activity</h2>
        <div className="card-grid">
          {data.recent?.length
            ? data.recent.map((a) => <ArticleCard key={a.id} article={a} />)
            : <div className="empty">Nothing recent.</div>}
        </div>
      </section>
    </div>
  )
}
