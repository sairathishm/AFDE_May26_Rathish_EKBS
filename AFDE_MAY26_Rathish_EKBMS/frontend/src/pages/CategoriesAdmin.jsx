import { useEffect, useState } from 'react'
import {
  listCategories, getCategoryTree, createCategory, updateCategory, deleteCategory,
} from '../services/categories.js'
import CategoryTree from '../components/CategoryTree.jsx'

export default function CategoriesAdmin() {
  const [flat, setFlat] = useState([])
  const [tree, setTree] = useState([])
  const [form, setForm] = useState({ name: '', parent_id: '' })
  const [editing, setEditing] = useState(null)
  const [error, setError] = useState(null)
  const [msg, setMsg] = useState(null)

  const reload = async () => {
    const [f, t] = await Promise.all([listCategories(), getCategoryTree()])
    setFlat(f); setTree(t)
  }

  useEffect(() => { reload().catch((e) => setError(e.friendlyMessage || e.message)) }, [])

  const submit = async (e) => {
    e.preventDefault()
    setError(null); setMsg(null)
    if (!form.name.trim()) { setError('Name is required.'); return }
    try {
      const payload = {
        name: form.name.trim(),
        parent_id: form.parent_id ? parseInt(form.parent_id, 10) : null,
      }
      if (editing) {
        await updateCategory(editing.id, payload)
        setMsg(`Updated "${payload.name}".`)
        setEditing(null)
      } else {
        await createCategory(payload)
        setMsg(`Created "${payload.name}".`)
      }
      setForm({ name: '', parent_id: '' })
      await reload()
    } catch (e) { setError(e.friendlyMessage || e.message) }
  }

  const onAction = async (action, node) => {
    setError(null); setMsg(null)
    if (action === 'edit') {
      setEditing(node)
      setForm({ name: node.name, parent_id: node.parent_id || '' })
    } else if (action === 'delete') {
      if (!window.confirm(`Delete "${node.name}"? This also removes any sub-categories.`)) return
      try { await deleteCategory(node.id); setMsg(`Deleted "${node.name}".`); await reload() }
      catch (e) { setError(e.friendlyMessage || e.message) }
    }
  }

  return (
    <div>
      <div className="page-header"><h1>Manage Categories</h1></div>

      {error && <div className="alert alert-error">{error}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}

      <div className="card">
        <form onSubmit={submit}>
          <h3 style={{ marginTop: 0 }}>{editing ? `Edit "${editing.name}"` : 'Add category'}</h3>
          <div className="form-row">
            <label>Name</label>
            <input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="e.g., Onboarding"
            />
          </div>
          <div className="form-row">
            <label>Parent category</label>
            <select
              value={form.parent_id}
              onChange={(e) => setForm((f) => ({ ...f, parent_id: e.target.value }))}
            >
              <option value="">— None (top-level) —</option>
              {flat
                .filter((c) => !editing || c.id !== editing.id)
                .map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
            </select>
          </div>
          <div className="form-actions">
            <button className="btn-primary" type="submit">{editing ? 'Save changes' : 'Create'}</button>
            {editing && (
              <button type="button" onClick={() => { setEditing(null); setForm({ name: '', parent_id: '' }) }}>
                Cancel edit
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Tree</h3>
        <CategoryTree nodes={tree} onAction={onAction} />
      </div>
    </div>
  )
}
