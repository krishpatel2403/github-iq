# Changelog

All notable changes to GitHubIQ will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- GitHub OAuth login/logout flow with CSRF state protection
- Encrypted GitHub access token storage (Fernet)
- Repository tracking and analytics (stars, forks, watchers, issues, PRs)
- Manual sync from GitHub API with sync status tracking
- React frontend with Tailwind CSS and Recharts charts
- Loading, empty, and error states on all async actions
- Responsive dashboard with tracked repository cards

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Fernet encryption for tokens at rest
- HttpOnly, SameSite=Lax session cookies
- CORS restricted to frontend origin

## [0.1.0] - 2026-10-30

### Added
- Initial project scaffolding (Phase 1 & 2)
- Backend: FastAPI, SQLAlchemy 2.0, Alembic, SQLite
- Backend: `/api/v1/health` endpoint
- Frontend: React 18, Vite, TypeScript, Tailwind CSS
- CI: GitHub Actions workflow
- Deployment: Dockerfiles, Render config, Vercel config
