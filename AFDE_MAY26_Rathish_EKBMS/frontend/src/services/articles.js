/** Article + lifecycle + collaboration service. */
import { api } from '../api'

export const listArticles = (params = {}) =>
  api.get('/articles', { params }).then((r) => r.data)

export const getArticle = (id) =>
  api.get(`/articles/${id}`).then((r) => r.data)

export const createArticle = (body) =>
  api.post('/articles', body).then((r) => r.data)

export const updateArticle = (id, body) =>
  api.put(`/articles/${id}`, body).then((r) => r.data)

export const deleteArticle = (id) =>
  api.delete(`/articles/${id}`)

export const submitArticle = (id) =>
  api.post(`/articles/${id}/submit`).then((r) => r.data)

export const decideArticle = (id, action, comment) =>
  api.post(`/articles/${id}/decision`, { action, comment }).then((r) => r.data)

export const listApprovalLogs = (id) =>
  api.get(`/articles/${id}/approvals`).then((r) => r.data)

export const listComments = (id) =>
  api.get(`/articles/${id}/comments`).then((r) => r.data)

export const addComment = (id, body) =>
  api.post(`/articles/${id}/comments`, { body }).then((r) => r.data)

export const deleteComment = (articleId, commentId) =>
  api.delete(`/articles/${articleId}/comments/${commentId}`)

export const rateArticle = (id, stars) =>
  api.post(`/articles/${id}/ratings`, { stars }).then((r) => r.data)

export const toggleBookmark = (id) =>
  api.post(`/articles/${id}/bookmark`).then((r) => r.data)

export const listAttachments = (id) =>
  api.get(`/articles/${id}/attachments`).then((r) => r.data)

export const uploadAttachment = (id, file) => {
  const form = new FormData()
  form.append('file', file)
  return api
    .post(`/articles/${id}/attachments`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data)
}

export const deleteAttachment = (articleId, attId) =>
  api.delete(`/articles/${articleId}/attachments/${attId}`)

export const downloadAttachmentUrl = (articleId, attId) => {
  const base = api.defaults.baseURL
  return `${base}/articles/${articleId}/attachments/${attId}/download`
}

export const searchArticles = (q) =>
  api.get('/search', { params: { q } }).then((r) => r.data)

export const listBookmarks = (userId) =>
  api.get('/search/bookmarks', { params: { user_id: userId } }).then((r) => r.data)
