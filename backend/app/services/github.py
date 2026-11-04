"""GitHub API client wrapper.

Wraps the GitHub REST API with authentication, rate-limit awareness, and
error handling. All methods return parsed JSON from GitHub.
"""

import httpx


class GitHubError(Exception):
    """Raised when the GitHub API returns an error."""


class GitHubClient:
    def __init__(self, access_token: str | None = None):
        self.access_token = access_token
        self.base_url = "https://api.github.com"

    def _headers(self) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitHubIQ/0.1.0",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    async def get(self, path: str, params: dict | None = None) -> dict:
        """GET a single JSON object from the GitHub API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{path}",
                headers=self._headers(),
                params=params,
                timeout=30,
            )
            if response.status_code == 401:
                raise GitHubError("GitHub token is invalid or expired.")
            if response.status_code == 403:
                raise GitHubError("GitHub API rate limit exceeded or forbidden.")
            if response.status_code == 404:
                raise GitHubError("GitHub resource not found.")
            response.raise_for_status()
            return response.json()

    async def get_list(self, path: str, params: dict | None = None) -> list:
        """GET a JSON list from the GitHub API."""
        data = await self.get(path, params)
        if not isinstance(data, list):
            raise GitHubError(f"Expected a list from {path}, got {type(data).__name__}")
        return data

    # --- Repository ----------------------------------------------------------

    async def get_repository(self, full_name: str) -> dict:
        """Fetch repository metadata (stars, forks, language, pushed_at, ...)."""
        return await self.get(f"/repos/{full_name}")

    async def get_languages(self, full_name: str) -> dict[str, int]:
        """Fetch language breakdown: {language: byte_count, ...}."""
        return await self.get(f"/repos/{full_name}/languages")

    # --- Issues --------------------------------------------------------------

    async def get_issues(
        self, full_name: str, state: str = "all", per_page: int = 100
    ) -> list[dict]:
        """Fetch issues (includes pull requests on GitHub's API)."""
        return await self.get_list(
            f"/repos/{full_name}/issues",
            params={"state": state, "per_page": per_page, "page": 1},
        )

    # --- Pull requests -------------------------------------------------------

    async def get_pull_requests(
        self, full_name: str, state: str = "all", per_page: int = 100
    ) -> list[dict]:
        """Fetch pull requests."""
        return await self.get_list(
            f"/repos/{full_name}/pulls",
            params={"state": state, "per_page": per_page, "page": 1},
        )
