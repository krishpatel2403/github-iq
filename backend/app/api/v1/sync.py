"""Repository sync API routes.

Trigger a manual re-sync of all tracked repositories from GitHub and
check the status of the most recent sync.
"""

from datetime import datetime, timedelta, timezone

from app.api.deps import DbDep, get_current_user
from app.core.security import decrypt_token
from app.models.connection import GitHubConnection
from app.models.repository import Repository
from app.models.snapshot import RepositoryMetricsSnapshot
from app.models.sync_log import SyncLog
from app.models.user import User
from app.schemas.repository import SyncStatus
from app.services.github import GitHubClient, GitHubError
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

router = APIRouter()


def _get_github_token(db: Session, user: User) -> str | None:
    conn = db.query(GitHubConnection).filter(GitHubConnection.user_id == user.id).first()
    if not conn or not conn.encrypted_access_token:
        return None
    try:
        return decrypt_token(conn.encrypted_access_token)
    except Exception:
        return None


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


@router.post("/sync/repositories", response_model=SyncStatus)
def sync_repositories(
    db: DbDep,
    user: User = Depends(get_current_user),
    force: bool = Query(default=False, description="Re-sync even if recently synced"),
):
    """Sync all tracked repositories for the current user from GitHub."""
    token = _get_github_token(db, user)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="No GitHub connection found. Please reconnect your GitHub account.",
        )

    log = SyncLog(user_id=user.id, status="pending")
    db.add(log)
    db.commit()
    db.refresh(log)

    client = GitHubClient(access_token=token)
    repos = db.query(Repository).all()
    records_fetched = 0
    error_message = None

    try:
        for repo in repos:
            if not force and repo.synced_at:
                if repo.synced_at.replace(tzinfo=timezone.utc) > datetime.now(
                    timezone.utc
                ) - timedelta(minutes=15):
                    continue

            try:
                repo_data = client.get_repository(repo.full_name)
                issues = client.get_issues(repo.full_name)
                pulls = client.get_pull_requests(repo.full_name)
            except GitHubError as exc:
                error_message = f"Failed to sync {repo.full_name}: {exc}"
                continue

            _record_snapshot(db, repo.id, repo_data, issues=issues, pulls=pulls)
            records_fetched += 1

        log.status = "completed"
        log.completed_at = datetime.now(timezone.utc)
        log.records_fetched = records_fetched
        log.error_message = error_message
    except Exception as exc:
        log.status = "failed"
        log.completed_at = datetime.now(timezone.utc)
        log.error_message = str(exc)

    db.commit()
    return SyncStatus(
        status=log.status,
        records_fetched=log.records_fetched,
        started_at=log.started_at.isoformat() if log.started_at else None,
        completed_at=log.completed_at.isoformat() if log.completed_at else None,
        error_message=log.error_message,
    )


@router.get("/sync/status", response_model=SyncStatus)
def sync_status(db: DbDep, user: User = Depends(get_current_user)):
    """Return the most recent sync log for the current user."""
    log = (
        db.query(SyncLog)
        .filter(SyncLog.user_id == user.id)
        .order_by(desc(SyncLog.started_at))
        .first()
    )
    if not log:
        return SyncStatus(
            status="never",
            records_fetched=0,
            started_at=None,
            completed_at=None,
            error_message=None,
        )
    return SyncStatus(
        status=log.status,
        records_fetched=log.records_fetched,
        started_at=log.started_at.isoformat() if log.started_at else None,
        completed_at=log.completed_at.isoformat() if log.completed_at else None,
        error_message=log.error_message,
    )
