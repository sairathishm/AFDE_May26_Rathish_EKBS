"""Users + Roles endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..db import get_db
from ..deps import require_roles

router = APIRouter()


# ---------- Roles ----------

@router.get("/roles", response_model=list[schemas.RoleOut], tags=["roles"])
def list_roles(db: Session = Depends(get_db)):
    return crud.list_roles(db)


# ---------- Users ----------

@router.get("/users", response_model=list[schemas.UserOut], tags=["users"])
def list_users(db: Session = Depends(get_db)):
    return crud.list_users(db)


@router.get("/users/{user_id}", response_model=schemas.UserOut, tags=["users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"User {user_id} not found.")
    return user


@router.post(
    "/users",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
    dependencies=[Depends(require_roles("Admin"))],
)
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, str(data.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already in use.")
    role = db.query(models.Role).filter(models.Role.id == data.role_id).first()
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Role {data.role_id} not found.")
    return crud.create_user(db, data)


@router.put(
    "/users/{user_id}",
    response_model=schemas.UserOut,
    tags=["users"],
    dependencies=[Depends(require_roles("Admin"))],
)
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"User {user_id} not found.")
    if data.role_id is not None:
        if not db.query(models.Role).filter(models.Role.id == data.role_id).first():
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Role {data.role_id} not found.")
    return crud.update_user(db, user, data)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["users"],
    dependencies=[Depends(require_roles("Admin"))],
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"User {user_id} not found.")
    crud.delete_user(db, user)
    return None
