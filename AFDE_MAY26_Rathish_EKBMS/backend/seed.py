"""Idempotent seed script. Populates roles, sample users, categories,
tags, and a handful of articles so the UI has something to show.

Run from the project root:
    py -m backend.seed

Safe to re-run: only inserts rows that don't already exist (by natural key).
"""
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal
from . import models


def _get_or_create(db: Session, model, defaults: dict | None = None, **lookup):
    obj = db.query(model).filter_by(**lookup).first()
    if obj:
        return obj, False
    params = {**lookup, **(defaults or {})}
    obj = model(**params)
    db.add(obj)
    db.flush()
    return obj, True


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Roles
        roles = {}
        for name in ("Admin", "Author", "Reviewer", "Employee"):
            r, _ = _get_or_create(db, models.Role, name=name)
            roles[name] = r

        # Users
        users_spec = [
            ("Aarav Admin",     "admin@ekbms.com",          "Admin"),
            ("Priya Author",    "priya.author@ekbms.com",   "Author"),
            ("Rohan Author",    "rohan.author@ekbms.com",   "Author"),
            ("Neha Reviewer",   "neha.reviewer@ekbms.com",  "Reviewer"),
            ("Vikram Employee", "vikram@ekbms.com",         "Employee"),
            ("Sneha Employee",  "sneha@ekbms.com",          "Employee"),
        ]
        users = {}
        for name, email, role_name in users_spec:
            u, _ = _get_or_create(
                db, models.User, email=email,
                defaults={"name": name, "role_id": roles[role_name].id},
            )
            users[email] = u

        # Categories (hierarchical)
        cats_spec = [
            ("HR Policies", None),
            ("IT Support", None),
            ("Finance", None),
            ("Operations", None),
            ("Training Materials", None),
            ("Leave Policies", "HR Policies"),
            ("Onboarding", "HR Policies"),
            ("Networking", "IT Support"),
            ("VPN", "Networking"),
            ("Hardware", "IT Support"),
            ("Expense Reports", "Finance"),
        ]
        cats = {}
        for name, parent_name in cats_spec:
            parent = cats.get(parent_name) if parent_name else None
            c, _ = _get_or_create(
                db, models.Category, name=name,
                parent_id=(parent.id if parent else None),
            )
            cats[name] = c

        # Tags
        tag_names = ["leave", "wfh", "vpn", "troubleshooting", "onboarding",
                     "expense", "policy", "sop", "training", "security"]
        tags = {}
        for n in tag_names:
            t, _ = _get_or_create(db, models.Tag, name=n)
            tags[n] = t

        # Articles
        articles_spec = [
            {
                "title": "Annual Leave Policy 2026",
                "content": ("Employees are entitled to 24 days of paid annual leave per calendar year. "
                            "Requests must be filed in the HR portal at least 7 working days in advance. "
                            "Carry-over of up to 5 days is permitted with manager approval."),
                "category": "Leave Policies", "author": "priya.author@ekbms.com",
                "status": "approved", "view_count": 142, "tags": ["leave", "policy"],
            },
            {
                "title": "Work-From-Home Guidelines",
                "content": ("Hybrid employees may work from home up to 3 days per week. Ensure stable "
                            "internet (10 Mbps+), be reachable on Teams/Slack during core hours, and "
                            "follow the standard security checklist."),
                "category": "HR Policies", "author": "priya.author@ekbms.com",
                "status": "approved", "view_count": 98, "tags": ["wfh", "policy"],
            },
            {
                "title": "VPN Setup — Windows",
                "content": ("Step 1: Download the GlobalProtect installer from the IT portal. "
                            "Step 2: Run as administrator. Step 3: Enter portal address vpn.ekbms.local. "
                            "Step 4: Authenticate with your AD credentials. "
                            "Step 5: Test by browsing an internal-only resource."),
                "category": "VPN", "author": "rohan.author@ekbms.com",
                "status": "approved", "view_count": 211, "tags": ["vpn", "troubleshooting", "sop"],
            },
            {
                "title": "New Hire Onboarding Checklist",
                "content": ("Day 1: Laptop pickup, ID card, access provisioning. "
                            "Week 1: Mandatory training (security, code of conduct). "
                            "Week 2: Team intros + first ticket assignment. "
                            "End of month: 30-day check-in with manager."),
                "category": "Onboarding", "author": "priya.author@ekbms.com",
                "status": "approved", "view_count": 73, "tags": ["onboarding", "sop"],
            },
            {
                "title": "Expense Report Submission SOP",
                "content": ("Submit receipts through the Finance portal within 30 days of incurring "
                            "the expense. Attach scanned copies of all receipts > Rs. 500. Approvals "
                            "route to your reporting manager, then Finance."),
                "category": "Expense Reports", "author": "rohan.author@ekbms.com",
                "status": "approved", "view_count": 54, "tags": ["expense", "sop"],
            },
            {
                "title": "Laptop Issue Troubleshooting",
                "content": ("If laptop fails to boot: 1) Hold power for 30s, 2) Try external monitor, "
                            "3) Check for amber LED. If still failing, raise an IT ticket with serial "
                            "number and amber/red LED status."),
                "category": "Hardware", "author": "rohan.author@ekbms.com",
                "status": "pending", "view_count": 0, "tags": ["troubleshooting"],
            },
            {
                "title": "Information Security Training — Q2",
                "content": ("Mandatory online module covering phishing, password hygiene, data "
                            "classification, and incident reporting. Complete by end of quarter to "
                            "avoid access suspension."),
                "category": "Training Materials", "author": "priya.author@ekbms.com",
                "status": "pending", "view_count": 0, "tags": ["training", "security"],
            },
            {
                "title": "Draft: Reimbursement Policy v2",
                "content": "Working draft for the updated reimbursement policy. To be finalized after Finance review.",
                "category": "Finance", "author": "rohan.author@ekbms.com",
                "status": "draft", "view_count": 0, "tags": ["expense", "policy"],
            },
        ]

        for spec in articles_spec:
            existing = db.query(models.Article).filter_by(title=spec["title"]).first()
            if existing:
                continue
            art = models.Article(
                title=spec["title"],
                content=spec["content"],
                category_id=cats[spec["category"]].id,
                author_id=users[spec["author"]].id,
                status=spec["status"],
                view_count=spec["view_count"],
            )
            art.tags = [tags[n] for n in spec["tags"]]
            db.add(art)
        db.flush()

        # Comments / Ratings / Bookmarks (only if none exist yet for these articles)
        if db.query(models.Comment).count() == 0:
            articles_by_title = {a.title: a for a in db.query(models.Article).all()}
            vikram = users["vikram@ekbms.com"]
            sneha = users["sneha@ekbms.com"]
            leave = articles_by_title["Annual Leave Policy 2026"]
            vpn = articles_by_title["VPN Setup — Windows"]
            db.add_all([
                models.Comment(article_id=leave.id, user_id=vikram.id,
                               body="Very helpful — can we get a quick FAQ for sandwich leaves?"),
                models.Comment(article_id=vpn.id,   user_id=sneha.id,
                               body="Worked perfectly on my Windows 11 machine. Thanks!"),
                models.Comment(article_id=vpn.id,   user_id=vikram.id,
                               body="Does this work for macOS too?"),
            ])

        if db.query(models.Rating).count() == 0:
            arts = {a.title: a for a in db.query(models.Article).all()}
            vikram = users["vikram@ekbms.com"]
            sneha = users["sneha@ekbms.com"]
            ratings = [
                ("Annual Leave Policy 2026", vikram, 5),
                ("Annual Leave Policy 2026", sneha, 4),
                ("Work-From-Home Guidelines", vikram, 4),
                ("VPN Setup — Windows", vikram, 5),
                ("VPN Setup — Windows", sneha, 5),
                ("New Hire Onboarding Checklist", sneha, 4),
                ("Expense Report Submission SOP", vikram, 3),
            ]
            for title, user, stars in ratings:
                if title in arts:
                    db.add(models.Rating(article_id=arts[title].id, user_id=user.id, stars=stars))

        if db.query(models.Bookmark).count() == 0:
            arts = {a.title: a for a in db.query(models.Article).all()}
            vikram = users["vikram@ekbms.com"]
            sneha = users["sneha@ekbms.com"]
            for title, user in [
                ("Annual Leave Policy 2026", vikram),
                ("VPN Setup — Windows", vikram),
                ("VPN Setup — Windows", sneha),
            ]:
                if title in arts:
                    db.add(models.Bookmark(article_id=arts[title].id, user_id=user.id))

        if db.query(models.ApprovalLog).count() == 0:
            vpn = db.query(models.Article).filter_by(title="VPN Setup — Windows").first()
            reviewer = users["neha.reviewer@ekbms.com"]
            if vpn and reviewer:
                db.add(models.ApprovalLog(
                    article_id=vpn.id, reviewer_id=reviewer.id,
                    action="approved",
                    comment="Steps verified end-to-end on a fresh Windows install.",
                ))

        db.commit()
        print("[seed] OK")
        print(f"  roles      : {db.query(models.Role).count()}")
        print(f"  users      : {db.query(models.User).count()}")
        print(f"  categories : {db.query(models.Category).count()}")
        print(f"  tags       : {db.query(models.Tag).count()}")
        print(f"  articles   : {db.query(models.Article).count()}")
        print(f"  comments   : {db.query(models.Comment).count()}")
        print(f"  ratings    : {db.query(models.Rating).count()}")
        print(f"  bookmarks  : {db.query(models.Bookmark).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
