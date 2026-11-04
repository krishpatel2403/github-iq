# GitHubIQ — Developer Analytics | Phase 1: Discovery & Planning

> **Status:** Planning complete — ready for Phase 2 (Development Environment)
> **Owner:** You (product) + Me (senior engineer / architect)
> **Assumptions:** Windows 10/11, VS Code, no existing repo, Python + React stack

---

## 1. Problem, Target Users, and Real-World Use Cases

### Problem
GitHub is the de-facto portfolio for developers, but its native UI shows raw data (stars, forks, issue counts) without **context, trends, or comparative insight**. Engineering managers can't easily see team velocity; open-source maintainers can't tell which repositories are stagnating; freelancers and job-seekers can't present their GitHub activity as an analytics-backed resume. Existing GitHub analytics tools are either enterprise-grade (expensive) or read-only dashboards that don't let you connect your own account and track the repositories *you* care about.

### Target Users
| User | What they need | Why current tools fall short |
|------|---------------|------------------------------|
| Freelance / job-seeking developers | A shareable, analytics-backed view of their GitHub profile and top repos | GitHub profile shows raw counts only |
| Open-source maintainers | Repo health: issue/PR velocity, contributor trends, language breakdown | Must manually check multiple repo pages |
| Engineering leads / small dev teams | Team repo activity across multiple repos, sprint-style velocity signals | Enterprise GitHub Advanced Security is overpriced for small teams |
| Recruiters / technical hiring managers | Candidate code activity summarized consistently | Inconsistent across candidate profiles |

### Real-World Use Cases (MVP scope)
1. **Connect GitHub account** via OAuth; see profile stats (total stars, repos, followers, account age).
2. **Add a repository** to track; view stars/forks/watchers, open vs. closed issues, open vs. merged PRs, primary language, last activity.
3. **Refresh data** on demand (GitHub API is not real-time; we cache and re-sync).
4. **Dashboard** showing key metrics for all connected repos with loading/empty/error states.
5. **Compare two repositories** side by side (stars, issues, PRs, languages) — stretch MVP depending on time.

---

## 2. Feature Definitions

### MVP (v0.1.0) — must ship
| ID | Feature | Acceptance criteria |
|----|---------|---------------------|
| M1 | GitHub OAuth login / logout | User can connect a GitHub account; token stored encrypted; session persists across refresh |
| M2 | Connected GitHub profile view | Shows username, avatar, public repos, stars, followers, following, account age |
| M3 | Repository discovery + connect | Search GitHub repositories; add one to tracking; list tracked repositories |
| M4 | Repository analytics page | Stars, forks, watchers, open/closed issues, open/merged PRs, top language, last pushed date |
| M5 | Dashboard | Aggregated cards for all tracked repos (total stars, total issues, recent activity) |
| M6 | Data sync / refresh | Manual "Refresh" button triggers GitHub API fetch; shows last-synced timestamp |
| M7 | Loading, empty, error states | Every async action has a spinner, empty illustration, or error toast with retry |
| M8 | Responsive UI | Works on mobile (≥375px), tablet, and desktop |

### Advanced (v0.2.0–v0.4.0) — post-MVP
- Multi-repo comparison chart (stars over time, issue velocity)
- Organization/team view (requires GitHub App or org-scoped token)
- Weekly digest email summary (resend/SendGrid free tier)
- Contributor leaderboard per repository
- "Repo health score" (activity freshness, issue response time, PR merge ratio)
- Dark mode

### Optional future enhancements (v1.0.0+)
- GitHub App installation for org-wide onboarding (no per-user OAuth)
- Pull-request sentiment / code-review velocity
- CI/CD integration (deploy status badges in dashboard)
- Export analytics to PDF/CSV
- Mobile React Native companion

---

## 3. Technology Stack (Free / Low-Cost)

