# Git pre-push hook for regression testing (PowerShell version)
# 
# This hook prevents pushing to remote if any previously passing test fails.
#
# Installation:
#   Copy this file to .git/hooks/pre-push
#   Make sure PowerShell execution policy allows scripts

$ErrorActionPreference = "Stop"

# Get the project root directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

Set-Location $projectRoot

# Check if baseline exists
if (-not (Test-Path ".test_baseline.json")) {
    Write-Host "⚠️  No test baseline found." -ForegroundColor Yellow
    Write-Host "   Run 'python scripts/regression_test.py update' to create a baseline."
    Write-Host ""
    Write-Host "   Proceeding with push (no baseline to check against)..." -ForegroundColor Yellow
    exit 0
}

# Run regression check
Write-Host "Running regression tests..." -ForegroundColor Cyan
python scripts/regression_test.py run

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Regression tests failed. Push aborted." -ForegroundColor Red
    Write-Host ""
    Write-Host "To fix:"
    Write-Host "  1. Fix the failing tests"
    Write-Host "  2. Run 'python scripts/regression_test.py update' to update baseline"
    Write-Host "  3. Try pushing again"
    Write-Host ""
    Write-Host "To bypass this check (not recommended):"
    Write-Host "  git push --no-verify"
    exit 1
}

Write-Host "✅ Regression tests passed. Proceeding with push..." -ForegroundColor Green
exit 0

