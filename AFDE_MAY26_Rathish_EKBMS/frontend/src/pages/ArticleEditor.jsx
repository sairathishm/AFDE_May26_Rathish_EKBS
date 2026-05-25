import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createArticle, getArticle, updateArticle, submitArticle } from '../services/articles.js'
import { listCategories } from '../services/categories.js'

export default function ArticleEditor({ mode }) {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', content: '', category_id: '', tag_names: '' })
  const [categories, setCategories] = useState([])
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(mode === 'edit')

  useEffect(() => { listCategories().then(setCategories).catch(() => {}) }, [])

  useEffect(() => {
    if (mode === 'edit' && id) {
      getArticle(id)
        .then((a) =>
          setForm({
            title: a.title,
            content: a.content,
            category_id: a.category_id || '',
            tag_names: (a.tags || []).map((t) => t.name).join(', '),
          })
        )
        .catch((e) => setError(e.friendlyMessage || e.message))
        .finally(() => setLoading(false))
    }
  }, [id, mode])

  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const validate = () => {
    if (form.title.trim().length < 3) return 'Title must be at least 3 characters.'
    if (!form.content.trim()) return 'Content cannot be empty.'
    return null
  }

  const submit = async (alsoSubmitForReview = false) => {
    const v = validate()
    if (v) { setError(v); return }
    setSaving(true); setError(null)
    const payload = {
      title: form.title.trim(),
      content: form.content,
      category_id: form.category_id ? parseInt(form.category_id, 10) : null,
      tag_names: form.tag_names
        ? form.tag_names.split(',').map((s) => s.trim()).filter(Boolean)
        : [],
    }
    try {
      const result = mode === 'edit'
        ? await updateArticle(id, payload)
        : await createArticle(payload)
      if (alsoSubmitForReview) {
        await submitArticle(result.id)
      }
      navigate(`/articles/${result.id}`)
    } catch (e) {
      setError(e.friendlyMessage || e.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div><span className="spinner" /> Loading…</div>

  return (
    <div>
      <div className="page-header">
        <h1>{mode === 'edit' ? 'Edit Article' : 'New Article'}</h1>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="card">
        <div className="form-row">
          <label>Title</label>
          <input
            value={form.title}
            onChange={(e) => update('title', e.target.value)}
            placeholder="e.g., How to reset your VPN password"
            maxLength={200}
          />
        </div>

        <div className="form-row">
          <label>Category</label>
          <select value={form.category_id} onChange={(e) => update('category_id', e.target.value)}>
            <option value="">— None —</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <label>Tags (comma-separated)</label>
          <input
            value={form.tag_names}
            onChange={(e) => update('tag_names', e.target.value)}
            placeholder="vpn, troubleshooting, sop"
          />
        </div>

        <div className="form-row">
          <label>Content</label>
          <textarea
            value={form.content}
            onChange={(e) => update('content', e.target.value)}
            placeholder="Write the article body here…"
          />
        </div>

        <div className="form-actions">
          <button className="btn-primary" disabled={saving} onClick={() => submit(false)}>
            {saving ? 'Saving…' : 'Save draft'}
          </button>
          <button className="btn-success" disabled={saving} onClick={() => submit(true)}>
            Save & submit for review
          </button>
          <button onClick={() => navigate(-1)}>Cancel</button>
        </div>
      </div>
    </div>
  )
}
