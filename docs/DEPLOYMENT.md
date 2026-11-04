# GitHubIQ — Deployment Guide

Deploy the backend and frontend to free-tier hosting so the app is accessible via a public URL.

## Option A: Render + Vercel (Recommended, Free)

### Prerequisites
- GitHub account with this repo pushed
- Render account (https://render.com) — free
- Vercel account (https://vercel.com) — free
- GitHub OAuth App (https://github.com/settings/developers) — free

### Step 1: Create GitHub OAuth App (Production)
1. Go to https://github.com/settings/developers → "New OAuth App"
2. Application name: `GitHubIQ`
3. Homepage URL: `https://<your-frontend>.vercel.app`
4. Authorization callback URL: `https://<your-backend>.onrender.com/api/v1/auth/github/callback`
5. Copy **Client ID** and **Client Secret**

### Step 2: Generate Secrets
```powershell
# Fernet key (backend/.env)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Session secret
# Use any random string, e.g. from a password manager
```

### Step 3: Deploy Backend on Render
1. Log in to Render → "New Web Service"
2. Connect your GitHub repo → select this repository
3. Root Directory: `backend`
4. Runtime: `Python`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Add Environment Variables:
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | `sqlite:///./data/app.db` (for MVP; see note below) |
   | `GITHUB_CLIENT_ID` | from GitHub OAuth App |
   | `GITHUB_CLIENT_SECRET` | from GitHub OAuth App |
   | `GITHUB_CALLBACK_URL` | `https://<backend>.onrender.com/api/v1/auth/github/callback` |
   | `FRONTEND_URL` | `https://<frontend>.vercel.app` |
   | `GITHUB_TOKEN_ENCRYPTION_KEY` | from step 2 |
   | `SESSION_SECRET_KEY` | from step 2 |
   | `CORS_ORIGINS` | `https://<frontend>.vercel.app` |
   | `ENVIRONMENT` | `production` |
8. Click "Create Web Service"

### Step 4: Deploy Frontend on Vercel
1. Log in to Vercel → "Add New Project"
2. Import your GitHub repo
3. Framework Preset: `Vite`
4. Root Directory: `frontend`
5. Build Command: `npm run build`
6. Output Directory: `dist`
7. Add Environment Variable:
   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://<backend>.onrender.com` |
8. Click "Deploy"

### Step 5: Update GitHub OAuth Callback
Go back to your GitHub OAuth App settings and update:
- Homepage URL: `https://<your-frontend>.vercel.app`
- Callback URL: `https://<your-backend>.onrender.com/api/v1/auth/github/callback`

### Step 6: Test
1. Open `https://<your-frontend>.vercel.app`
2. Click "Connect GitHub" → authorize → Dashboard
3. Add a repository → view analytics

---

## Option B: Docker Compose (Self-Hosted)

If you have a VPS or want to run it yourself:

```powershell
# Fill in backend/.env and frontend/.env first
docker-compose up --build
```

Then open `http://localhost:5173`.

---

## Important: SQLite Limitation on Free Hosting

Render's free tier has an **ephemeral filesystem** — any SQLite data is lost when the service restarts or spins down. For a production deployment:

1. **Create a Render PostgreSQL database** (free tier available)
2. Copy its **Internal Connection String**
3. Set `DATABASE_URL` on the backend service to that connection string
4. SQLAlchemy will automatically use PostgreSQL instead of SQLite

```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## View Your Live App

After deployment, your app will be accessible at:
- **Frontend:** `https://<your-project>.vercel.app`
- **Backend API:** `https://<your-project>.onrender.com/api/v1/health`

Share the frontend URL — anyone can use it directly.
