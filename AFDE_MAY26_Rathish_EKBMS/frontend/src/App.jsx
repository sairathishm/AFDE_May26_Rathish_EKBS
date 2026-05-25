import { Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { useUser, hasRole } from './services/UserContext.jsx'
import RoleSwitcher from './components/RoleSwitcher.jsx'

import Dashboard from './pages/Dashboard.jsx'
import ArticlesList from './pages/ArticlesList.jsx'
import ArticleDetail from './pages/ArticleDetail.jsx'
import ArticleEditor from './pages/ArticleEditor.jsx'
import ApprovalsQueue from './pages/ApprovalsQueue.jsx'
import CategoriesAdmin from './pages/CategoriesAdmin.jsx'
import SearchPage from './pages/SearchPage.jsx'
import Bookmarks from './pages/Bookmarks.jsx'

export default function App() {
  const { currentUser, loading, error } = useUser()

  if (loading) {
    return (
      <div className="app-shell">
        <div className="page"><span className="spinner" /> Loading users…</div>
      </div>
    )
  }
  if (error) {
    return (
      <div className="app-shell">
        <div className="page">
          <div className="alert alert-error">
            Couldn’t reach the backend at <code>{import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}</code>.
            Start it with <code>py -m uvicorn backend.main:app --reload</code> from the project root. <br />
            Underlying error: <code>{error}</code>
          </div>
        </div>
      </div>
    )
  }

  const role = currentUser?.role?.name || 'Employee'
  const canAuthor = hasRole(currentUser, 'Admin', 'Author')
  const canReview = hasRole(currentUser, 'Admin', 'Reviewer')
  const isAdmin = hasRole(currentUser, 'Admin')

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">EKBMS</div>
        <nav className="nav">
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/articles">Articles</NavLink>
          <NavLink to="/search">Search</NavLink>
          {canAuthor && <NavLink to="/new">New Article</NavLink>}
          {canReview && <NavLink to="/approvals">Approvals</NavLink>}
          {isAdmin && <NavLink to="/categories">Categories</NavLink>}
          <NavLink to="/bookmarks">Bookmarks</NavLink>
        </nav>
        <RoleSwitcher />
      </header>

      <main className="page">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/articles" element={<ArticlesList />} />
          <Route path="/articles/:id" element={<ArticleDetail />} />
          <Route path="/articles/:id/edit" element={<ArticleEditor mode="edit" />} />
          <Route path="/new" element={<ArticleEditor mode="create" />} />
          <Route path="/approvals" element={<ApprovalsQueue />} />
          <Route path="/categories" element={<CategoriesAdmin />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/bookmarks" element={<Bookmarks />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <footer style={{ padding: '12px 24px', color: '#64748b', fontSize: '0.85rem' }}>
        EKBMS Phase 1 capstone &middot; Acting as <strong>{currentUser?.name}</strong> ({role})
      </footer>
    </div>
  )
}
