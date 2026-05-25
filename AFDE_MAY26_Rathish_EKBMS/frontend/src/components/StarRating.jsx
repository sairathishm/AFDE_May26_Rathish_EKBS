export default function StarRating({ value = 0, onChange, readonly = false, size = 'md' }) {
  const stars = [1, 2, 3, 4, 5]
  const fontSize = size === 'sm' ? '0.95rem' : '1.1rem'
  return (
    <span className="star-rating" style={{ fontSize }} role="img" aria-label={`${value} of 5 stars`}>
      {stars.map((s) => (
        <span
          key={s}
          className={`star ${s <= value ? 'filled' : ''} ${readonly ? 'readonly' : ''}`}
          onClick={() => !readonly && onChange && onChange(s)}
        >
          {s <= value ? '★' : '☆'}
        </span>
      ))}
    </span>
  )
}
