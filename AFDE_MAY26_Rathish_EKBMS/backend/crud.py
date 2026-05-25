"""CRUD layer: all DB-touching logic isolated from FastAPI routers.

Routers stay thin and call these functions. This makes endpoints easy to test
and keeps SQL concerns out of HTTP concerns.
"""
from typing import List, Optional, Sequence
from sqlalchemy import func, or_, desc, asc
from sqlalchemy.orm import Session, joinedload

from . import models, schemas


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _article_to_out(db: Session, art: models.Article) -> dict:
    """Build the dict used to populate ArticleOut, including aggregates."""
    avg, cnt = db.query(
        func.coalesce(func.avg(models.Rating.stars), 0.0),
        func.count(models.Rating.id),
    ).filter(models.Rating.article_id == art.id).first()
    return {
        "id": art.id,
        "title": art.title,
        "content": art.content,
        "category_id": art.category_id,
        "category_name": art.category.name if art.category else None,
        "author_id": art.author_id,
        "author_name": art.author.name if art.author else None,
        "status": art.status,
        "view_count": art.view_count,
        "created_at": art.created_at,
        "updated_at": art.updated_at,
        "tags": art.tags,
        "attachments": art.attachments,
        "average_rating": round(float(avg or 0.0), 2),
        "rating_count": int(cnt or 0),
    }


def _article_to_list_item(db: Session, art: models.Article) -> dict:
    avg = db.query(func.coalesce(func.avg(models.Rating.stars), 0.0))\
        .filter(models.Rating.article_id == art.id).scalar() or 0.0
    return {
        "id": art.id,
        "title": art.title,
        "category_id": art.category_id,
        "category_name": art.category.name if art.category else None,
        "author_id": art.author_id,
        "author_name": art.author.name if art.author else None,
        "status": art.status,
        "view_count": art.view_count,
        "updated_at": art.updated_at,
        "tags": art.tags,
        "average_rating": round(float(avg), 2),
    }


def _get_or_create_tag(db: Session, name: str) -> models.Tag:
    name = name.strip().lower()
    tag = db.query(models.Tag).filter(models.Tag.name == name).first()
    if not tag:
        tag = models.Tag(name=name)
        db.add(tag)
        db.flush()
    return tag


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

def list_roles(db: Session) -> Sequence[models.Role]:
    return db.query(models.Role).order_by(models.Role.id).all()


def get_role_by_name(db: Session, name: str) -> Optional[models.Role]:
    return db.query(models.Role).filter(models.Role.name == name).first()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users(db: Session) -> Sequence[models.User]:
    return db.query(models.User).options(joinedload(models.User.role))\
        .order_by(models.User.id).all()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).options(joinedload(models.User.role))\
        .filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, data: schemas.UserCreate) -> models.User:
    user = models.User(name=data.name, email=str(data.email), role_id=data.role_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: models.User, data: schemas.UserUpdate) -> models.User:
    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        user.email = str(data.email)
    if data.role_id is not None:
        user.role_id = data.role_id
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: models.User) -> None:
    db.delete(user)
    db.commit()


# ---------------------------------------------------------------------------
# Categories (hierarchical)
# ---------------------------------------------------------------------------

def list_categories(db: Session) -> Sequence[models.Category]:
    return db.query(models.Category).order_by(models.Category.parent_id.asc().nullsfirst(),
                                              models.Category.name.asc()).all()


def get_category(db: Session, cid: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == cid).first()


