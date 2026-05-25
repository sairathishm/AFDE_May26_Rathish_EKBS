import { useState } from 'react'
import {
  listAttachments, uploadAttachment, deleteAttachment, downloadAttachmentUrl,
} from '../services/articles.js'

function fmtSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

export default function Attachments({ articleId, attachments, onChange, canEdit }) {
  const [error, setError] = useState(null)
  const [uploading, setUploading] = useState(false)

  const refresh = async () => {
    const list = await listAttachments(articleId)
    onChange && onChange(list)
  }

  const handleUpload = async (e) => {
    setError(null)
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      await uploadAttachment(articleId, file)
      await refresh()
    } catch (err) {
      setError(err.friendlyMessage || err.message)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleDelete = async (att) => {
    if (!window.confirm(`Delete ${att.file_name}?`)) return
    try {
      await deleteAttachment(articleId, att.id)
      await refresh()
    } catch (err) {
      setError(err.friendlyMessage || err.message)
    }
  }

  return (
    <div>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="attachment-list">
        {(attachments || []).map((a) => (
          <div className="attachment-row" key={a.id}>
            <span>
              📎{' '}
              <a href={downloadAttachmentUrl(articleId, a.id)} target="_blank" rel="noreferrer">
                {a.file_name}
              </a>
              <span style={{ color: '#64748b', marginLeft: 8, fontSize: '0.85rem' }}>
                ({fmtSize(a.size_bytes)})
              </span>
            </span>
            {canEdit && (
              <button className="btn-ghost" onClick={() => handleDelete(a)}>Delete</button>
            )}
          </div>
        ))}
        {!attachments?.length && <div className="empty" style={{ padding: 12 }}>No attachments yet.</div>}
      </div>
      {canEdit && (
        <div style={{ marginTop: 12 }}>
          <input type="file" onChange={handleUpload} disabled={uploading} />
          {uploading && <span style={{ marginLeft: 8 }}><span className="spinner" /> Uploading…</span>}
        </div>
      )}
    </div>
  )
}
