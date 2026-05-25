"""Dashboard endpoint — aggregates for the home screen."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..db import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=schemas.DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    return crud.dashboard(db)
