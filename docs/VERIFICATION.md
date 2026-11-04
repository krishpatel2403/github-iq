# GitHubIQ — Verification Commands

> This document distinguishes **verified** results (actually run and passing)
> from **pending** results (need to be run by you).

---

## Backend Verification

### Python Environment

| Command | Expected Result | Status |
|---------|----------------|--------|
| `backend\.venv\Scripts\python.exe --version` | `Python 3.13.1` | ✅ Verified |
| `backend\.venv\Scripts\pip list` | Shows fastapi, sqlalchemy, alembic, httpx, authlib, cryptography, pytest | ✅ Verified |

### Backend Tests

| Command | Expected Result | Status |
|---------|----------------|--------|
| `backend\.venv\Scripts\python.exe -m pytest tests/ -v` | `17 passed` | ✅ Verified (Oct 29 2026) |
| `backend\.venv\Scripts\python.exe -m ruff check app tests` | `All checks passed!` | ✅ Verified |
| `backend\.venv\Scripts\python.exe -m ruff format --check app tests` | `31 files already formatted` | ✅ Verified |

### Backend Live Smoke Test

Start the server: `backend\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000`

| Command | Expected Result | Status |
|---------|----------------|--------|
| `curl http://localhost:8000/api/v1/health` | `{"status":"ok","database":"healthy"}` | ✅ Verified |
| `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/auth/me` | `401` | ✅ Verified |
| `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/auth/github/login` | `302` | ✅ Verified |
| `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/repositories` | `401` | ✅ Verified |
| `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/v1/sync/repositories` | `401` | ✅ Verified |

> ⚠️ Pending: Full OAuth flow test requires real GitHub OAuth App credentials in `backend/.env`.

### Backend Import Check

| Command | Expected Result | Status |
|---------|----------------|--------|
| `backend\.venv\Scripts\python.exe -c "import app.main, app.api.v1.auth, app.api.v1.repositories, app.api.v1.sync, app.services.github, app.crud.user; print('IMPORTS_OK')"` | `IMPORTS_OK` | ✅ Verified |

---

## Frontend Verification

### Node Environment

| Command | Expected Result | Status |
|---------|----------------|--------|
| `node --version` | `v24.19.0` | ✅ Verified |
| `npm --version` | `11.17.0` | ✅ Verified |

### Frontend Tests

| Command | Expected Result | Status |
|---------|----------------|--------|
| `cd frontend && npm test` | `17 passed` across 4 test files | ✅ Verified |
| `cd frontend && npx eslint src --ext ts,tsx --max-warnings 0` | No output (clean) | ✅ Verified |
| `cd frontend && npx tsc --noEmit` | No output (clean) | ✅ Verified |
| `cd frontend && npm run build` | `dist/` directory created, ~610 kB bundle | ✅ Verified |

---

## Pending: End-to-End Integration Test

The following full flow test requires a GitHub OAuth App and is **pending** your setup:

1. Create GitHub OAuth App at https://github.com/settings/developers
   - Callback URL: `http://localhost:8000/api/v1/auth/github/callback`
2. Generate Fernet key and session secret
3. Fill in `backend/.env` with real values
4. Run both servers (backend on 8000, frontend on 5173)
5. Open `http://localhost:5173`
6. Click "Connect GitHub" → authorize → Dashboard
7. Add repository (e.g. `facebook/react`)
8. View analytics page
9. Click "Refresh" → verify sync completes

---

## Pending: Production Deployment Test

After deploying to Render + Vercel:

| Command | Expected Result |
|---------|----------------|
| `curl https://<backend>.onrender.com/api/v1/health` | `{"status":"ok","database":"healthy"}` |
| `curl https://<frontend>.vercel.app` | Returns HTML (React app) |
| Open `https://<frontend>.vercel.app` in browser | Login page loads |

---

## Dependency Auditing

| Command | Purpose |
|---------|---------|
| `cd backend && pip install pip-audit && pip-audit -r requirements.txt -r requirements-dev.txt` | Python dependency vulnerability scan |
| `cd frontend && npm audit` | Node.js dependency vulnerability scan |
| `cd frontend && npm audit fix --force` | Auto-fix vulnerable packages (use with caution) |

> ⚠️ Pending: Run dependency audits before first production deployment.

---

## How to Run the Full Verification Suite

```powershell
# Backend
cd backend
.\.venv\Scripts\python.exe -m pytest tests/
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m ruff format --check app tests

# Frontend
cd frontend
npm test
npx eslint src --ext ts,tsx --max-warnings 0
npx tsc --noEmit
npm run build
```

**Expected outcome:** All tests pass, lint clean, types clean, build succeeds.