def category_tree(db: Session) -> List[dict]:
    rows = db.query(models.Category).order_by(models.Category.name).all()
    by_id = {c.id: {
        "id": c.id, "name": c.name, "parent_id": c.parent_id,
        "created_at": c.created_at, "children": []
    } for c in rows}
    roots: List[dict] = []
    for c in rows:
        node = by_id[c.id]
        if c.parent_id and c.parent_id in by_id:
            by_id[c.parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


def create_category(db: Session, data: schemas.CategoryCreate) -> models.Category:
    cat = models.Category(name=data.name.strip(), parent_id=data.parent_id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, cat: models.Category, data: schemas.CategoryUpdate) -> models.Category:
    if data.name is not None:
        cat.name = data.name.strip()
    if data.parent_id is not None:
        # prevent making a category its own ancestor
        if data.parent_id == cat.id:
            raise ValueError("A category cannot be its own parent.")
        cat.parent_id = data.parent_id
    db.commit()
    db.refresh(cat)
    return cat


def delete_category(db: Session, cat: models.Category) -> None:
    db.delete(cat)
    db.commit()


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

def list_tags(db: Session) -> Sequence[models.Tag]:
    return db.query(models.Tag).order_by(models.Tag.name).all()


def create_tag(db: Session, data: schemas.TagCreate) -> models.Tag:
    tag = _get_or_create_tag(db, data.name)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag: models.Tag) -> None:
    db.delete(tag)
    db.commit()


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------

def get_article(db: Session, aid: int) -> Optional[models.Article]:
    return db.query(models.Article).options(
        joinedload(models.Article.category),
        joinedload(models.Article.author),
        joinedload(models.Article.tags),
        joinedload(models.Article.attachments),
    ).filter(models.Article.id == aid).first()


def create_article(db: Session, author: models.User, data: schemas.ArticleCreate) -> models.Article:
    art = models.Article(
        title=data.title.strip(),
        content=data.content,
        category_id=data.category_id,
        author_id=author.id,
        status="draft",
    )
    if data.tag_names:
        art.tags = [_get_or_create_tag(db, n) for n in data.tag_names if n.strip()]
    db.add(art)
    db.commit()
    db.refresh(art)
    return art


def update_article(db: Session, art: models.Article, data: schemas.ArticleUpdate) -> models.Article:
    if data.title is not None:
        art.title = data.title.strip()
    if data.content is not None:
        art.content = data.content
    if data.category_id is not None:
        art.category_id = data.category_id
    if data.tag_names is not None:
        art.tags = [_get_or_create_tag(db, n) for n in data.tag_names if n.strip()]
    db.commit()
    db.refresh(art)
    return art


def delete_article(db: Session, art: models.Article) -> None:
    db.delete(art)
    db.commit()


def set_article_status(db: Session, art: models.Article, status: str) -> models.Article:
    art.status = status
    db.commit()
    db.refresh(art)
    return art


def increment_view(db: Session, art: models.Article) -> None:
    art.view_count = (art.view_count or 0) + 1
    db.commit()


def list_articles(
    db: Session,
    *,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    sort: str = "recent",
    limit: int = 50,
    offset: int = 0,
) -> List[models.Article]:
    query = db.query(models.Article).options(
        joinedload(models.Article.category),
        joinedload(models.Article.author),
        joinedload(models.Article.tags),
    )
    if status:
        query = query.filter(models.Article.status == status)
    if category_id is not None:
        query = query.filter(models.Article.category_id == category_id)
    if author_id is not None:
        query = query.filter(models.Article.author_id == author_id)
    if tag:
        query = query.join(models.Article.tags).filter(models.Tag.name == tag.strip().lower())
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(models.Article.title.ilike(like),
                                 models.Article.content.ilike(like)))
    if sort == "popular":
        query = query.order_by(desc(models.Article.view_count), desc(models.Article.updated_at))
    elif sort == "oldest":
        query = query.order_by(asc(models.Article.created_at))
    else:
        query = query.order_by(desc(models.Article.updated_at))
    return query.offset(offset).limit(limit).all()


def search_articles(db: Session, q: str, limit: int = 25) -> List[models.Article]:
    """Full-text search across title, content, and tag name."""
    if not q or not q.strip():
        return []
    like = f"%{q.strip()}%"
    query = (
        db.query(models.Article)
        .options(joinedload(models.Article.category),
                 joinedload(models.Article.author),
                 joinedload(models.Article.tags))
        .outerjoin(models.Article.tags)
        .filter(or_(
            models.Article.title.ilike(like),
            models.Article.content.ilike(like),
            models.Tag.name.ilike(like),
        ))
        .distinct()
        .order_by(desc(models.Article.updated_at))
        .limit(limit)
    )
    return query.all()


# ---------------------------------------------------------------------------
# Approval workflow
# ---------------------------------------------------------------------------

