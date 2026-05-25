"""Article + lifecycle endpoints.

Holds: article CRUD, list/filter, single article view (with view count bump),
status transitions, submit-for-approval, approve/reject, plus the nested
collection endpoints for comments, ratings, bookmarks, and approval logs.
"""
import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..db import get_db
from ..deps import current_user, require_roles

router = APIRouter(prefix="/articles", tags=["articles"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".png", ".jpg", ".jpeg", ".txt", ".md",
}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


# ---------- List & detail ----------

@router.get("", response_model=list[schemas.ArticleListItem])
def list_articles(
    db: Session = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    category_id: int | None = None,
    author_id: int | None = None,
    tag: str | None = None,
    q: str | None = None,
    sort: str = Query("recent", pattern="^(recent|popular|oldest)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    arts = crud.list_articles(
        db,
        status=status_filter, category_id=category_id, author_id=author_id,
        tag=tag, q=q, sort=sort, limit=limit, offset=offset,
    )
    return [crud._article_to_list_item(db, a) for a in arts]


@router.get("/{aid}", response_model=schemas.ArticleOut)
def get_article(aid: int, db: Session = Depends(get_db)):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    crud.increment_view(db, art)
    return crud._article_to_out(db, art)


# ---------- Create / update / delete ----------

@router.post(
    "",
    response_model=schemas.ArticleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Admin", "Author"))],
)
def create_article(
    data: schemas.ArticleCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    if data.category_id is not None and not crud.get_category(db, data.category_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Category {data.category_id} not found.")
    art = crud.create_article(db, user, data)
    return crud._article_to_out(db, art)


@router.put(
    "/{aid}",
    response_model=schemas.ArticleOut,
    dependencies=[Depends(require_roles("Admin", "Author"))],
)
def update_article(
    aid: int,
    data: schemas.ArticleUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    # Authors can only edit their own drafts/rejected articles
    if user.role.name.lower() == "author" and art.author_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Authors can only edit their own articles.")
    if data.category_id is not None and not crud.get_category(db, data.category_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Category {data.category_id} not found.")
    art = crud.update_article(db, art, data)
    return crud._article_to_out(db, art)


@router.delete(
    "/{aid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("Admin", "Author"))],
)
def delete_article(
    aid: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    if user.role.name.lower() == "author" and art.author_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Authors can only delete their own articles.")
    crud.delete_article(db, art)
    return None


# ---------- Lifecycle / approval ----------

@router.post(
    "/{aid}/submit",
    response_model=schemas.ArticleOut,
    dependencies=[Depends(require_roles("Admin", "Author"))],
)
def submit_article(
    aid: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    if user.role.name.lower() == "author" and art.author_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Authors can only submit their own articles.")
    if art.status not in ("draft", "rejected"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Cannot submit article from status '{art.status}'."
        )
    art = crud.submit_for_approval(db, art)
    return crud._article_to_out(db, art)


@router.post(
    "/{aid}/decision",
    response_model=schemas.ApprovalLogOut,
    dependencies=[Depends(require_roles("Admin", "Reviewer"))],
)
def decide_article(
    aid: int,
    decision: schemas.ApprovalDecision,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    if art.status != "pending":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Only pending articles can be decided on; current status: '{art.status}'."
        )
    log = crud.record_approval(db, art, user, decision.action, decision.comment)
    return {
        "id": log.id,
        "article_id": log.article_id,
        "reviewer_id": log.reviewer_id,
        "reviewer_name": user.name,
        "action": log.action,
        "comment": log.comment,
        "created_at": log.created_at,
    }


@router.get("/{aid}/approvals", response_model=list[schemas.ApprovalLogOut])
def get_approval_logs(aid: int, db: Session = Depends(get_db)):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    logs = crud.list_approval_logs(db, aid)
    return [{
        "id": l.id, "article_id": l.article_id, "reviewer_id": l.reviewer_id,
        "reviewer_name": l.reviewer.name if l.reviewer else None,
        "action": l.action, "comment": l.comment, "created_at": l.created_at,
    } for l in logs]


@router.put(
    "/{aid}/status",
    response_model=schemas.ArticleOut,
    dependencies=[Depends(require_roles("Admin"))],
)
def set_status(
    aid: int,
    data: schemas.ArticleStatusUpdate,
    db: Session = Depends(get_db),
):
    """Admin-only manual status override (e.g., archive)."""
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    art = crud.set_article_status(db, art, data.status)
    return crud._article_to_out(db, art)


# ---------- Attachments ----------

@router.post(
    "/{aid}/attachments",
    response_model=schemas.AttachmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Admin", "Author"))],
)
async def upload_attachment(
    aid: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    if user.role.name.lower() == "author" and art.author_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Authors can only attach to their own articles.")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"File type '{ext}' not allowed. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit."
        )

    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / stored_name
    dest.write_bytes(contents)

    att = models.Attachment(
        article_id=art.id,
        file_name=file.filename or stored_name,
        stored_name=stored_name,
        content_type=file.content_type,
        size_bytes=len(contents),
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


@router.get("/{aid}/attachments", response_model=list[schemas.AttachmentOut])
def list_attachments(aid: int, db: Session = Depends(get_db)):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    return art.attachments


@router.get("/{aid}/attachments/{att_id}/download")
def download_attachment(aid: int, att_id: int, db: Session = Depends(get_db)):
    att = db.query(models.Attachment).filter(
        models.Attachment.id == att_id,
        models.Attachment.article_id == aid,
    ).first()
    if not att:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Attachment not found.")
    path = UPLOAD_DIR / att.stored_name
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File missing on server.")
    return FileResponse(path, filename=att.file_name, media_type=att.content_type or "application/octet-stream")


@router.delete(
    "/{aid}/attachments/{att_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("Admin", "Author"))],
)
def delete_attachment(
    aid: int,
    att_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    att = db.query(models.Attachment).filter(
        models.Attachment.id == att_id,
        models.Attachment.article_id == aid,
    ).first()
    if not att:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Attachment not found.")
    if user.role.name.lower() == "author" and att.article.author_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Authors can only delete their own attachments.")
    path = UPLOAD_DIR / att.stored_name
    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass
    db.delete(att)
    db.commit()
    return None


# ---------- Comments ----------

@router.get("/{aid}/comments", response_model=list[schemas.CommentOut])
def list_comments(aid: int, db: Session = Depends(get_db)):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    items = crud.list_comments(db, aid)
    return [{
        "id": c.id, "article_id": c.article_id, "user_id": c.user_id,
        "user_name": c.user.name if c.user else None,
        "body": c.body, "created_at": c.created_at,
    } for c in items]


@router.post(
    "/{aid}/comments",
    response_model=schemas.CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    aid: int,
    data: schemas.CommentCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    c = crud.create_comment(db, art, user, data.body)
    return {
        "id": c.id, "article_id": c.article_id, "user_id": c.user_id,
        "user_name": user.name, "body": c.body, "created_at": c.created_at,
    }


@router.delete(
    "/{aid}/comments/{cid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    aid: int,
    cid: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    c = db.query(models.Comment).filter(
        models.Comment.id == cid, models.Comment.article_id == aid
    ).first()
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found.")
    # Author of the comment, or Admin
    if c.user_id != user.id and user.role.name.lower() != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Can only delete your own comment.")
    crud.delete_comment(db, c)
    return None


# ---------- Ratings ----------

@router.post(
    "/{aid}/ratings",
    response_model=schemas.RatingOut,
    status_code=status.HTTP_201_CREATED,
)
def rate_article(
    aid: int,
    data: schemas.RatingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    return crud.upsert_rating(db, art, user, data.stars)


# ---------- Bookmarks ----------

@router.post(
    "/{aid}/bookmark",
    status_code=status.HTTP_200_OK,
)
def toggle_bookmark(
    aid: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    art = crud.get_article(db, aid)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Article {aid} not found.")
    result = crud.toggle_bookmark(db, art, user)
    if result is None:
        return {"bookmarked": False, "article_id": aid}
    return {"bookmarked": True, "article_id": aid, "bookmark_id": result.id}
