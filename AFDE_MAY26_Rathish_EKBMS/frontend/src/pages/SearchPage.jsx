import { useState } from 'react'
import { searchArticles } from '../services/articles.js'
import ArticleCard from '../components/ArticleCard.jsx'

export default function SearchPage() {
  const [q, setQ] = useState('')
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const run = async (e) => {
    e?.preventDefault()
    if (!q.trim()) return
    setLoading(true); setError(null)
    try {
      const r = await searchArticles(q.trim())
      setResults(r)
    } catch (err) {
      setError(err.friendlyMessage || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="page-header"><h1>Search</h1></div>

      <form className="search-bar" onSubmit={run}>
        <input
          autoFocus
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search titles, content, and tags…"
        />
        <button className="btn-primary" type="submit">Search</button>
      </form>

      {error && <div className="alert alert-error">{error}</div>}
      {loading && <div><span className="spinner" /> Searching…</div>}

      {results !== null && !loading && (
        <>
          <p style={{ color: '#475569' }}>
            {results.length} result{results.length === 1 ? '' : 's'} for <strong>“{q}”</strong>
          </p>
          {results.length
            ? <div className="card-grid">{results.map((a) => <ArticleCard key={a.id} article={a} />)}</div>
            : <div className="empty">No matches. Try a different query or check spelling.</div>}
        </>
      )}
    </div>
  )
}
