# GitHubIQ — Developer Analytics

> Connect your GitHub account, track repositories, and view analytics (stars, forks, issues, pull requests, languages, activity) in a polished, responsive dashboard.

[![CI](https://img.shields.io/github/actions/workflow/status/<your-username>/github-iq/ci.yml?branch=main)](https://github.com/<your-username>/github-iq/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-latest-yellow.svg)](https://vitejs.dev)

## What GitHubIQ Does

GitHubIQ is a developer analytics dashboard that turns raw GitHub data into meaningful insights:

- **GitHub OAuth login/logout** — connect your account, no passwords stored
- **Connected profile view** — stars, repos, followers, account age
- **Repository tracking** — add any public repo to monitor
- **Repository analytics** — stars, forks, watchers, open/closed issues, open/merged PRs, top language, last activity
- **Dashboard** — aggregated metrics across all tracked repositories
- **Manual sync** — refresh data from GitHub API on demand with last-synced timestamps
- **Responsive UI** — loading, empty, success, and error states; works on mobile, tablet, and desktop

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + FastAPI + SQLAlchemy 2.0 + SQLite + Alembic |
| Auth | GitHub OAuth (Authlib), Fernet-encrypted token storage, signed session cookies |
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS + Recharts + Axios + React Router |
| Tests | pytest + httpx (backend), Vitest + React Testing Library (frontend) |
| Lint/Format | ruff (Python), ESLint + Prettier (frontend) |
| CI | GitHub Actions |

## Quick Start (Windows)

### Prerequisites

- Python 3.11+
- Node.js 18+ (LTS recommended)
- Git

### 1. Clone the Repository

```powershell
git clone https://github.com/<your-username>/github-iq.git
cd github-iq
```

### 2. Run Setup

```powershell
.\setup.ps1
```

This initializes the Git repo, creates Python and Node virtual environments, installs dependencies, and copies `.env.example` files.

### 3. Configure Environment Variables

Create a GitHub OAuth App at https://github.com/settings/developers:

- **Application name:** GitHubIQ
- **Homepage URL:** `http://localhost:8000`
- **Authorization callback URL:** `http://localhost:8000/api/v1/auth/github/callback`

Copy the **Client ID** and **Client Secret**.

Then generate secrets:

```powershell
# Fernet key (encrypts GitHub tokens at rest)
backend\.venv\Scripts\python.exe -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Session secret (signs session cookies)
# Use any random 32+ character string
```

Edit `backend/.env`:

```env
GITHUB_CLIENT_ID=your_actual_client_id
GITHUB_CLIENT_SECRET=your_actual_client_secret
GITHUB_CALLBACK_URL=http://localhost:8000/api/v1/auth/github/callback
FRONTEND_URL=http://localhost:5173
GITHUB_TOKEN_ENCRYPTION_KEY=your_fernet_key
SESSION_SECRET_KEY=your_session_secret
CORS_ORIGINS=http://localhost:5173
```

### 4. Run the Backend

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### 5. Run the Frontend

```powershell
cd frontend
cmd /c npm run dev
```

### 6. Open the App

Open **http://localhost:5173** in your browser.

## Deployment

See `docs/DEPLOYMENT.md` for step-by-step instructions to deploy on Render (backend) + Vercel (frontend), both with free tiers.

### Quick Deploy Summary

1. Create a GitHub OAuth App with production callback URLs
2. Generate Fernet key and session secret
3. Deploy backend to Render (free tier)
4. Deploy frontend to Vercel (free tier)
5. Update GitHub OAuth callback URLs to production URLs
6. Share your frontend URL — anyone can use it directly

## Project Structure

```
github-iq/
├── backend/                 # FastAPI application
│   ├── app/                 # Source code
│   ├── tests/               # pytest tests
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Runtime dependencies
│   ├── requirements-dev.txt # Dev dependencies
│   ├── Dockerfile
│   └── .env.example
├── frontend/                # React + Vite SPA
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # API client
│   │   ├── pages/           # Page components
│   │   ├── types/           # TypeScript types
│   │   └── __tests__/       # Vitest tests
│   ├── dist/                # Production build
│   ├── Dockerfile
│   ├── vercel.json
│   ├── package.json
│   └── .env.example
├── docs/                    # Documentation
│   ├── DEPLOYMENT.md
│   ├── PHASE1_PLANNING.md
│   ├── THREAT_MODEL.md
│   └── VERIFICATION.md
├── .github/
│   ├── workflows/ci.yml     # GitHub Actions CI
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── dependabot.yml
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
├── docker-compose.yml
├── render.yaml
├── setup.ps1
└── README.md
```

## Testing

```powershell
# Backend
cd backend
.\.venv\Scripts\python.exe -m pytest tests/

# Frontend
cd frontend
npm test
```

## Verification

See `docs/VERIFICATION.md` for verified vs pending test results and exact commands.

## License

MIT — see `LICENSE`.

## Contributing

See `CONTRIBUTING.md` for how to contribute, report bugs, and suggest features.

## Security

See `SECURITY.md` for our security policy and responsible disclosure process.
