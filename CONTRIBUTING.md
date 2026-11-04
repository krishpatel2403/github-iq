# Contributing to GitHubIQ

Thank you for considering a contribution to GitHubIQ! We welcome bug reports,
feature requests, and pull requests.

## Code of Conduct

Please be respectful and constructive in all interactions. Harassment,
discrimination, or toxic behavior will not be tolerated.

## How to Contribute

### 1. Fork and Clone

```powershell
git clone https://github.com/<your-username>/github-iq.git
cd github-iq
```

### 2. Set Up the Development Environment

Follow the setup instructions in `README.md` and `docs/DEPLOYMENT.md`.

### 3. Create a Branch

```powershell
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 4. Make Changes

- Follow the existing code style.
- Backend: Python, FastAPI, SQLAlchemy. Lint with `ruff`.
- Frontend: React, TypeScript, Tailwind. Lint with `eslint`, format with `prettier`.
- Add tests for new features.
- Update documentation if needed.

### 5. Verify Locally

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

### 6. Commit and Push

```powershell
git add .
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
```

### 7. Open a Pull Request

Open a PR against `main`. Include:
- A clear title and description
- Screenshots for UI changes
- Reference to any related issue

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short summary>

<optional body>
<optional footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `security`, `perf`

Examples:
- `feat: add repository sync status endpoint`
- `fix: handle expired OAuth state cookie`
- `docs: update deployment guide for Render`
- `test: add RepoCard unit tests`
- `security: rotate Fernet key on startup if invalid`

## Reporting Bugs

Use the bug report template in `.github/ISSUE_TEMPLATE/bug_report.md`.

## Suggesting Features

Use the feature request template in `.github/ISSUE_TEMPLATE/feature_request.md`.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
