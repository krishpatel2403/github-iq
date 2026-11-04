# GitHubIQ — Git Commands Reference

Exact commands for initializing, branching, committing, remote setup, and pushing.

## Prerequisites

Run these from the project root: `C:\Users\krish\Downloads\GITHUB-UI_Agent`

## 1. Initialize Git Repository (Already Done)

```powershell
git init -b main
```

## 2. Check Status

```powershell
git status
git log --oneline
```

## 3. Stage All Files

```powershell
git add .
```

## 4. Create the Initial Commit

```powershell
git commit -m "feat: initial project scaffold

- Backend: FastAPI, SQLAlchemy 2.0, Alembic, SQLite
- Auth: GitHub OAuth with Fernet-encrypted tokens
- Frontend: React 18, Vite, TypeScript, Tailwind CSS
- CI: GitHub Actions workflow
- Deployment: Dockerfiles, Render config, Vercel config
- Docs: README, deployment guide, threat model, verification"
```

## 5. Create a Feature Branch

```powershell
git checkout -b feature/your-feature-name
```

## 6. Switch Back to Main

```powershell
git checkout main
```

## 7. Merge a Feature Branch

```powershell
git merge feature/your-feature-name
```

## 8. Delete a Feature Branch (After Merge)

```powershell
git branch -d feature/your-feature-name
```

## 9. Add a Remote (GitHub)

Replace `<your-username>` with your GitHub username:

```powershell
git remote add origin https://github.com/<your-username>/github-iq.git
```

## 10. Verify Remote

```powershell
git remote -v
```

## 11. Push to GitHub

First push (sets upstream):

```powershell
git push -u origin main
```

Subsequent pushes:

```powershell
git push
```

## 12. Push a Tag (Release)

```powershell
git tag v0.1.0
git push origin v0.1.0
```

## 13. Pull Latest Changes

```powershell
git pull origin main
```

## 14. View Remote URL

```powershell
git remote get-url origin
```

## 15. Remove Remote (if needed)

```powershell
git remote remove origin
```

---

## Suggested Commit Messages

| Type | Example |
|------|---------|
| Feature | `feat: add repository analytics endpoint` |
| Fix | `fix: handle expired OAuth state cookie` |
| Docs | `docs: update deployment guide for Render` |
| Test | `test: add RepoCard unit tests` |
| Style | `style: format backend code with ruff` |
| Refactor | `refactor: extract GitHubClient into service module` |
| Security | `security: rotate Fernet key validation on startup` |
| Chore | `chore: update Python dependencies` |

## Suggested Release Tags

| Version | Meaning | Command |
|---------|---------|---------|
| `v0.1.0` | MVP release | `git tag v0.1.0 && git push origin v0.1.0` |
| `v0.2.0` | GitHub API sync + analytics | `git tag v0.2.0 && git push origin v0.2.0` |
| `v0.3.0` | Frontend integration complete | `git tag v0.3.0 && git push origin v0.3.0` |
| `v1.0.0` | Production-ready release | `git tag v1.0.0 && git push origin v1.0.0` |

---

## Never Do These

- ❌ Never commit `.env` files (they contain secrets)
- ❌ Never commit `node_modules/`, `.venv/`, `__pycache__/`
- ❌ Never push secrets, tokens, or keys
- ❌ Never force-push to `main` without team consensus
