# Screenshot Capture Guide

Save PNGs to the top-level `screenshots/` folder. Suggested naming: `01_dashboard.png`, `02_articles_list.png`, etc. The rubric mentions UI screens, CRUD actions, search/filter, and Postman/API screens — the list below covers all four buckets.

## UI screens

| # | File | What to show |
| --- | --- | --- |
| 1 | `01_dashboard.png` | Dashboard with metric tiles (Total/Approved/Pending/Drafts/Active Users), Most Viewed and Recent grids |
| 2 | `02_articles_list.png` | `/articles` page with at least one filter active (e.g., status=approved or category=IT Support) |
| 3 | `03_article_detail.png` | An approved article detail page — status pill, tags, content, average rating, attachments, comments |
| 4 | `04_new_article_form.png` | `/new` — empty title showing the inline validation hint, or filled-out form ready to save |
| 5 | `05_approval_queue.png` | `/approvals` page (act as Reviewer) showing pending items |
| 6 | `06_categories_admin.png` | `/categories` showing the hierarchical tree + add/edit form (act as Admin) |
| 7 | `07_search_results.png` | `/search` with a query like "vpn" and 1+ results |
| 8 | `08_bookmarks.png` | `/bookmarks` page with at least one saved item |
| 9 | `09_role_switcher.png` | Topbar close-up showing the role badge + Acting-as dropdown open |

## CRUD operations (capture mid-flow)

| # | File | What to show |
| --- | --- | --- |
| 10 | `10_crud_create.png` | Filled-in New Article form, just before clicking Save |
| 11 | `11_crud_read.png` | Article detail page (same as #3 if convenient) |
| 12 | `12_crud_update.png` | `/articles/{id}/edit` with modified content |
| 13 | `13_crud_delete.png` | Browser confirm dialog for "Delete this article?" |
| 14 | `14_workflow_submit.png` | Author's draft article with the "Submit for review" button visible |
| 15 | `15_workflow_approve.png` | Reviewer's view of a pending article with Approve/Reject panel and reviewer-comment field |

## Search / filter

| # | File | What to show |
| --- | --- | --- |
| 16 | `16_filter_by_status.png` | `/articles?status=pending` (use the status dropdown) |
| 17 | `17_filter_by_category.png` | Articles list filtered to e.g. "IT Support" or its child "Networking" |
| 18 | `18_search_tag.png` | Either the `/search` page with `q=onboarding`, or `/articles?tag=vpn` |

## API testing (Postman or Swagger)

| # | File | What to show |
| --- | --- | --- |
| 19 | `19_postman_collection.png` | Postman sidebar showing the imported EKBMS collection |
| 20 | `20_postman_get_articles.png` | Postman response panel for `GET /articles` (200, JSON body visible) |
| 21 | `21_postman_post_article_201.png` | Postman response for `POST /articles` with status `201 Created` |
| 22 | `22_postman_422.png` | Postman response for an intentional 422 — easiest: `POST /articles` with `{"title": "ab", "content": ""}`, showing the `errors[]` array |
| 23 | `23_postman_403.png` | Postman response for `POST /articles` while sending `X-User-Id: 5` (Employee) — 403 |
| 24 | `24_swagger_ui.png` | `http://127.0.0.1:8000/docs` — Swagger landing page |

## Capture tips

- Use Windows **Snipping Tool** (`Win + Shift + S`) for region captures.
- Before each screenshot, switch the role to the most natural actor: Admin for categories/users, Author for create/submit, Reviewer for approvals, Employee for read/comment/rate/bookmark.
- For the Postman screenshots, set the `userId` collection variable to match the row you’re showing (1=Admin, 2/3=Author, 4=Reviewer, 5/6=Employee).
- Keep the browser zoom around 100% so text is readable in the README preview.