def submit_for_approval(db: Session, art: models.Article) -> models.Article:
    art.status = "pending"
    db.commit()
    db.refresh(art)
    return art


def record_approval(
    db: Session,
    art: models.Article,
    reviewer: models.User,
    action: str,
    comment: Optional[str],
) -> models.ApprovalLog:
    art.status = "approved" if action == "approved" else "rejected"
    log = models.ApprovalLog(
        article_id=art.id,
        reviewer_id=reviewer.id,
        action=action,
        comment=comment,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_approval_logs(db: Session, article_id: int) -> Sequence[models.ApprovalLog]:
    return db.query(models.ApprovalLog)\
        .options(joinedload(models.ApprovalLog.reviewer))\
        .filter(models.ApprovalLog.article_id == article_id)\
        .order_by(desc(models.ApprovalLog.created_at)).all()


# ---------------------------------------------------------------------------
# Comments / Ratings / Bookmarks
# ---------------------------------------------------------------------------

def list_comments(db: Session, article_id: int) -> Sequence[models.Comment]:
    return db.query(models.Comment)\
        .options(joinedload(models.Comment.user))\
        .filter(models.Comment.article_id == article_id)\
        .order_by(asc(models.Comment.created_at)).all()


def create_comment(db: Session, art: models.Article, user: models.User, body: str) -> models.Comment:
    c = models.Comment(article_id=art.id, user_id=user.id, body=body.strip())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def delete_comment(db: Session, comment: models.Comment) -> None:
    db.delete(comment)
    db.commit()


def upsert_rating(db: Session, art: models.Article, user: models.User, stars: int) -> models.Rating:
    existing = db.query(models.Rating)\
        .filter(models.Rating.article_id == art.id,
                models.Rating.user_id == user.id).first()
    if existing:
        existing.stars = stars
        db.commit()
        db.refresh(existing)
        return existing
    r = models.Rating(article_id=art.id, user_id=user.id, stars=stars)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def list_bookmarks(db: Session, user_id: int) -> Sequence[models.Bookmark]:
    return db.query(models.Bookmark)\
        .filter(models.Bookmark.user_id == user_id)\
        .order_by(desc(models.Bookmark.created_at)).all()


def toggle_bookmark(db: Session, art: models.Article, user: models.User) -> Optional[models.Bookmark]:
    """Toggle behavior: returns the new bookmark, or None if it was removed."""
    existing = db.query(models.Bookmark)\
        .filter(models.Bookmark.article_id == art.id,
                models.Bookmark.user_id == user.id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return None
    bm = models.Bookmark(article_id=art.id, user_id=user.id)
    db.add(bm)
    db.commit()
    db.refresh(bm)
    return bm


# ---------------------------------------------------------------------------
# Dashboard aggregates
# ---------------------------------------------------------------------------

def dashboard(db: Session) -> dict:
    total = db.query(func.count(models.Article.id)).scalar() or 0
    approved = db.query(func.count(models.Article.id))\
        .filter(models.Article.status == "approved").scalar() or 0
    pending = db.query(func.count(models.Article.id))\
        .filter(models.Article.status == "pending").scalar() or 0
    draft = db.query(func.count(models.Article.id))\
        .filter(models.Article.status == "draft").scalar() or 0
    active_users = db.query(func.count(models.User.id)).scalar() or 0

    most_viewed = db.query(models.Article).options(
        joinedload(models.Article.category),
        joinedload(models.Article.author),
        joinedload(models.Article.tags),
    ).filter(models.Article.status == "approved")\
     .order_by(desc(models.Article.view_count)).limit(5).all()

    recent = db.query(models.Article).options(
        joinedload(models.Article.category),
        joinedload(models.Article.author),
        joinedload(models.Article.tags),
    ).order_by(desc(models.Article.updated_at)).limit(5).all()

    return {
        "total_articles": int(total),
        "approved_articles": int(approved),
        "pending_approvals": int(pending),
        "draft_articles": int(draft),
        "active_users": int(active_users),
        "most_viewed": [_article_to_list_item(db, a) for a in most_viewed],
        "recent": [_article_to_list_item(db, a) for a in recent],
    }