| Layer | Choice | Version | Justification | Cost |
|-------|--------|---------|---------------|------|
| Language (backend) | Python | 3.11+ | Modern, async-ready, huge ecosystem, easy to hire/learn | Free |
| Web framework | FastAPI | latest | Automatic OpenAPI/Swagger docs, Pydantic validation, high performance, async | Free (MIT) |
| ORM + migrations | SQLAlchemy 2.0 + Alembic | latest | SQLite → PostgreSQL upgrade path, type-safe models | Free |
| Database (MVP) | SQLite | built-in | Zero-config, single file, production-ready for low-to-medium traffic | Free |
| Auth | GitHub OAuth (Authlib) | latest | Industry standard, no password storage, users bring their own identity | Free |
| Token encryption | cryptography (Fernet) | latest | Encrypt GitHub access tokens at rest; key from env var | Free |
| HTTP client (backend) | httpx | latest | Async/sync, modern replacement for requests | Free |
| Config | python-dotenv | latest | 12-factor env vars; no secrets in code | Free |
| Language (frontend) | TypeScript | 5.x | Catches bugs early; self-documenting | Free |
| Frontend framework | React | 18 | Component model, huge ecosystem | Free (MIT) |
| Build tool | Vite | latest | Fast HMR, lean production bundles | Free (MIT) |
| Styling | Tailwind CSS | latest | Utility-first, responsive by design, no custom CSS bloat | Free (MIT) |
| Charts | Recharts | latest | React-native, declarative, accessible SVG charts | Free (MIT) |
| HTTP client (frontend) | axios | latest | Request/response interceptors for auth tokens | Free (MIT) |
| State | React hooks + context | built-in | Avoids Redux complexity for MVP | Free |
| Testing (backend) | pytest + httpx | latest | Standard Python testing; httpx for mocking FastAPI | Free |
| Testing (frontend) | Vitest + React Testing Library | latest | Vite-native, fast, Jest-compatible | Free |
| Linting (backend) | ruff | latest | Fast Python lint + format (replaces flake8/black/isort) | Free |
| Linting (frontend) | ESLint + Prettier | latest | Standard JS/TS lint + format | Free |
| Type checks (frontend) | tsc | latest | TypeScript compiler check in CI | Free |
| CI / CD | GitHub Actions | built-in | Free for public repos; 2,000 min/month for private | Free tier |

### Total estimated cost: $0/month for MVP
- GitHub REST API: 5,000 requests/hour with authenticated token (free); 60/hour unauthenticated.
- Hosting: free tiers of Render (backend) + Vercel/Netlify (frontend), or self-host on your Windows machine.
- Domain: optional (github.io subdomain is free).

---

## 4. Architecture, Database Design, API Routes, Data Flow, Security

### 4.1 High-level architecture (monorepo, two services)

```
github-iq/
├── backend/              # FastAPI (Python) — port 8000
│   ├── app/
│   ├── tests/
│   └── ...
└── frontend/             # React + Vite (TypeScript) — port 5173
    ├── src/
    └── ...
```

- **Backend**: stateless FastAPI service. All persistent state in SQLite (`data/app.db`). GitHub access tokens encrypted at rest with Fernet (key in `GITHUB_TOKEN_ENCRYPTION_KEY`).
- **Frontend**: React SPA consuming `http://localhost:8000/api/v1` in dev; proxied to same origin in production.
- **Communication**: JSON over HTTPS. CORS restricted to frontend origin.

### 4.2 Database design (SQLite via SQLAlchemy 2.0)

```text
users
- id: UUID PK
- github_id: INTEGER UNIQUE (GitHub user id)
- username: VARCHAR (GitHub login)
- email: VARCHAR
- avatar_url: VARCHAR
- created_at, updated_at: DATETIME

github_connections
- id: UUID PK
- user_id: FK → users.id
- encrypted_access_token: BLOB (Fernet-encrypted)
- token_scope: VARCHAR
- created_at, updated_at: DATETIME

repositories
- id: UUID PK
- github_repo_id: INTEGER UNIQUE
- full_name: VARCHAR (owner/name)
- owner_login: VARCHAR
- description: TEXT
- html_url: VARCHAR
- stargazers_count: INTEGER
- forks_count: INTEGER
- watchers_count: INTEGER
- open_issues_count: INTEGER
- default_branch: VARCHAR
- language: VARCHAR
- pushed_at: DATETIME (GitHub)
- synced_at: DATETIME (our last sync)
- created_at, updated_at: DATETIME

repository_metrics_snapshot
- id: UUID PK
- repository_id: FK → repositories.id
- snapshot_at: DATETIME
- stars: INTEGER
- forks: INTEGER
- open_issues: INTEGER
- closed_issues: INTEGER
- open_prs: INTEGER
- merged_prs: INTEGER

sync_logs
- id: UUID PK
- user_id: FK → users.id
- status: VARCHAR (pending/completed/failed)
- started_at, completed_at: DATETIME
- records_fetched: INTEGER
- error_message: TEXT
```

