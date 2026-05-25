# 3-Day Commit Plan

The instructions explicitly penalize last-day bulk uploads, so the goal is **steady, dated commits** that line up with the rubric. Conventional Commits style (`feat:`, `fix:`, `docs:`, `chore:`, `test:`) keeps history scannable.

## Day 1 — Database & Backend

| Order | Suggested message |
| --- | --- |
| 1 | `chore: bootstrap repo structure (backend, frontend, database, docs, screenshots)` |
| 2 | `feat(backend): add db.py, models, schemas for users/roles/categories/tags/articles` |
| 3 | `feat(backend): add CRUD layer with hierarchical category tree and article filters` |
| 4 | `feat(backend): wire FastAPI app with CORS, custom 422 handler, role-based deps` |
| 5 | `feat(backend): article CRUD + lifecycle (submit/approve/reject) routes` |
| 6 | `feat(backend): attachments, comments, ratings, bookmarks endpoints` |
| 7 | `feat(backend): /search and /dashboard routes` |
| 8 | `feat(db): schema.sql with indexes and idempotent seed data` |
| 9 | `test(backend): end-to-end smoke test covering 49 cases` |
| 10 | `docs: initial README, API.md, Postman collection` |

End-of-day verify: `py -m uvicorn backend.main:app --reload` runs, `py smoke_test.py` is green.

## Day 2 — Frontend & Integration

| Order | Suggested message |
| --- | --- |
| 1 | `feat(frontend): Vite + React scaffold, axios api.js, UserContext role switcher` |
| 2 | `feat(frontend): global styles + topbar nav + role switcher component` |
| 3 | `feat(frontend): dashboard page with metric tiles + most-viewed + recent grids` |
| 4 | `feat(frontend): articles list with status/category/tag/sort filters` |
| 5 | `feat(frontend): article detail with rating, bookmark, approval, attachments, comments` |
| 6 | `feat(frontend): article editor (create + edit) with validation` |
| 7 | `feat(frontend): approvals queue page (Reviewer)` |
| 8 | `feat(frontend): hierarchical categories admin page` |
| 9 | `feat(frontend): search page and bookmarks page` |
| 10 | `chore: PowerShell launcher scripts for backend and frontend` |

End-of-day verify: `npm run build` succeeds, clicking through every page works against the running backend.

## Day 3 — Polish, Docs, Submission

| Order | Suggested message |
| --- | --- |
| 1 | `fix(backend): tighten validation messages and 422 error shape` (only if needed) |
| 2 | `docs: complete API reference with curl examples` |
| 3 | `docs: screenshot capture guide` |
| 4 | `chore: add screenshots/*.png for all 24 capture points` |
| 5 | `docs: finalize README with run instructions, seed users, and notes on auth model` |
| 6 | `test: re-run smoke test, confirm 49/49 passing` |
| 7 | `chore: final repo cleanup, .gitignore, requirements.txt` |
| 8 | `chore: submission tag v1.0` (optional `git tag v1.0`) |

## Tips

- Use `git add -p` to make commits semantically clean rather than dumping every change at once.
- Run `git log --oneline` at the end of each day to confirm the trail looks intentional.
- If a fix touches multiple modules, split it: one commit per concern (backend fix vs frontend integration vs doc tweak) reads much better than one large omnibus commit.
- A single tag (`git tag v1.0 && git push --tags`) at the very end gives the evaluator a fixed "this is the submission" anchor.
