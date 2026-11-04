"""Repository tracking and analytics API routes.

All routes require a valid session cookie (githubiq_session).
"""

from datetime import datetime, timezone

from app.api.deps import DbDep, get_current_user
from app.core.security import decrypt_token
from app.models.connection import GitHubConnection
from app.models.repository import Repository
from app.models.snapshot import RepositoryMetricsSnapshot
from app.models.user import User
from app.schemas.repository import (
    RepositoryAnalytics,
    RepositoryCreate,
    RepositoryOut,
)
from app.services.github import GitHubClient, GitHubError
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

router = APIRouter()


def _get_github_token(db: Session, user: User) -> str | None:
    """Fetch and decrypt the user's stored GitHub access token."""
    conn = db.query(GitHubConnection).filter(GitHubConnection.user_id == user.id).first()
    if not conn or not conn.encrypted_access_token:
        return None
    try:
        return decrypt_token(conn.encrypted_access_token)
    except Exception:
        return None


@router.get("/repositories", response_model=list[RepositoryOut])
def list_repositories(db: DbDep, user: User = Depends(get_current_user)):
    """List repositories tracked by the current user."""
    repos = db.query(Repository).order_by(desc(Repository.stargazers_count)).all()
    return repos


@router.post("/repositories", response_model=RepositoryOut)
def add_repository(
    payload: RepositoryCreate,
    db: DbDep,
    user: User = Depends(get_current_user),
):
    """Add a repository to track (e.g. "facebook/react")."""
    full_name = payload.full_name.strip()
    if "/" not in full_name:
        raise HTTPException(
            status_code=400,
            detail='full_name must be "owner/repo" (e.g. facebook/react)',
        )

    token = _get_github_token(db, user)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="No GitHub connection found. Please reconnect your GitHub account.",
        )

    client = GitHubClient(access_token=token)
    try:
        repo_data = client.get_repository(full_name)
    except GitHubError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    existing = db.query(Repository).filter(Repository.github_repo_id == repo_data["id"]).first()
    if existing:
        raise HTTPException(status_code=409, detail="Repository already tracked.")

    repo = Repository(
        github_repo_id=repo_data["id"],
        full_name=repo_data["full_name"],
        owner_login=repo_data["owner"]["login"],
        description=repo_data.get("description"),
        html_url=repo_data.get("html_url"),
        stargazers_count=repo_data.get("stargazers_count", 0),
        forks_count=repo_data.get("forks_count", 0),
        watchers_count=repo_data.get("watchers_count", 0),
        open_issues_count=repo_data.get("open_issues_count", 0),
        default_branch=repo_data.get("default_branch"),
        language=repo_data.get("language"),
        pushed_at=_parse_github_ts(repo_data.get("pushed_at")),
        synced_at=datetime.now(timezone.utc),
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)

    _record_snapshot(db, repo.id, repo_data)
    db.commit()

    return repo


@router.get("/repositories/{repo_id}/analytics", response_model=RepositoryAnalytics)
def repository_analytics(
    repo_id: int,
    db: DbDep,
    user: User = Depends(get_current_user),
    force: bool = Query(default=False, description="Re-fetch from GitHub before returning"),
):
    """Return analytics for a tracked repository."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if force:
        token = _get_github_token(db, user)
        if not token:
            raise HTTPException(
                status_code=401,
                detail="No GitHub connection found. Please reconnect your GitHub account.",
            )
        client = GitHubClient(access_token=token)
        try:
            repo_data = client.get_repository(repo.full_name)
            issues = client.get_issues(repo.full_name)
            pulls = client.get_pull_requests(repo.full_name)
        except GitHubError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        _update_repo_from_github(db, repo, repo_data)
        _record_snapshot(db, repo.id, repo_data, issues=issues, pulls=pulls)
        db.commit()
        db.refresh(repo)

    latest = (
        db.query(RepositoryMetricsSnapshot)
        .filter(RepositoryMetricsSnapshot.repository_id == repo.id)
        .order_by(desc(RepositoryMetricsSnapshot.snapshot_at))
        .first()
    )

    return RepositoryAnalytics(
        id=repo.id,
        full_name=repo.full_name,
        html_url=repo.html_url,
        stars=latest.stars if latest else repo.stargazers_count,
        forks=latest.forks if latest else repo.forks_count,
        watchers=latest.watchers if latest else repo.watchers_count,
        open_issues=latest.open_issues if latest else repo.open_issues_count,
        closed_issues=latest.closed_issues if latest else 0,
        open_prs=latest.open_prs if latest else 0,
        merged_prs=latest.merged_prs if latest else 0,
        language=repo.language,
        last_pushed=repo.pushed_at.isoformat() if repo.pushed_at else None,
        last_synced=repo.synced_at.isoformat() if repo.synced_at else None,
    )


def _parse_github_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _record_snapshot(
    db: Session,
    repository_id: int,
    repo_data: dict,
    issues: list[dict] | None = None,
    pulls: list[dict] | None = None,
):
    """Insert a metrics snapshot from GitHub API data."""
    open_issues = 0
    closed_issues = 0
    if issues is not None:
        for item in issues:
            if "pull_request" in item:
                continue
            if item.get("state") == "open":
                open_issues += 1
            else:
                closed_issues += 1

    open_prs = 0
    merged_prs = 0
    if pulls is not None:
        for pr in pulls:
            if pr.get("state") == "open":
                open_prs += 1
            if pr.get("merged_at"):
                merged_prs += 1

    snapshot = RepositoryMetricsSnapshot(
        repository_id=repository_id,
        stars=repo_data.get("stargazers_count", 0),
        forks=repo_data.get("forks_count", 0),
        open_issues=open_issues,
        closed_issues=closed_issues,
        open_prs=open_prs,
        merged_prs=merged_prs,
    )
    db.add(snapshot)

    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if repo:
        repo.stargazers_count = repo_data.get("stargazers_count", 0)
        repo.forks_count = repo_data.get("forks_count", 0)
        repo.watchers_count = repo_data.get("watchers_count", 0)
        repo.open_issues_count = open_issues
        repo.language = repo_data.get("language")
        repo.pushed_at = _parse_github_ts(repo_data.get("pushed_at"))
        repo.synced_at = datetime.now(timezone.utc)


def _update_repo_from_github(db: Session, repo: Repository, repo_data: dict):
    repo.stargazers_count = repo_data.get("stargazers_count", 0)
    repo.forks_count = repo_data.get("forks_count", 0)
    repo.watchers_count = repo_data.get("watchers_count", 0)
    repo.language = repo_data.get("language")
    repo.pushed_at = _parse_github_ts(repo_data.get("pushed_at"))
    repo.synced_at = datetime.now(timezone.utc)
    db.add(repo)
