"""SQLAlchemy ORM models for the Enterprise Knowledge Base Management System.

Entity overview:
- Role         : Admin / Author / Reviewer / Employee
- User         : belongs to one Role
- Category     : self-referencing (hierarchical) tree
- Tag          : free-form keyword
- Article      : core entity, lifecycle: draft -> pending -> approved/rejected -> archived
- ArticleTag   : many-to-many between Article and Tag
- Attachment   : uploaded file linked to an Article
- Comment      : user comment on an Article
- Rating       : 1-5 star rating; one rating per (user, article) pair
- Bookmark     : user bookmarks an Article; unique per (user, article)
- ApprovalLog  : audit row each time a reviewer approves/rejects an article
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship

from .db import Base


# ---------- Roles & Users ---------- #

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    role = relationship("Role", back_populates="users")
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")


# ---------- Categories (hierarchical) & Tags ---------- #

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="category")

    __table_args__ = (
        UniqueConstraint("name", "parent_id", name="uq_category_name_parent"),
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(60), unique=True, nullable=False, index=True)

    articles = relationship("Article", secondary="article_tags", back_populates="tags")


class ArticleTag(Base):
    __tablename__ = "article_tags"

    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


# ---------- Articles ---------- #

ARTICLE_STATUSES = ("draft", "pending", "approved", "rejected", "archived")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="draft", nullable=False, index=True)
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    category = relationship("Category", back_populates="articles")
    author = relationship("User", back_populates="articles")
    tags = relationship("Tag", secondary="article_tags", back_populates="articles")
    attachments = relationship("Attachment", back_populates="article", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="article", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="article", cascade="all, delete-orphan")
    approval_logs = relationship("ApprovalLog", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','pending','approved','rejected','archived')",
            name="ck_article_status",
        ),
    )


# ---------- Attachments ---------- #

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    article = relationship("Article", back_populates="attachments")


# ---------- Collaboration ---------- #

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    article = relationship("Article", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stars = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    article = relationship("Article", back_populates="ratings")
    user = relationship("User", back_populates="ratings")

    __table_args__ = (
        UniqueConstraint("article_id", "user_id", name="uq_rating_per_user_article"),
        CheckConstraint("stars BETWEEN 1 AND 5", name="ck_rating_range"),
    )


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    article = relationship("Article", back_populates="bookmarks")
    user = relationship("User", back_populates="bookmarks")

    __table_args__ = (
        UniqueConstraint("article_id", "user_id", name="uq_bookmark_per_user_article"),
    )


# ---------- Approval audit log ---------- #

class ApprovalLog(Base):
    __tablename__ = "approval_logs"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(20), nullable=False)  # 'approved' or 'rejected'
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    article = relationship("Article", back_populates="approval_logs")
    reviewer = relationship("User")

    __table_args__ = (
        CheckConstraint("action IN ('approved','rejected')", name="ck_approval_action"),
    )
