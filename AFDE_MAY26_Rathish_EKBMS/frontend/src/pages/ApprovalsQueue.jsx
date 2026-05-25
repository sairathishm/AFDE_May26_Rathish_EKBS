import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listArticles } from '../services/articles.js'
import ArticleCard from '../components/ArticleCard.jsx'

export default function ApprovalsQueue() {
  const [items, setItems] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listArticles({ status: 'pending' })
      .then(setItems)
      .catch((e) => setError(e.friendlyMessage || e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <div className="page-header">
        <h1>Approval Queue</h1>
        <span style={{ color: '#475569' }}>{items.length} pending</span>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {loading
        ? <div><span className="spinner" /> Loading queue…</div>
        : (items.length
            ? (
                <div className="card-grid">
                  {items.map((a) => (
                    <div key={a.id}>
                      <ArticleCard article={a} />
                      <div style={{ marginTop: 6, textAlign: 'right' }}>
                        <Link className="btn-primary" to={`/articles/${a.id}`}>Review →</Link>
                      </div>
                    </div>
                  ))}
                </div>
              )
            : <div className="empty">No articles awaiting approval. Inbox zero!</div>)}
    </div>
  )
}
