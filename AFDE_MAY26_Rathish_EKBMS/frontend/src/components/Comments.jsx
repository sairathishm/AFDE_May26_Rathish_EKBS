import { useState } from 'react'
import { addComment, deleteComment, listComments } from '../services/articles.js'
import { useUser, hasRole } from '../services/UserContext.jsx'

export default function Comments({ articleId, comments, onChange }) {
  const { currentUser } = useUser()
  const [body, setBody] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const refresh = async () => {
    const list = await listComments(articleId)
    onChange && onChange(list)
  }

  const handleAdd = async (e) => {
    e.preventDefault()
    setError(null)
    if (!body.trim()) return
    setSubmitting(true)
    try {
      await addComment(articleId, body.trim())
      setBody('')
      await refresh()
    } catch (err) {
      setError(err.friendlyMessage || err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (c) => {
    if (!window.confirm('Delete this comment?')) return
    try {
      await deleteComment(articleId, c.id)
      await refresh()
    } catch (err) {
      setError(err.friendlyMessage || err.message)
    }
  }

  return (
    <div>
      <h3 style={{ marginTop: 0 }}>Comments ({comments?.length || 0})</h3>
      {error && <div className="alert alert-error">{error}</div>}
      {(comments || []).map((c) => {
        const canDelete = currentUser && (c.user_id === currentUser.id || hasRole(currentUser, 'Admin'))
        return (
          <div className="comment" key={c.id}>
            <div className="comment-meta">
              <span><strong>{c.user_name || `User #${c.user_id}`}</strong> · {new Date(c.created_at).toLocaleString()}</span>
              {canDelete && <button className="btn-ghost" onClick={() => handleDelete(c)}>Delete</button>}
            </div>
            <div className="comment-body">{c.body}</div>
          </div>
        )
      })}
      {!comments?.length && <div className="empty" style={{ padding: 16 }}>No comments yet.</div>}

      <form onSubmit={handleAdd} style={{ marginTop: 16 }}>
        <div className="form-row">
          <label>Add a comment</label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Share an observation or correction…"
            maxLength={2000}
            style={{ minHeight: 80 }}
          />
        </div>
        <button className="btn-primary" disabled={submitting || !body.trim()}>
          {submitting ? 'Posting…' : 'Post comment'}
        </button>
      </form>
    </div>
  )
}
