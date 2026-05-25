import { useEffect, useState } from 'react'
import { listArticles } from '../services/articles.js'
import { listCategories } from '../services/categories.js'
import ArticleCard from '../components/ArticleCard.jsx'

export default function ArticlesList() {
  const [articles, setArticles] = useState([])
  const [categories, setCategories] = useState([])
  const [filters, setFilters] = useState({ status: '', category_id: '', tag: '', q: '', sort: 'recent' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { listCategories().then(setCategories).catch(() => {}) }, [])

  useEffect(() => {
    setLoading(true)
    const params = {}
    if (filters.status) params.status = filters.status
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.tag) params.tag = filters.tag
    if (filters.q) params.q = filters.q
    if (filters.sort) params.sort = filters.sort
    listArticles(params)
      .then(setArticles)
      .catch((e) => setError(e.friendlyMessage || e.message))
      .finally(() => setLoading(false))
  }, [filters])

  const update = (k, v) => setFilters((f) => ({ ...f, [k]: v }))

  return (
    <div>
      <div className="page-header"><h1>Articles</h1></div>

      <div className="filter-row">
        <input
          placeholder="Quick text filter…"
          value={filters.q}
          onChange={(e) => update('q', e.target.value)}
        />
        <select value={filters.status} onChange={(e) => update('status', e.target.value)}>
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="archived">Archived</option>
        </select>
        <select value={filters.category_id} onChange={(e) => update('category_id', e.target.value)}>
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <input
          placeholder="Tag…"
          value={filters.tag}
          onChange={(e) => update('tag', e.target.value)}
        />
        <select value={filters.sort} onChange={(e) => update('sort', e.target.value)}>
          <option value="recent">Recently updated</option>
          <option value="popular">Most viewed</option>
          <option value="oldest">Oldest first</option>
        </select>
        <button onClick={() => setFilters({ status: '', category_id: '', tag: '', q: '', sort: 'recent' })}>
          Reset
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {loading
        ? <div><span className="spinner" /> Loading…</div>
        : (articles.length
            ? <div className="card-grid">{articles.map((a) => <ArticleCard key={a.id} article={a} />)}</div>
            : <div className="empty">No articles match.</div>)}
    </div>
  )
}
