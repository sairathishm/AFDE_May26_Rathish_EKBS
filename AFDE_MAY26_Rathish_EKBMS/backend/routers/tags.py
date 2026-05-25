"""Tag endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..db import get_db
from ..deps import require_roles

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[schemas.TagOut])
def list_tags(db: Session = Depends(get_db)):
    return crud.list_tags(db)


@router.post(
    "",
    response_model=schemas.TagOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Admin", "Author"))],
)
def create_tag(data: schemas.TagCreate, db: Session = Depends(get_db)):
    return crud.create_tag(db, data)


@router.delete(
    "/{tid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("Admin"))],
)
def delete_tag(tid: int, db: Session = Depends(get_db)):
    tag = db.query(models.Tag).filter(models.Tag.id == tid).first()
    if not tag:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Tag {tid} not found.")
    crud.delete_tag(db, tag)
    return None
