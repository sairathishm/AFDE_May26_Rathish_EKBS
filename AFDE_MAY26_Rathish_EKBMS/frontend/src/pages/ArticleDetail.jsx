import { useEffect, useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import {
  getArticle, deleteArticle, submitArticle, decideArticle,
  rateArticle, toggleBookmark, listComments, listApprovalLogs,
} from '../services/articles.js'
import StarRating from '../components/StarRating.jsx'
import Comments from '../components/Comments.jsx'
import Attachments from '../components/Attachments.jsx'
import { useUser, hasRole } from '../services/UserContext.jsx'

export default function ArticleDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { currentUser } = useUser()

  const [article, setArticle] = useState(null)
  const [comments, setComments] = useState([])
  const [approvals, setApprovals] = useState([])
  const [bookmarked, setBookmarked] = useState(false)
  const [decisionComment, setDecisionComment] = useState('')
  const [error, setError] = useState(null)
  const [msg, setMsg] = useState(null)
  const [loading, setLoading] = useState(true)

  const reload = async () => {
    try {
      const [a, cs, ls] = await Promise.all([
        getArticle(id),
        listComments(id),
        listApprovalLogs(id),
      ])
      setArticle(a)
      setComments(cs)
      setApprovals(ls)
    } catch (e) {
      setError(e.friendlyMessage || e.message)
    }
  }

  useEffect(() => {
    setLoading(true)
    reload().finally(() => setLoading(false))
  }, [id])

  if (loading) return <div><span className="spinner" /> Loading article…</div>
  if (error && !article) return <div className="alert alert-error">{error}</div>
  if (!article) return null

  const canEdit = hasRole(currentUser, 'Admin') || (hasRole(currentUser, 'Author') && article.author_id === currentUser.id)
  const canDecide = hasRole(currentUser, 'Admin', 'Reviewer') && article.status === 'pending'
  const canSubmit = canEdit && (article.status === 'draft' || article.status === 'rejected')

  const handleDelete = async () => {
    if (!window.confirm('Delete this article?')) return
    try {
      await deleteArticle(article.id)
      navigate('/articles')
    } catch (e) { setError(e.friendlyMessage || e.message) }
  }

  const handleSubmit = async () => {
    try { await submitArticle(article.id); setMsg('Submitted for review.'); reload() }
    catch (e) { setError(e.friendlyMessage || e.message) }
  }

  const handleDecide = async (action) => {
    try { await decideArticle(article.id, action, decisionComment || null); setMsg(`Article ${action}.`); setDecisionComment(''); reload() }
    catch (e) { setError(e.friendlyMessage || e.message) }
  }

  const handleRate = async (stars) => {
    try { await rateArticle(article.id, stars); setMsg(`Thanks — rated ${stars}/5.`); reload() }
    catch (e) { setError(e.friendlyMessage || e.message) }
  }

  const handleBookmark = async () => {
    try {
      const r = await toggleBookmark(article.id)
      setBookmarked(!!r.bookmarked)
      setMsg(r.bookmarked ? 'Bookmarked.' : 'Bookmark removed.')
    } catch (e) { setError(e.friendlyMessage || e.message) }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 style={{ marginBottom: 4 }}>{article.title}</h1>
          <div className="article-aside">
            <span className={`status-pill status-${article.status}`}>{article.status}</span>
            <span>by <strong>{article.author_name}</strong></span>
            {article.category_name && <span>in <strong>{article.category_name}</strong></span>}
            <span>{article.view_count} views</span>
            <StarRating value={Math.round(article.average_rating)} readonly size="sm" />
            <span style={{ color: '#475569' }}>
              {article.average_rating} ({article.rating_count} {article.rating_count === 1 ? 'rating' : 'ratings'})
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button onClick={handleBookmark}>{bookmarked ? '★ Bookmarked' : '☆ Bookmark'}</button>
          {canEdit && <Link className="btn" to={`/articles/${article.id}/edit`}>Edit</Link>}
          {canSubmit && <button className="btn-primary" onClick={handleSubmit}>Submit for review</button>}
          {canEdit && <button className="btn-danger" onClick={handleDelete}>Delete</button>}
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}

      {!!article.tags?.length && (
        <div style={{ marginBottom: 16 }}>
          {article.tags.map((t) => <span className="tag" key={t.id}>#{t.name}</span>)}
        </div>
      )}

      <div className="card">
        <div className="article-body">{article.content}</div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Rate this article</h3>
        <StarRating value={0} onChange={handleRate} />
      </div>

      {canDecide && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3 style={{ marginTop: 0 }}>Review</h3>
          <div className="form-row">
            <label>Reviewer comment (optional)</label>
            <textarea
              value={decisionComment}
              onChange={(e) => setDecisionComment(e.target.value)}
              placeholder="Approve with notes, or explain rejection…"
              style={{ minHeight: 80 }}
            />
          </div>
          <div className="form-actions">
            <button className="btn-success" onClick={() => handleDecide('approved')}>Approve</button>
            <button className="btn-danger" onClick={() => handleDecide('rejected')}>Reject</button>
          </div>
        </div>
      )}

      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Attachments</h3>
        <Attachments
          articleId={article.id}
          attachments={article.attachments}
          onChange={(list) => setArticle((a) => ({ ...a, attachments: list }))}
          canEdit={canEdit}
        />
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <Comments articleId={article.id} comments={comments} onChange={setComments} />
      </div>

      {approvals.length > 0 && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3 style={{ marginTop: 0 }}>Approval history</h3>
          {approvals.map((l) => (
            <div className="comment" key={l.id}>
              <div className="comment-meta">
                <span>
                  <span className={`status-pill status-${l.action === 'approved' ? 'approved' : 'rejected'}`}>
                    {l.action}
                  </span>
                  {' by '}<strong>{l.reviewer_name}</strong> · {new Date(l.created_at).toLocaleString()}
                </span>
              </div>
              {l.comment && <div className="comment-body">{l.comment}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
