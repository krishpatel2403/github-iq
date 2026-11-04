from sqlalchemy import Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class GitHubConnection(Base):
    __tablename__ = "github_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    encrypted_access_token = Column(LargeBinary, nullable=False)
    token_scope = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="connections")
