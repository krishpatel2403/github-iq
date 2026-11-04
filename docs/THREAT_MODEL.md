# GitHubIQ — Threat Model

> Security threat model for GitHubIQ Developer Analytics.
> Review this document before each release and after any architecture change.

---

## 1. Assets

| Asset | Sensitivity | Why it matters |
|-------|-------------|----------------|
| GitHub OAuth access tokens | High | Grants access to user's GitHub data (repos, issues, PRs) |
| User session cookies | High | Hijacking = impersonation |
| User GitHub profile data | Medium | Private emails, org membership could be exposed |
| Repository analytics data | Low–Medium | Could reveal internal repo names / activity patterns |
| Encryption key (Fernet) | Critical | Compromise = all stored tokens decryptable |
| Session signing key | Critical | Compromise = forged session cookies |

---

## 2. Trust Boundaries

```
┌─────────────┐    HTTPS    ┌──────────────┐    HTTPS    ┌─────────────┐
│   Browser   │────────────►│  Backend     │────────────►│  GitHub     │
│  (React)    │    (TLS)    │  (FastAPI)   │    (TLS)    │  API        │
└─────────────┘             └──────────────┘             └─────────────┘
       │                          │
       │ HttpOnly cookie          │ SQLite (file/Postgres)
       ▼                          ▼
  LocalStorage                  backend/data/app.db
  (none used)                   Fernet-encrypted tokens
```

**Trust boundaries:**
1. Browser ↔ Backend: HTTPS, session cookie (HttpOnly, SameSite=Lax)
2. Backend ↔ GitHub API: HTTPS, Bearer token
3. Backend ↔ Database: local file / PostgreSQL connection

---

## 3. Threats (STRIDE)

| # | Threat | STRIDE | Asset | Impact | Likelihood | Mitigation |
|---|--------|--------|-------|--------|------------|------------|
| T1 | Token theft via XSS | Information Disclosure | GitHub access token | High | Low | HttpOnly cookies prevent JS access; CSP headers |
| T2 | Session hijacking via cookie theft | Spoofing | Session cookie | High | Low | Secure flag (prod), SameSite=Lax, 7-day expiry, signed with itsdangerous |
| T3 | CSRF on OAuth callback | Spoofing | OAuth flow | Medium | Low | State parameter stored in cookie, verified on callback |
| T4 | Token exposure in logs | Information Disclosure | GitHub access token | High | Low | Never log tokens; structured logging excludes secrets |
| T5 | Database file read at rest | Information Disclosure | Encrypted tokens | Medium | Medium | Fernet encryption; key stored in env var, not in DB |
| T6 | Fernet key compromise | Elevation of Privilege | All tokens | Critical | Low | Key in env var only; rotate if leaked; `.gitignore` excludes `.env` |
| T7 | Session key forge | Spoofing | Session cookie | High | Low | Session key in env var; 7-day max age |
| T8 | GitHub API rate-limit exhaustion | Denial of Service | GitHub API access | Medium | Medium | Cache results, 15-min sync cooldown, surface 429 gracefully |
| T9 | Repo enumeration abuse | Denial of Service | Backend API | Low | Medium | Auth required for /repositories, /sync; rate limiting on /sync |
| T10 | SQL injection | Elevation of Privilege | Database | High | Low | SQLAlchemy ORM with parameterized queries; no raw SQL |
| T11 | Redirect to malicious site | Spoofing | OAuth login | Medium | Low | Redirect URLs validated; FRONTEND_URL from env only |

---

## 4. Security Controls Implemented

| Control | Implementation |
|---------|---------------|
| Encryption at rest | Fernet (symmetric, AES-128) for GitHub tokens in SQLite |
| Session signing | itsdangerous `TimestampSigner` with 7-day max age |
| Cookie security | HttpOnly, SameSite=Lax, Secure in production |
| CSRF protection | OAuth state parameter in HttpOnly cookie |
| Input validation | Pydantic v2 schemas on all request bodies/query params |
| Error handling | Structured JSON errors; no stack traces leaked to client |
| Logging | Structured JSON; tokens/secrets never logged |
| CORS | Restricted to frontend origin only (never `*`) |
| AuthZ | Session cookie required for all data endpoints |
| Dependency scanning | `pip-audit` / `npm audit` in CI |
| HTTPS | Enforced in production via reverse proxy (Render/Vercel) |

---

## 5. Residual Risks (Accepted)

| Risk | Reason |
|------|--------|
| SQLite on Render free tier | Ephemeral filesystem — data lost on restart. Mitigation: use Render PostgreSQL for production. |
| GitHub token scope `repo` | Grants read access to all repos. Users must consent. Mitigation: document scope clearly. |
| No rate limiting on /login | Authlib/OAuth flow itself is rate-limited by GitHub. |
| No refresh token flow | 7-day session is acceptable for MVP. Re-auth via OAuth after expiry. |

---

## 6. Security Testing Instructions

### Safe Self-Testing (Read-Only)

These tests do **not** modify production data and are safe to run against a local dev instance:

```powershell
# 1. Verify health endpoint
curl http://localhost:8000/api/v1/health

# 2. Verify unauthenticated endpoints return 401
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/auth/me
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/repositories
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/v1/sync/repositories
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/sync/status

# 3. Verify OAuth login redirects (302) when configured
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/auth/github/login

# 4. Verify CSRF protection: callback without state cookie returns 400
curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/v1/auth/github/callback?code=abc&state=xyz"
```

### Penetration Testing (Authorized Only)

**Do not run penetration tests against deployed Render/Vercel instances without written authorization.**

For authorized testing, use these tools against your own deployed instance:

| Tool | Purpose | Command Example |
|------|---------|-----------------|
| `owasp-zap` | Automated scan | `zap-cli quick-scan --self-start http://localhost:8000` |
| `curl` | Manual probe | See Safe Self-Testing above |
| `pip-audit` | Python dependency vulns | `pip install pip-audit && pip-audit -r backend/requirements.txt` |
| `npm audit` | Node dependency vulns | `cd frontend && npm audit` |

### Responsible Disclosure

If you find a security vulnerability, do not open a public GitHub issue. Instead, contact the maintainer directly or use GitHub's private vulnerability reporting.

---

## 7. Security Checklist (Pre-Release)

- [ ] `.env` files are in `.gitignore` and not committed
- `GITHUB_TOKEN_ENCRYPTION_KEY` is a real Fernet key, not a placeholder
- `SESSION_SECRET_KEY` is a strong random string (32+ chars)
- `ENVIRONMENT=production` in production
- `CORS_ORIGINS` lists only the production frontend URL
- `SESSION_COOKIE_NAME` uses `secure=true` behind HTTPS
- Database URL uses PostgreSQL (not SQLite) for production
- `pip-audit` and `npm audit` show no critical vulnerabilities
- All API endpoints require authentication (except `/health`)
- Error responses don't leak stack traces or token fragments
