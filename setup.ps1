# =============================================================================
# GitHubIQ — Development environment setup (Windows PowerShell)
# =============================================================================
# Run:  .\setup.ps1
# Prerequisites: Python 3.11+, Node.js 18+, Git
# Notes:
#   - If npm is blocked by execution policy, run:  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#   - Or invoke npm via:  cmd /c npm <command>
# =============================================================================

$ErrorActionPreference = "Stop"
$ROOT = Resolve-Path .
$BACKEND = "$ROOT\backend"
$FRONTEND = "$ROOT\frontend"

Write-Host "== GitHubIQ setup ==" -ForegroundColor Cyan

# --- 1. Verify prerequisites -------------------------------------------------
function Test-Command($cmd) {
  try { & $cmd --version | Out-Null; return $true } catch { return $false }
}

Write-Host "`n[1/6] Checking prerequisites..." -ForegroundColor Yellow
if (-not (Test-Command python)) { Write-Error "Python not found. Install from https://python.org"; exit 1 }
if (-not (Test-Command node)) { Write-Error "Node.js not found. Install from https://nodejs.org"; exit 1 }
if (-not (Test-Command git)) { Write-Error "Git not found. Install from https://git-scm.com"; exit 1 }

# npm via cmd because npm.ps1 shim is blocked by execution policy on some Windows machines
$npmVersion = cmd /c "npm --version" 2>$null
if (-not $npmVersion) { Write-Error "npm not usable. Try: Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned"; exit 1 }

Write-Host "   Python: $(python --version)" -ForegroundColor Green
Write-Host "   Node:   $(node --version)" -ForegroundColor Green
Write-Host "   Git:    $(git --version)" -ForegroundColor Green
Write-Host "   npm:    $npmVersion" -ForegroundColor Green

# --- 2. Initialize git repository -------------------------------------------
Write-Host "`n[2/6] Initializing Git repository..." -ForegroundColor Yellow
if (-not (Test-Path "$ROOT\.git")) {
  git init
  git branch -m main
  Write-Host "   Git initialized (branch: main)" -ForegroundColor Green
} else {
  Write-Host "   Git repo already exists" -ForegroundColor Green
}

# --- 3. Backend virtual environment + dependencies --------------------------
Write-Host "`n[3/6] Setting up backend (Python venv)..." -ForegroundColor Yellow
$VENV = "$BACKEND\.venv"
if (-not (Test-Path "$VENV\Scripts\activate")) {
  python -m venv $VENV
  Write-Host "   venv created" -ForegroundColor Green
}
& "$VENV\Scripts\pip install" --upgrade pip | Out-Null
if (Test-Path "$BACKEND\requirements.txt") {
  & "$VENV\Scripts\pip install" -r "$BACKEND\requirements.txt"
  Write-Host "   Backend dependencies installed" -ForegroundColor Green
}
if (Test-Path "$BACKEND\requirements-dev.txt") {
  & "$VENV\Scripts\pip install" -r "$BACKEND\requirements-dev.txt"
  Write-Host "   Backend dev dependencies installed" -ForegroundColor Green
}

# --- 4. Frontend dependencies -----------------------------------------------
Write-Host "`n[4/6] Setting up frontend (npm install)..." -ForegroundColor Yellow
cmd /c "cd /d `"$FRONTEND`" && npm install" | Out-Null
Write-Host "   Frontend dependencies installed" -ForegroundColor Green

# --- 5. Environment files ---------------------------------------------------
Write-Host "`n[5/6] Preparing environment files..." -ForegroundColor Yellow
foreach ($src in @("$ROOT\.env.example", "$BACKEND\.env.example", "$FRONTEND\.env.example")) {
  $dest = $src -replace "\.example$", ""
  if (-not (Test-Path $dest)) {
    Copy-Item $src $dest
    Write-Host "   Created: $dest" -ForegroundColor Green
  } else {
    Write-Host "   Skipped (exists): $dest" -ForegroundColor Gray
  }
}
Write-Host "   IMPORTANT: Edit backend/.env and frontend/.env with your GitHub OAuth keys before running the app." -ForegroundColor Red

# --- 6. Next steps ----------------------------------------------------------
Write-Host "`n== Setup complete! ==" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the backend:" -ForegroundColor Yellow
Write-Host "  cd backend"
Write-Host "  .\.venv\Scripts\activate"
Write-Host "  uvicorn app.main:app --reload --port 8000"
Write-Host ""
Write-Host "To run the frontend:" -ForegroundColor Yellow
Write-Host "  cd frontend"
Write-Host "  cmd /c npm run dev"
Write-Host ""
Write-Host "Then open: http://localhost:5173"
Write-Host ""
