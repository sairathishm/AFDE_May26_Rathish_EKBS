import { Link } from 'react-router-dom'
import StarRating from './StarRating.jsx'

export default function ArticleCard({ article }) {
  const updated = new Date(article.updated_at).toLocaleDateString()
  return (
    <div className="article-card">
      <h3><Link to={`/articles/${article.id}`}>{article.title}</Link></h3>
      <div>
        <span className={`status-pill status-${article.status}`}>{article.status}</span>
        {article.category_name && (
          <span style={{ marginLeft: 8, fontSize: '0.8rem', color: '#475569' }}>
            in <strong>{article.category_name}</strong>
          </span>
        )}
      </div>
      <div className="article-card-meta">
        <span>by {article.author_name || `User #${article.author_id}`}</span>
        <span>updated {updated}</span>
        <span>{article.view_count ?? 0} views</span>
      </div>
      {!!article.tags?.length && (
        <div>
          {article.tags.map((t) => <span className="tag" key={t.id}>#{t.name}</span>)}
        </div>
      )}
      {!!article.average_rating && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <StarRating value={Math.round(article.average_rating)} readonly size="sm" />
          <span style={{ fontSize: '0.8rem', color: '#475569' }}>{article.average_rating}</span>
        </div>
      )}
    </div>
  )
}
