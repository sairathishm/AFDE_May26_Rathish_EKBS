/**
 * Holds the "currently acting" user, which the backend reads from the
 * X-User-Id header to enforce role-based access. Persists across reloads
 * via localStorage. Wraps the app via UserProvider in main.jsx.
 */
import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../api'

const UserContext = createContext(null)

export function UserProvider({ children }) {
  const [users, setUsers] = useState([])
  const [currentUser, setCurrentUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api
      .get('/users')
      .then((r) => {
        setUsers(r.data)
        const storedId = parseInt(localStorage.getItem('ekbms_user_id') || '0', 10)
        const found = r.data.find((u) => u.id === storedId)
        const pick = found || r.data[0] || null
        if (pick) {
          localStorage.setItem('ekbms_user_id', String(pick.id))
          setCurrentUser(pick)
        }
      })
      .catch((e) => setError(e.friendlyMessage || e.message))
      .finally(() => setLoading(false))
  }, [])

  const switchUser = (userId) => {
    const u = users.find((x) => x.id === userId)
    if (u) {
      localStorage.setItem('ekbms_user_id', String(u.id))
      setCurrentUser(u)
    }
  }

  const value = { users, currentUser, switchUser, loading, error }
  return <UserContext.Provider value={value}>{children}</UserContext.Provider>
}

export function useUser() {
  const ctx = useContext(UserContext)
  if (!ctx) throw new Error('useUser must be used inside UserProvider')
  return ctx
}

export function hasRole(user, ...allowed) {
  if (!user) return false
  return allowed.map((r) => r.toLowerCase()).includes(user.role.name.toLowerCase())
}
