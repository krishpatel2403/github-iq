from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RepositoryBase(BaseModel):
    full_name: str
    owner_login: str
    description: Optional[str] = None
    html_url: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    watchers_count: int = 0
    open_issues_count: int = 0
    default_branch: Optional[str] = None
    language: Optional[str] = None
    pushed_at: Optional[datetime] = None


class RepositoryCreate(BaseModel):
    full_name: str


class RepositoryOut(RepositoryBase):
    id: int
    synced_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RepositoryAnalytics(BaseModel):
    id: int
    full_name: str
    html_url: Optional[str] = None
    stars: int
    forks: int
    watchers: int
    open_issues: int
    closed_issues: int
    open_prs: int
    merged_prs: int
    language: Optional[str]
    last_pushed: Optional[str]
    last_synced: Optional[str]


class SyncStatus(BaseModel):
    status: str
    records_fetched: int
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
