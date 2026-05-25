/** Recursive category tree. Optionally fires onAction for edit/delete. */
export default function CategoryTree({ nodes, onAction }) {
  if (!nodes?.length) return <div className="empty">No categories yet.</div>
  return (
    <ul className="cat-tree">
      {nodes.map((n) => <CategoryNode key={n.id} node={n} onAction={onAction} />)}
    </ul>
  )
}

function CategoryNode({ node, onAction }) {
  return (
    <li>
      <div className="cat-node">
        <span className="cat-node-name">{node.name}</span>
        {onAction && (
          <span style={{ display: 'flex', gap: 6 }}>
            <button className="btn-ghost" onClick={() => onAction('edit', node)}>Edit</button>
            <button className="btn-ghost" onClick={() => onAction('delete', node)}>Delete</button>
          </span>
        )}
      </div>
      {!!node.children?.length && (
        <ul>
          {node.children.map((c) => (
            <CategoryNode key={c.id} node={c} onAction={onAction} />
          ))}
        </ul>
      )}
    </li>
  )
}
