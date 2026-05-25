import { useUser } from '../services/UserContext.jsx'

export default function RoleSwitcher() {
  const { users, currentUser, switchUser } = useUser()
  if (!currentUser) return null

  return (
    <div className="role-switcher">
      <span className="role-badge">{currentUser.role.name}</span>
      <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        Acting as:
        <select
          value={currentUser.id}
          onChange={(e) => switchUser(parseInt(e.target.value, 10))}
        >
          {users.map((u) => (
            <option key={u.id} value={u.id}>
              {u.name} — {u.role.name}
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}
