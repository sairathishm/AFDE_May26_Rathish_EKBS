/**
 * Axios instance shared by every service file.
 *
 * - Reads the API URL from VITE_API_URL (.env)
 * - Attaches X-User-Id from localStorage on every request (simple role-switcher
 *   auth — see services/UserContext.jsx)
 */
import axios from 'axios'

export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const userId = localStorage.getItem('ekbms_user_id')
  if (userId) {
    config.headers['X-User-Id'] = userId
  }
  return config
})

api.interceptors.response.use(
  (resp) => resp,
  (err) => {
    // Normalize FastAPI validation errors into a single human-readable string
    if (err.response && err.response.data) {
      const data = err.response.data
      if (Array.isArray(data.errors) && data.errors.length) {
        err.friendlyMessage = data.errors.map((e) => `${e.field}: ${e.message}`).join('; ')
      } else if (typeof data.detail === 'string') {
        err.friendlyMessage = data.detail
      } else if (Array.isArray(data.detail)) {
        err.friendlyMessage = data.detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
      }
    }
    return Promise.reject(err)
  }
)
