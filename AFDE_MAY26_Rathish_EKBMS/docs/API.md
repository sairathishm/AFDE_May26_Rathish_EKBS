# EKBMS API Reference

Base URL (local): `http://127.0.0.1:8000`
Interactive Swagger UI: `http://127.0.0.1:8000/docs`

## Conventions

- **Auth**: every request that *changes* data must include the header
  `X-User-Id: <user_id>`. The backend looks up the user, reads its role, and
  enforces role-based access.
- **Errors** follow this shape:
  - **422** validation: `{"detail": "Validation failed", "errors": [{"field": "...", "message": "..."}]}`
  - **401/403/404/409**: `{"detail": "<human-readable message>"}`
- **Statuses**: an article is always in one of `draft | pending | approved | rejected | archived`.
- **All curl examples assume bash quoting**; on PowerShell use double quotes for the JSON body or pipe from a file.

## Meta

### `GET /`

Returns the API name, version, and a quick endpoint index.

### `GET /health`

Returns `{"status": "ok"}`. Used by the smoke test and frontend bootstrap.

## Roles

### `GET /roles`

```bash
curl http://127.0.0.1:8000/roles
```

```json
[
  {"id": 1, "name": "Admin"},
  {"id": 2, "name": "Author"},
  {"id": 3, "name": "Reviewer"},
  {"id": 4, "name": "Employee"}
]
```

## Users

### `GET /users` &middot; `GET /users/{id}`

Lists all users (no auth required, useful for populating the role-switcher).

### `POST /users` &middot; Admin only

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 1" \
  -d '{"name": "New Author", "email": "new@ekbms.com", "role_id": 2}'
```

- `201 Created` on success
- `409 Conflict` if email already exists
- `422` if body fails validation

### `PUT /users/{id}` &middot; Admin only
### `DELETE /users/{id}` &middot; Admin only — `204 No Content`

## Categories (hierarchical)

### `GET /categories`

Flat list ordered by `parent_id` then `name`.

### `GET /categories/tree`

Same data nested as a tree:

```json
[
  {"id": 1, "name": "HR Policies", "parent_id": null, "children": [
    {"id": 6, "name": "Leave Policies", "parent_id": 1, "children": []},
    {"id": 7, "name": "Onboarding", "parent_id": 1, "children": []}
  ]}
]
```

### `POST /categories` &middot; Admin only

```bash
curl -X POST http://127.0.0.1:8000/categories \
  -H "Content-Type: application/json" -H "X-User-Id: 1" \
  -d '{"name": "Cloud", "parent_id": 2}'
```

### `PUT /categories/{id}` &middot; Admin only
### `DELETE /categories/{id}` &middot; Admin only — cascades to children & articles

## Tags

### `GET /tags`
### `POST /tags` &middot; Admin or Author

```bash
curl -X POST http://127.0.0.1:8000/tags \
  -H "Content-Type: application/json" -H "X-User-Id: 2" \
  -d '{"name": "wfh"}'
```

### `DELETE /tags/{id}` &middot; Admin

## Articles

### `GET /articles`

Filterable list. Query params:

| param | type | notes |
| --- | --- | --- |
| `status` | string | one of `draft pending approved rejected archived` |
| `category_id` | int | |
| `author_id` | int | |
| `tag` | string | tag name |
| `q` | string | substring match on title/content |
| `sort` | string | `recent` (default), `popular`, `oldest` |
| `limit` | int | default 50, max 200 |
| `offset` | int | default 0 |

### `GET /articles/{id}`

Returns the full article (incl. tags, attachments, view count, average rating). Side effect: increments `view_count` by 1.

### `POST /articles` &middot; Admin or Author

```bash
curl -X POST http://127.0.0.1:8000/articles \
  -H "Content-Type: application/json" -H "X-User-Id: 2" \
  -d '{
    "title": "Password Reset Guide",
    "content": "1. Visit portal.ekbms.com ...",
    "category_id": 2,
    "tag_names": ["security", "sop"]
  }'
