import { useEffect, useState } from 'react'
import { listBookmarks } from '../services/articles.js'
import { useUser } from '../services/UserContext.jsx'
import ArticleCard from '../components/ArticleCard.jsx'

export default function Bookmarks() {
  const { currentUser } = useUser()
  const [items, setItems] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!currentUser) return
    setLoading(true)
    listBookmarks(currentUser.id)
      .then(setItems)
      .catch((e) => setError(e.friendlyMessage || e.message))
      .finally(() => setLoading(false))
  }, [currentUser?.id])

  return (
    <div>
      <div className="page-header"><h1>Your Bookmarks</h1></div>
      {error && <div className="alert alert-error">{error}</div>}
      {loading
        ? <div><span className="spinner" /> Loading…</div>
        : (items.length
            ? <div className="card-grid">{items.map((a) => <ArticleCard key={a.id} article={a} />)}</div>
            : <div className="empty">No bookmarks yet. Open an article and tap ☆.</div>)}
    </div>
  )
}
