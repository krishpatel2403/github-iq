from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class RepositoryMetricsSnapshot(Base):
    __tablename__ = "repository_metrics_snapshot"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(
        Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_at = Column(DateTime(timezone=True), server_default=func.now())
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    closed_issues = Column(Integer, default=0)
    open_prs = Column(Integer, default=0)
    merged_prs = Column(Integer, default=0)

    repository = relationship("Repository", back_populates="snapshots")
