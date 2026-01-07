# PowerShell script to create and activate a virtual environment
# Run this with: .\setup_venv.ps1

Write-Host "Creating virtual environment..."
python -m venv venv

Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "Virtual environment activated!"
Write-Host "To activate in future sessions, run: .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Installing dependencies (if requirements.txt exists)..."
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "No requirements.txt found. Install packages manually as needed."
}

