# Enterprise Knowledge Base Management System (EKBMS)

**Capstone Phase 1** &middot; Batch: AFDE Jan 26 &middot; Participant: Sharath &middot; Code: **EKBMS**

A centralized web platform for creating, categorizing, approving, and searching enterprise knowledge articles — HR policies, IT troubleshooting guides, SOPs, onboarding materials, and similar. Designed for four user roles (Admin, Author, Reviewer, Employee) with a full draft → review → publish lifecycle, hierarchical categories, tagging, file attachments, comments, ratings, and bookmarks.

## Table of Contents

- [Features Implemented](#features-implemented)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Running the App](#running-the-app)
- [Seed Users (for the role switcher)](#seed-users-for-the-role-switcher)
- [API Overview](#api-overview)
- [Smoke Test](#smoke-test)
- [Screenshots](#screenshots)
- [Notes on the Auth Model](#notes-on-the-auth-model)

## Features Implemented

| Module | Highlights |
| --- | --- |
| **User & Role Management** | 4 seeded roles, in-app role switcher (X-User-Id header), Admin can CRUD users |
| **Knowledge Articles** | Create, edit, delete, view-count tracking, status lifecycle |
| **Approval Workflow** | Draft → Pending → Approved/Rejected → (Archived). Reviewer comments stored as audit log |
| **Categories** | Hierarchical (parent/child), tree view, Admin CRUD |
| **Tags** | Free-form, many-to-many with articles, used in filters and search |
| **Search** | Full-text across title/content/tags + filters by status, category, author, tag, sort |
| **File Attachments** | PDF/DOC/PPT/XLS/PNG/JPG/TXT/MD, 10 MB limit, extension validation |
| **Comments** | Threaded list, delete-own (Admin can delete any) |
| **Ratings** | 1-5 stars, one rating per user/article, average shown on detail and cards |
| **Bookmarks** | Toggle per article, dedicated Bookmarks page |
| **Dashboard** | Totals + status counters + most viewed + recent activity |
| **Error Handling** | Custom 422 payload (`{detail, errors:[{field,message}]}`), 401/403/404/409 with helpful messages |

## Technology Stack

| Layer | Choice |
| --- | --- |
| Frontend | React 18 + Vite, React Router, axios, plain CSS |
| Backend | FastAPI (Python 3.14 friendly), SQLAlchemy 2.x, Pydantic v2 |
| Database | SQLite (file-based, zero config) |
| Tooling | Postman collection, end-to-end smoke test, PowerShell launchers |

## Project Structure

```
AFDE_Jan26_Sharath_EKBMS/
├── backend/
│   ├── __init__.py
│   ├── main.py             FastAPI app, CORS, exception handlers
│   ├── db.py               SQLAlchemy engine + Base + get_db
│   ├── models.py           ORM models
│   ├── schemas.py          Pydantic v2 schemas (Create/Update/Out)
│   ├── crud.py             All DB-touching logic
│   ├── deps.py             current_user / require_roles dependencies
│   ├── seed.py             Idempotent seed script
│   ├── smoke_test.py       49-check end-to-end smoke test
│   ├── uploads/            Where uploaded attachments are stored
│   └── routers/
│       ├── users.py        Users + Roles
│       ├── categories.py   Hierarchical categories
│       ├── tags.py         Tag CRUD
│       ├── articles.py     CRUD + lifecycle + comments + ratings + attachments
│       ├── search.py       /search + /search/bookmarks
│       └── dashboard.py    /dashboard aggregates
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── api.js
│       ├── styles.css
│       ├── components/
│       ├── pages/
│       └── services/
├── database/
│   └── schema.sql          CREATE TABLE + indexes + seed data
├── docs/
│   ├── API.md
│   ├── EKBMS.postman_collection.json
│   ├── SCREENSHOTS.md
│   └── COMMIT_PLAN.md
├── screenshots/
├── start_backend.ps1
├── start_frontend.ps1
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

### Backend

```powershell
cd C:\Users\sharathbabu.gv\Downloads\AFDE_Jan26_Sharath_EKBMS
py -m pip install -r requirements.txt
```

### Frontend

PowerShell-only environment (cmd is disabled), so:

```powershell
npm config set script-shell "powershell.exe"   # one-time
cd C:\Users\sharathbabu.gv\Downloads\AFDE_Jan26_Sharath_EKBMS\frontend
npm install
```

### Database

SQLite is file-based; nothing to install. The backend auto-creates the schema on startup via `Base.metadata.create_all`. To seed sample data, either:

- Run the included seed script: `py -m backend.seed`
- Or apply `database/schema.sql` directly: `sqlite3 database\ekbms.db < database\schema.sql`

## Running the App

Easiest path — use the PowerShell launchers from the repo root:

```powershell
# Terminal 1 — backend
.\start_backend.ps1
# installs deps, seeds DB, starts http://127.0.0.1:8000

# Terminal 2 — frontend
.\start_frontend.ps1
# installs deps, starts http://localhost:5173
```

Manual equivalents:

```powershell
py -m uvicorn backend.main:app --reload          # backend
cd frontend; npm run dev                          # frontend
```

Open the app at <http://localhost:5173>. Swagger docs live at <http://127.0.0.1:8000/docs>.

## Seed Users (for the role switcher)

| Role | Name | Email |
| --- | --- | --- |
| Admin | Aarav Admin | admin@ekbms.com |
| Author | Priya Author | priya.author@ekbms.com |
| Author | Rohan Author | rohan.author@ekbms.com |
| Reviewer | Neha Reviewer | neha.reviewer@ekbms.com |
| Employee | Vikram Employee | vikram@ekbms.com |
| Employee | Sneha Employee | sneha@ekbms.com |

The top-right dropdown switches which user the frontend acts as; the backend reads the `X-User-Id` header and enforces role checks.

## API Overview

Full reference with request/response examples is in [`docs/API.md`](docs/API.md). Postman collection in [`docs/EKBMS.postman_collection.json`](docs/EKBMS.postman_collection.json).

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| GET | `/roles` | List roles |
| GET, POST, PUT, DELETE | `/users[/{id}]` | User CRUD (POST/PUT/DELETE: Admin only) |
| GET, POST, PUT, DELETE | `/categories[/{id}]` | Category CRUD; POST/PUT/DELETE: Admin only |
| GET | `/categories/tree` | Hierarchical view |
| GET, POST, DELETE | `/tags[/{id}]` | Tag listing & management |
| GET, POST, PUT, DELETE | `/articles[/{id}]` | Article CRUD |
| POST | `/articles/{id}/submit` | Submit draft for review |
| POST | `/articles/{id}/decision` | Approve / reject (Reviewer/Admin) |
| PUT | `/articles/{id}/status` | Manual status override (Admin) |
| GET | `/articles/{id}/approvals` | Approval audit log |
| GET, POST, DELETE | `/articles/{id}/attachments[/{att_id}]` | File attachments |
| GET | `/articles/{id}/attachments/{att_id}/download` | Stream file |
| GET, POST, DELETE | `/articles/{id}/comments[/{cid}]` | Comments |
| POST | `/articles/{id}/ratings` | Rate (1-5) |
| POST | `/articles/{id}/bookmark` | Toggle bookmark |
| GET | `/search?q=...` | Full-text search across title/content/tags |
| GET | `/search/bookmarks?user_id=...` | A user's bookmarked articles |
| GET | `/dashboard` | Aggregate counters + most viewed + recent |

## Smoke Test

`backend/smoke_test.py` hits every endpoint with positive cases, role-gating cases, and validation/404 cases. With the backend running:

```powershell
cd C:\Users\sharathbabu.gv\Downloads\AFDE_Jan26_Sharath_EKBMS\backend
py smoke_test.py
```

Current result: **49 / 49 passing.**

## Screenshots

See [`docs/SCREENSHOTS.md`](docs/SCREENSHOTS.md) for the capture checklist. PNGs live in `screenshots/`.

## Notes on the Auth Model

To keep Phase 1 scope sane, EKBMS uses a "role switcher" instead of full JWT login: every API call carries an `X-User-Id` header, and the backend looks the user up and enforces their role. This still demonstrates real RBAC at the route level (Author cannot manage users, Employee cannot approve articles, etc.) without burning a day on bcrypt + JWT plumbing. The model is documented as a deliberate scope choice; replacing it with real login is a clean, isolated change to `deps.py` and the frontend `UserContext`.
