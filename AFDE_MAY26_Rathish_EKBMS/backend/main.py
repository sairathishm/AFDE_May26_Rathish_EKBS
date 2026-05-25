"""FastAPI app entrypoint.

Run from the project root with:
    py -m uvicorn backend.main:app --reload
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .db import Base, engine
from . import models  # noqa: F401 (ensure models are registered on Base.metadata)
from .routers import users, categories, tags, articles, search, dashboard

# Create tables on startup. Idempotent — won't drop existing data.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Enterprise Knowledge Base Management System (EKBMS) API",
    description=(
        "Phase 1 capstone backend. Centralized platform for creating, "
        "categorizing, approving, and searching enterprise knowledge articles. "
        "Auth uses an `X-User-Id` header (simple role-switcher pattern)."
    ),
    version="1.0.0",
)

# ---------- CORS ---------- #

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Exception handlers ---------- #

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return a flatter, friendlier 422 payload."""
    errors = []
    for err in exc.errors():
        loc = err.get("loc", [])
        # Strip the leading 'body'/'query'/'path' marker so the field name reads cleanly.
        field = ".".join(str(x) for x in loc[1:]) if len(loc) > 1 else ".".join(str(x) for x in loc)
        errors.append({"field": field or "body", "message": err.get("msg", "Invalid value")})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed", "errors": errors},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Database integrity error (likely duplicate or invalid reference)."},
    )


# ---------- Routes ---------- #

@app.get("/", tags=["meta"])
def root():
    return {
        "name": "EKBMS API",
        "version": app.version,
        "docs": "/docs",
        "endpoints": [
            "/roles", "/users", "/categories", "/categories/tree",
            "/tags", "/articles", "/articles/{id}/submit",
            "/articles/{id}/decision", "/articles/{id}/attachments",
            "/articles/{id}/comments", "/articles/{id}/ratings",
            "/articles/{id}/bookmark", "/search", "/search/bookmarks",
            "/dashboard",
        ],
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


# Register routers
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(articles.router)
app.include_router(search.router)
app.include_router(dashboard.router)
