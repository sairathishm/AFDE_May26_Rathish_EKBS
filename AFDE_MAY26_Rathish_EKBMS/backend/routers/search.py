"""Top-level /search endpoint for cross-cutting full-text + filter queries."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..db import get_db

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[schemas.ArticleListItem])
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
    limit: int = Query(25, ge=1, le=100),
):
    """Full-text search across article title, content, and tags."""
    arts = crud.search_articles(db, q, limit=limit)
    return [crud._article_to_list_item(db, a) for a in arts]


@router.get("/bookmarks", response_model=list[schemas.ArticleListItem])
def list_my_bookmarks(
    user_id: int = Query(..., description="User whose bookmarks to fetch"),
    db: Session = Depends(get_db),
):
    """List all articles a user has bookmarked."""
    bookmarks = crud.list_bookmarks(db, user_id)
    arts = [b.article for b in bookmarks if b.article is not None]
    return [crud._article_to_list_item(db, a) for a in arts]
