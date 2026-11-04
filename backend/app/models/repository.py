from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_repo_id = Column(Integer, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False, index=True)
    owner_login = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    html_url = Column(String, nullable=True)
    stargazers_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    watchers_count = Column(Integer, default=0)
    open_issues_count = Column(Integer, default=0)
    default_branch = Column(String, nullable=True)
    language = Column(String, nullable=True)
    pushed_at = Column(DateTime(timezone=True), nullable=True)
    synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    snapshots = relationship(
        "RepositoryMetricsSnapshot",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