```

- `201 Created`, body is the new article (status starts as `draft`)
- `422` if validation fails — example response:

```json
{
  "detail": "Validation failed",
  "errors": [
    {"field": "title", "message": "String should have at least 3 characters"}
  ]
}
```

### `PUT /articles/{id}` &middot; Admin or Author

Authors can only edit their own articles (`403` otherwise).

### `DELETE /articles/{id}` &middot; Admin or Author — `204`

## Article Lifecycle

### `POST /articles/{id}/submit` &middot; Author/Admin

Moves a `draft` (or previously `rejected`) article to `pending`.

### `POST /articles/{id}/decision` &middot; Reviewer/Admin

```bash
curl -X POST http://127.0.0.1:8000/articles/6/decision \
  -H "Content-Type: application/json" -H "X-User-Id: 4" \
  -d '{"action": "approved", "comment": "Verified on Windows 11."}'
```

`action` must be `approved` or `rejected`. Updates status and writes an `approval_logs` row.

### `GET /articles/{id}/approvals`

Returns the audit log for an article — `[{id, reviewer_id, reviewer_name, action, comment, created_at}, ...]`.

### `PUT /articles/{id}/status` &middot; Admin

Manual override; useful for archiving:

```bash
curl -X PUT http://127.0.0.1:8000/articles/3/status \
  -H "Content-Type: application/json" -H "X-User-Id: 1" \
  -d '{"status": "archived"}'
```

## Attachments

Supported types: PDF, DOC/DOCX, PPT/PPTX, XLS/XLSX, PNG, JPG/JPEG, TXT, MD. Max 10 MB.

### `POST /articles/{id}/attachments` &middot; Author/Admin (own articles)

Multipart upload:

```bash
curl -X POST http://127.0.0.1:8000/articles/3/attachments \
  -H "X-User-Id: 3" \
  -F "file=@./vpn-setup.pdf"
```

- `201` with file metadata
- `400` if extension not allowed
- `413` if file > 10 MB

### `GET /articles/{id}/attachments`
### `GET /articles/{id}/attachments/{att_id}/download`
### `DELETE /articles/{id}/attachments/{att_id}` &middot; Author/Admin

## Comments

### `GET /articles/{id}/comments`
### `POST /articles/{id}/comments`

```bash
curl -X POST http://127.0.0.1:8000/articles/3/comments \
  -H "Content-Type: application/json" -H "X-User-Id: 5" \
  -d '{"body": "Worked perfectly. Thanks!"}'
```

### `DELETE /articles/{id}/comments/{cid}`

Comment owner or Admin only.

## Ratings

### `POST /articles/{id}/ratings`

```bash
curl -X POST http://127.0.0.1:8000/articles/3/ratings \
  -H "Content-Type: application/json" -H "X-User-Id: 5" \
  -d '{"stars": 5}'
```

- `stars` must be 1-5 inclusive (else 422)
- Subsequent calls *update* the existing rating (one per user/article)

## Bookmarks

### `POST /articles/{id}/bookmark`

Toggle. Returns `{"bookmarked": true, "bookmark_id": ...}` or `{"bookmarked": false}`.

### `GET /search/bookmarks?user_id=5`

A user's bookmarked articles, as article list items.

## Search

### `GET /search?q=vpn`

Full-text across title, content, and tag names. Returns up to `limit` (default 25, max 100) results sorted by recency.

## Dashboard

### `GET /dashboard`

```json
{
  "total_articles": 8,
  "approved_articles": 5,
  "pending_approvals": 2,
  "draft_articles": 1,
  "active_users": 6,
  "most_viewed": [ ... up to 5 ArticleListItems ... ],
  "recent": [ ... up to 5 ArticleListItems ... ]
}
```

## Status Code Reference

| Code | Used when |
| --- | --- |
| 200 | Success (GET/PUT/POST without resource creation) |
| 201 | New resource created |
| 204 | Successful DELETE (empty body) |
| 400 | Domain rule broken (e.g., bad file extension, illegal status transition) |
| 401 | Missing or invalid `X-User-Id` |
| 403 | Authenticated user lacks the required role |
| 404 | Resource not found |
| 409 | DB integrity / duplicate (e.g., user email already taken) |
| 413 | Upload too large |
| 422 | Body/query fails Pydantic validation |
