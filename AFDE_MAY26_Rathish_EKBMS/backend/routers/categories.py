"""Category endpoints (hierarchical)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..db import get_db
from ..deps import require_roles

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return crud.list_categories(db)


@router.get("/tree", response_model=list[schemas.CategoryTreeOut])
def get_category_tree(db: Session = Depends(get_db)):
    return crud.category_tree(db)


@router.get("/{cid}", response_model=schemas.CategoryOut)
def get_category(cid: int, db: Session = Depends(get_db)):
    cat = crud.get_category(db, cid)
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Category {cid} not found.")
    return cat


@router.post(
    "",
    response_model=schemas.CategoryOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Admin"))],
)
def create_category(data: schemas.CategoryCreate, db: Session = Depends(get_db)):
    if data.parent_id is not None and not crud.get_category(db, data.parent_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Parent category {data.parent_id} not found.")
    return crud.create_category(db, data)


@router.put(
    "/{cid}",
    response_model=schemas.CategoryOut,
    dependencies=[Depends(require_roles("Admin"))],
)
def update_category(cid: int, data: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    cat = crud.get_category(db, cid)
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Category {cid} not found.")
    if data.parent_id is not None and data.parent_id != 0:
        if not crud.get_category(db, data.parent_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Parent category {data.parent_id} not found.")
    try:
        return crud.update_category(db, cat, data)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.delete(
    "/{cid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("Admin"))],
)
def delete_category(cid: int, db: Session = Depends(get_db)):
    cat = crud.get_category(db, cid)
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Category {cid} not found.")
    crud.delete_category(db, cat)
    return None
