"""Shared FastAPI dependencies.

`current_user` reads the `X-User-Id` header to identify who is acting (this is
the 'simple role switcher' approach — no JWT, but every action is attributed to
a user and gated by their role).

`require_roles(...)` returns a dependency that 403s unless the current user
holds one of the allowed roles.
"""
from typing import Iterable
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from . import models
from .db import get_db


def current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> models.User:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header. Pick a user from /users first.",
        )
    user = db.query(models.User).options(joinedload(models.User.role))\
        .filter(models.User.id == x_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No user with id={x_user_id}.",
        )
    return user


def require_roles(*allowed: str):
    """Dependency factory that 403s if current user's role isn't in `allowed`."""
    allowed_set = {r.lower() for r in allowed}

    def _checker(user: models.User = Depends(current_user)) -> models.User:
        if user.role.name.lower() not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role(s): {sorted(allowed_set)}; you are '{user.role.name}'.",
            )
        return user

    return _checker
