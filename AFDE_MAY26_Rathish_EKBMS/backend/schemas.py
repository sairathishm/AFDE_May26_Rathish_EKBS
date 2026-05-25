"""Pydantic v2 schemas for request/response models.

Separation: Create / Update / Response shapes per resource so partial updates
work cleanly and response payloads stay decoupled from inputs.
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


ARTICLE_STATUSES = ("draft", "pending", "approved", "rejected", "archived")
ApprovalAction = Literal["approved", "rejected"]


# ---------- Roles ---------- #

class RoleOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


# ---------- Users ---------- #

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    role_id: int


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleOut
    created_at: datetime
    model_config = {"from_attributes": True}


# ---------- Categories (hierarchical) ---------- #

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    parent_id: Optional[int] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    parent_id: Optional[int] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime
    model_config = {"from_attributes": True}


class CategoryTreeOut(CategoryOut):
    children: List["CategoryTreeOut"] = []


# ---------- Tags ---------- #

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)


class TagOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


# ---------- Articles ---------- #

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=1)
    category_id: Optional[int] = None
    tag_names: List[str] = Field(default_factory=list)


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = None
    tag_names: Optional[List[str]] = None


class ArticleStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def _valid_status(cls, v: str) -> str:
        if v not in ARTICLE_STATUSES:
            raise ValueError(f"status must be one of {ARTICLE_STATUSES}")
        return v


class AttachmentOut(BaseModel):
    id: int
    file_name: str
    content_type: Optional[str]
    size_bytes: int
    uploaded_at: datetime
    model_config = {"from_attributes": True}


class ArticleOut(BaseModel):
    id: int
    title: str
    content: str
    category_id: Optional[int]
    category_name: Optional[str] = None
    author_id: int
    author_name: Optional[str] = None
    status: str
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagOut] = []
    attachments: List[AttachmentOut] = []
    average_rating: float = 0.0
    rating_count: int = 0
    model_config = {"from_attributes": True}


class ArticleListItem(BaseModel):
    id: int
    title: str
    category_id: Optional[int]
    category_name: Optional[str] = None
    author_id: int
    author_name: Optional[str] = None
    status: str
    view_count: int
    updated_at: datetime
    tags: List[TagOut] = []
    average_rating: float = 0.0
    model_config = {"from_attributes": True}


# ---------- Approval workflow ---------- #

class ApprovalDecision(BaseModel):
    action: ApprovalAction
    comment: Optional[str] = None


class ApprovalLogOut(BaseModel):
    id: int
    article_id: int
    reviewer_id: int
    reviewer_name: Optional[str] = None
    action: str
    comment: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


# ---------- Collaboration ---------- #

class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)


class CommentOut(BaseModel):
    id: int
    article_id: int
    user_id: int
    user_name: Optional[str] = None
    body: str
    created_at: datetime
    model_config = {"from_attributes": True}


class RatingCreate(BaseModel):
    stars: int = Field(..., ge=1, le=5)


class RatingOut(BaseModel):
    id: int
    article_id: int
    user_id: int
    stars: int
    created_at: datetime
    model_config = {"from_attributes": True}


class BookmarkOut(BaseModel):
    id: int
    article_id: int
    user_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ---------- Dashboard ---------- #

class DashboardOut(BaseModel):
    total_articles: int
    approved_articles: int
    pending_approvals: int
    draft_articles: int
    active_users: int
    most_viewed: List[ArticleListItem]
    recent: List[ArticleListItem]


# Resolve forward refs for CategoryTreeOut
CategoryTreeOut.model_rebuild()
