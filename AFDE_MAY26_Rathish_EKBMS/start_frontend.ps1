# --------------------------------------------------------------
# EKBMS — Frontend launcher (Windows PowerShell)
# --------------------------------------------------------------
# Ensures npm uses PowerShell as its script shell (cmd is disabled
# on this machine), installs deps on first run, then starts Vite.
#
# Run from the repo root:
#     .\start_frontend.ps1
# --------------------------------------------------------------

$ErrorActionPreference = "Stop"

Write-Host "==> Pointing npm at powershell.exe (one-time, safe to repeat)..." -ForegroundColor Cyan
npm config set script-shell "powershell.exe" | Out-Null

Push-Location -Path "$PSScriptRoot\frontend"
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "==> Installing npm dependencies..." -ForegroundColor Cyan
        npm install
    } else {
        Write-Host "==> Dependencies already installed (node_modules exists)." -ForegroundColor DarkGray
    }

    Write-Host "==> Starting Vite dev server on http://localhost:5173 ..." -ForegroundColor Cyan
    Write-Host "    Press Ctrl+C to stop." -ForegroundColor DarkGray
    npm run dev
}
finally {
    Pop-Location
}
