# --------------------------------------------------------------
# EKBMS — Backend launcher (Windows PowerShell)
# --------------------------------------------------------------
# Installs deps on first run, seeds the SQLite DB if empty, and
# starts the FastAPI app via uvicorn with auto-reload.
#
# Run from the repo root:
#     .\start_backend.ps1
# --------------------------------------------------------------

$ErrorActionPreference = "Stop"

Write-Host "==> Installing Python dependencies..." -ForegroundColor Cyan
py -m pip install --quiet -r requirements.txt

Write-Host "==> Seeding database (idempotent)..." -ForegroundColor Cyan
py -m backend.seed

Write-Host "==> Starting FastAPI on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Write-Host "    Press Ctrl+C to stop." -ForegroundColor DarkGray
py -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