**Why this schema:** Keeps GitHub raw data in `repositories` and time-series snapshots in `repository_metrics_snapshot` so we can show trends later without re-calling GitHub. All timestamps stored in UTC.

### 4.3 API routes (backend)

| Method | Route | Description | Auth |
|--------|-------|-------------|------|
| GET | `/health` | Health check (db + github API reachability) | None |
| GET | `/api/v1/auth/me` | Current authenticated user profile | Session cookie |
| POST | `/api/v1/auth/github/login` | Redirect to GitHub OAuth authorize URL | None |
| GET | `/api/v1/auth/github/callback` | OAuth callback; exchange code for token; create user/connection | None |
| POST | `/api/v1/auth/logout` | Clear session | Session cookie |
| GET | `/api/v1/repositories` | List tracked repositories for current user | Session cookie |
| POST | `/api/v1/repositories` | Add a repository to track (by full_name) | Session cookie |
| GET | `/api/v1/repositories/{repo_id}/analytics` | Repo analytics + latest metrics snapshot | Session cookie |
| POST | `/api/v1/sync/repositories` | Trigger manual sync of tracked repos from GitHub API | Session cookie |
| GET | `/api/v1/sync/status` | Latest sync log status | Session cookie |
| GET | `/api/v1/users/{username}/profile` | Public GitHub profile summary (rate-limit aware) | None (optional) |

OpenAPI docs auto-generated at `/docs` (dev only; disabled in production).

### 4.4 Data flow (typical request: view repo analytics)

```
1. Browser → GET /api/v1/repositories/{id}/analytics (session cookie attached)
2. FastAPI → validates session → loads user + repo from SQLite
3. FastAPI → checks `synced_at`; if stale (> 15 min) or `force=1`:
      a. Reads encrypted GitHub token from github_connections
      b. Decrypts with Fernet key
      c. httpx GET https://api.github.com/repos/{owner}/{name} (Authorization: Bearer token)
      d. httpx GET .../issues, .../pulls, .../languages
      e. Upserts repositories row + inserts repository_metrics_snapshot
      f. Updates sync_logs
4. FastAPI → returns JSON analytics payload
5. Browser → renders Recharts line/card components
6. On 401/403/429 from GitHub → backend maps to user-friendly error (token expired / rate limited)
```

### 4.5 Security considerations

