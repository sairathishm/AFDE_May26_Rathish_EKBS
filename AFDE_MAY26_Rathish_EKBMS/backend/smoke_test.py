"""End-to-end smoke test against a running EKBMS backend.

Usage (with the backend running):
    cd backend
    py smoke_test.py

Exits 0 if every check passes, 1 otherwise. Prints a tidy [PASS]/[FAIL] line
per check so it's easy to spot what broke.
"""
import sys
import time
from io import BytesIO
import requests

BASE = "http://127.0.0.1:8000"

PASS = "\033[32m[PASS]\033[0m"
FAIL = "\033[31m[FAIL]\033[0m"
INFO = "\033[36m[INFO]\033[0m"

passes = 0
fails = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global passes, fails
    if condition:
        passes += 1
        print(f"{PASS} {label}")
    else:
        fails += 1
        print(f"{FAIL} {label}  {detail}")


def hdr(uid: int) -> dict:
    return {"X-User-Id": str(uid)}


def main() -> int:
    print(f"{INFO} Pinging {BASE} ...")
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        check("GET /health -> 200", r.status_code == 200, f"got {r.status_code}")
    except requests.RequestException as e:
        print(f"{FAIL} Backend not reachable at {BASE}: {e}")
        print("Start it first:  py -m uvicorn backend.main:app --reload")
        return 1

    # --- Roles & users ---
    r = requests.get(f"{BASE}/roles")
    check("GET /roles -> 200", r.status_code == 200)
    roles = {x["name"]: x["id"] for x in r.json()}
    check("All 4 roles present", set(roles) >= {"Admin", "Author", "Reviewer", "Employee"},
          f"got {list(roles)}")

    r = requests.get(f"{BASE}/users")
    check("GET /users -> 200", r.status_code == 200)
    users = r.json()
    by_role = {u["role"]["name"]: u for u in users}
    check("Has Admin user", "Admin" in by_role)
    check("Has Author user", "Author" in by_role)
    check("Has Reviewer user", "Reviewer" in by_role)
    check("Has Employee user", "Employee" in by_role)

    admin_id    = by_role["Admin"]["id"]
    author_id   = by_role["Author"]["id"]
    reviewer_id = by_role["Reviewer"]["id"]
    employee_id = by_role["Employee"]["id"]

    # --- Auth gating ---
    r = requests.post(f"{BASE}/articles", json={"title": "Nope", "content": "x"})
    check("POST /articles without X-User-Id -> 401", r.status_code == 401)

    r = requests.post(
        f"{BASE}/articles",
        json={"title": "Should fail", "content": "x"},
        headers=hdr(employee_id),
    )
    check("Employee POST /articles -> 403", r.status_code == 403)

    # --- Validation (422) ---
    r = requests.post(
        f"{BASE}/articles",
        json={"title": "ab", "content": ""},
        headers=hdr(author_id),
    )
    check("POST /articles short title -> 422", r.status_code == 422)
    if r.status_code == 422:
        body = r.json()
        check("422 payload has 'errors' list",
              isinstance(body.get("errors"), list) and len(body["errors"]) > 0,
              f"got {body}")

    # --- Categories ---
    r = requests.get(f"{BASE}/categories")
    check("GET /categories -> 200", r.status_code == 200)
    cats = r.json()
    check("At least 5 seeded categories", len(cats) >= 5, f"got {len(cats)}")

    r = requests.get(f"{BASE}/categories/tree")
    check("GET /categories/tree -> 200", r.status_code == 200)
    tree = r.json()
    has_children = any(node["children"] for node in tree)
    check("Tree shows nested children", has_children)

    # Admin creates a category
    new_cat_name = f"SmokeCat-{int(time.time())}"
    r = requests.post(
        f"{BASE}/categories",
        json={"name": new_cat_name},
        headers=hdr(admin_id),
    )
    check("Admin POST /categories -> 201", r.status_code == 201)
    new_cat_id = r.json()["id"] if r.status_code == 201 else None

    # Author cannot create category
    r = requests.post(
        f"{BASE}/categories",
        json={"name": "AuthorTry"},
        headers=hdr(author_id),
    )
    check("Author POST /categories -> 403", r.status_code == 403)

    # --- Article create / read / update / search ---
    create_payload = {
        "title": f"Smoke Test Article {int(time.time())}",
        "content": "This article was created by the smoke test.",
        "category_id": new_cat_id,
        "tag_names": ["smoke", "automated"],
    }
    r = requests.post(f"{BASE}/articles", json=create_payload, headers=hdr(author_id))
    check("Author POST /articles -> 201", r.status_code == 201)
    if r.status_code != 201:
        print(f"  detail: {r.text}")
        return 1
    article = r.json()
    aid = article["id"]
    check("Article starts in draft", article["status"] == "draft")
    check("Tags created via tag_names", len(article["tags"]) == 2)

    r = requests.get(f"{BASE}/articles/{aid}")
    check("GET /articles/{id} -> 200", r.status_code == 200)
    check("View count incremented on read", r.json()["view_count"] >= 1)

    r = requests.put(
        f"{BASE}/articles/{aid}",
        json={"content": "Updated by smoke test."},
        headers=hdr(author_id),
    )
    check("PUT /articles/{id} -> 200", r.status_code == 200)
    check("Content actually updated", r.json()["content"] == "Updated by smoke test.")

    r = requests.get(f"{BASE}/articles/{aid + 99999}")
    check("GET /articles/{missing} -> 404", r.status_code == 404)

    r = requests.get(f"{BASE}/articles", params={"q": "Smoke Test Article"})
    check("GET /articles?q= -> 200 + finds it",
          r.status_code == 200 and any(a["id"] == aid for a in r.json()))

    r = requests.get(f"{BASE}/search", params={"q": "Smoke"})
    check("GET /search?q= -> 200 + finds it",
          r.status_code == 200 and any(a["id"] == aid for a in r.json()))

    # --- Approval workflow ---
    r = requests.post(f"{BASE}/articles/{aid}/submit", headers=hdr(author_id))
    check("POST /articles/{id}/submit -> 200", r.status_code == 200)
    check("Status now 'pending'", r.json()["status"] == "pending")

    # Employee cannot decide
    r = requests.post(
        f"{BASE}/articles/{aid}/decision",
        json={"action": "approved"},
        headers=hdr(employee_id),
    )
    check("Employee POST /decision -> 403", r.status_code == 403)

    # Reviewer approves
    r = requests.post(
        f"{BASE}/articles/{aid}/decision",
        json={"action": "approved", "comment": "Looks good."},
        headers=hdr(reviewer_id),
    )
    check("Reviewer POST /decision -> 200", r.status_code == 200)

    r = requests.get(f"{BASE}/articles/{aid}")
    check("Article now 'approved'", r.status_code == 200 and r.json()["status"] == "approved")

    r = requests.get(f"{BASE}/articles/{aid}/approvals")
    check("GET /articles/{id}/approvals -> 200 with 1+ logs",
          r.status_code == 200 and len(r.json()) >= 1)

    # --- Comments ---
    r = requests.post(
        f"{BASE}/articles/{aid}/comments",
        json={"body": "Nice article."},
        headers=hdr(employee_id),
    )
    check("POST comment -> 201", r.status_code == 201)
    cid = r.json().get("id") if r.status_code == 201 else None

    r = requests.get(f"{BASE}/articles/{aid}/comments")
    check("GET comments -> 200", r.status_code == 200 and len(r.json()) >= 1)

    # --- Ratings ---
    r = requests.post(
        f"{BASE}/articles/{aid}/ratings",
        json={"stars": 5},
        headers=hdr(employee_id),
    )
    check("POST rating 5 -> 201", r.status_code == 201)

    r = requests.post(
        f"{BASE}/articles/{aid}/ratings",
        json={"stars": 7},
        headers=hdr(employee_id),
    )
    check("POST rating invalid stars -> 422", r.status_code == 422)

    # --- Bookmarks (toggle) ---
    r = requests.post(f"{BASE}/articles/{aid}/bookmark", headers=hdr(employee_id))
    check("POST bookmark (add) -> 200 + bookmarked=True",
          r.status_code == 200 and r.json().get("bookmarked") is True)

    r = requests.post(f"{BASE}/articles/{aid}/bookmark", headers=hdr(employee_id))
    check("POST bookmark (toggle off) -> 200 + bookmarked=False",
          r.status_code == 200 and r.json().get("bookmarked") is False)

    # --- Attachments ---
    files = {"file": ("note.txt", BytesIO(b"hello smoke test"), "text/plain")}
    r = requests.post(
        f"{BASE}/articles/{aid}/attachments",
        files=files,
        headers=hdr(author_id),
    )
    check("POST attachment -> 201", r.status_code == 201)
    att_id = r.json().get("id") if r.status_code == 201 else None

    # Bad extension is rejected
    files = {"file": ("evil.exe", BytesIO(b"MZ"), "application/octet-stream")}
    r = requests.post(
        f"{BASE}/articles/{aid}/attachments",
        files=files,
        headers=hdr(author_id),
    )
    check("POST attachment bad ext -> 400", r.status_code == 400)

    if att_id:
        r = requests.get(f"{BASE}/articles/{aid}/attachments/{att_id}/download")
        check("GET attachment download -> 200", r.status_code == 200)
        check("Download content matches", r.content == b"hello smoke test")

    # --- Dashboard ---
    r = requests.get(f"{BASE}/dashboard")
    check("GET /dashboard -> 200", r.status_code == 200)
    if r.status_code == 200:
        d = r.json()
        check("Dashboard has total_articles", "total_articles" in d and d["total_articles"] >= 1)

    # --- Cleanup the smoke article ---
    if cid:
        r = requests.delete(f"{BASE}/articles/{aid}/comments/{cid}", headers=hdr(employee_id))
        check("DELETE comment -> 204", r.status_code == 204)

    r = requests.delete(f"{BASE}/articles/{aid}", headers=hdr(admin_id))
    check("DELETE article (admin) -> 204", r.status_code == 204)

    # Cleanup the smoke category
    if new_cat_id:
        r = requests.delete(f"{BASE}/categories/{new_cat_id}", headers=hdr(admin_id))
        check("DELETE category (admin) -> 204", r.status_code == 204)

    print()
    print(f"{INFO} Summary: {passes} passed, {fails} failed")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