| Area | Control |
|------|---------|
| Secrets | `.env` only; never committed; `.env.example` committed with placeholder values |
| Token at rest | Fernet symmetric encryption; `GITHUB_TOKEN_ENCRYPTION_KEY` = 32-urlsafe-base64 bytes |
| Sessions | HttpOnly, SameSite=Lax, Secure cookies in production; signed session via itsdangerous/itsdangerous-style or FastAPI session middleware |
| CORS | `allow_origins` restricted to frontend URL; no `*` in production |
| Rate limiting | GitHub API: respect `X-RateLimit-Remaining`; backend endpoint rate limit (slowapi) on `/sync` to prevent abuse |
| Input validation | Pydantic v2 schemas on all request bodies/query params |
| Error handling | No stack traces or token leakage in client responses; structured `{error, code, message}` |
| Logging | Structured JSON logging; never log access tokens or auth codes |
| Headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer` |
| Dependencies | `pip-audit` / `safety` for Python; `npm audit` for Node; Dependabot in CI |

### Threat model (summary, Phase 4 detail)
1. **Token theft** — mitigated by encryption-at-rest + HttpOnly cookies + short OAuth scopes (`read:user`, `repo`).
2. **GitHub rate-limit exhaustion** — mitigated by caching, sync cooldown, and surfacing `429` gracefully.
3. **Repo enumeration abuse** — mitigated by requiring auth for list/sync endpoints and rate-limiting sync.
4. **XSS / CSRF** — mitigated by HttpOnly cookies, SameSite=Lax, CSP headers, React auto-escaping.

---

## 5. Milestone-Based Roadmap

| Milestone | Goal | Completion criteria (must be true before starting next) |
|-----------|------|--------------------------------------------------------|
| **M1** | Project scaffolding | Repo initialized; `backend/` and `frontend/` exist; `.env.example`, `.gitignore`, `README.md` created; `make install` (or setup script) runs cleanly; `uvicorn` dev server and `vite` dev server both start |
| **M2** | Backend core | FastAPI app factory, SQLAlchemy 2.0 models, Alembic migrations, `/health` endpoint returns 200, Pydantic settings with env validation |
| **M3** | GitHub OAuth + secure tokens | OAuth authorize/callback flow works; encrypted token stored/retrieved; `/api/v1/auth/me` returns connected user |
| **M4** | GitHub API client + sync | `GitHubClient` wraps httpx with auth + rate-limit handling; repository upsert + metrics snapshot works; `/sync/repositories` returns records fetched |
| **M5** | Analytics API | `/repositories`, `/repositories/{id}/analytics`, `/sync/status` return validated responses; error cases return structured JSON |
| **M6** | Frontend shell | Vite + React + Tailwind + Recharts; login page, dashboard, repo analytics page; loading/empty/error components |
| **M7** | Full integration | Frontend calls backend via axios with auth interceptor; end-to-end flow (login → add repo → view analytics → refresh) works end-to-end |
| **M8** | Quality & CI | pytest + httpx backend tests (≥70% coverage), Vitest + RTL frontend tests, ruff lint/format, ESLint/Prettier, tsc type check, GitHub Actions workflow running lint+test on push |
| **M9** | Deployment prep | `Dockerfile` (optional but recommended), `docker-compose.yml` for local prod-like run, env var docs, deploy guide for Render + Vercel, health check endpoint verified |

**Estimated effort:** 2–3 weekends (≈25–35 hours) for an experienced developer; 1–2 weeks part-time if learning as you go.

---

## 6. API Keys, Dependencies, Hardware Requirements, and Costs

### API keys / secrets (all free)
| Secret | Where from | Used for | Env var name |
|--------|-----------|----------|--------------|
| GitHub OAuth Client ID | https://github.com/settings/developers → New OAuth App | OAuth authorize URL | `GITHUB_CLIENT_ID` |
| GitHub OAuth Client Secret | Same app settings | Exchange code for token | `GITHUB_CLIENT_SECRET` |
| Fernet encryption key | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` | Encrypt GitHub tokens at rest | `GITHUB_TOKEN_ENCRYPTION_KEY` |
| Session secret | `openssl rand -hex 32` | Sign session cookies | `SESSION_SECRET_KEY` |
| GitHub OAuth callback URL | GitHub App settings | `http://localhost:8000/api/v1/auth/github/callback` (dev) | `GITHUB_CALLBACK_URL` |

### Hardware requirements (development)
- OS: Windows 10/11 (64-bit)
- RAM: 4 GB minimum, 8 GB recommended
- Disk: 2 GB free
- Python: 3.11 or 3.12
- Node.js: 18 LTS or 20 LTS
- Git: 2.x

### Potential costs (MVP = $0)
| Item | Free tier limit | When you'd pay |
|------|----------------|----------------|
| GitHub REST API | 5,000 req/hr per authenticated user | Never for personal/small-team use |
| Render web service | 750 hrs/month, spins down after inactivity | Custom domain / always-on |
| Vercel / Netlify | Unlimited bandwidth (hobby) | Custom domain, team seats |
| Domain name | N/A | ~$12/year if you buy one |

---

## 7. Phase 1 Verification Checklist

Before moving to Phase 2, confirm:

- [ ] Problem statement and use cases are clear to you
- [ ] MVP feature list fits in one weekend of implementation
- [ ] You accept the tech stack (Python/FastAPI + SQLite; React/Vite/Tailwind)
- [ ] You have a free GitHub account to create an OAuth App later
- [ ] Windows machine has Python 3.11+ and Node 18+ (we will verify in Phase 2)

## Next Action

**Phase 2 — Development Environment:** I will give exact installation commands, verify Python/Node/Git, initialize the Git repo, create the virtual environment, set up the folder structure, `.gitignore`, `.env.example`, dependency manifests, and setup scripts.

**Reply when you're ready**, or say `CONTINUE` to proceed directly to Phase 2. If you'd like to change any MVP feature or the tech stack, tell me now before we scaffold.
