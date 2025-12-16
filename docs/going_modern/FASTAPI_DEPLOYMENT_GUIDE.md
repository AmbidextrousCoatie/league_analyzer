# FastAPI Deployment Guide - Windows 11 Dev + Linux Production

**Context:** Development on Windows 11, deployment on Linux VM

---

## Quick Answer

FastAPI runs the same way on both Windows and Linux using **Uvicorn** (ASGI server).

```bash
# Same command on both Windows and Linux
uvicorn main:app --reload  # Development
uvicorn main:app --host 0.0.0.0 --port 8000  # Production
```

---

## Development: Windows 11

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install FastAPI and Uvicorn
pip install fastapi uvicorn[standard]
```

### Running Development Server

```bash
# Basic
uvicorn main:app --reload

# With specific host/port
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# With auto-reload on file changes
uvicorn main:app --reload --reload-dir ./app
```

**What `--reload` does:**
- Automatically restarts server on code changes
- Only for development (don't use in production)

### Development Script

Create `run_dev.py`:
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload on changes
        reload_dirs=["./app", "./domain", "./application"],  # Watch these directories
        log_level="info"
    )
```

Run with:
```bash
python run_dev.py
```

---

## Production: Linux VM

### Installation (Same as Windows)

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux)
source venv/bin/activate

# Install FastAPI and Uvicorn
pip install fastapi uvicorn[standard]
```

### Option 1: Direct Uvicorn (Simple)

```bash
# Run directly
uvicorn main:app --host 0.0.0.0 --port 8000

# With workers (multiple processes)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Pros:**
- Simple
- Good for small deployments

**Cons:**
- No automatic restart on crash
- No process management
- Manual worker management

---

### Option 2: Systemd Service (Recommended for Linux)

Create `/etc/systemd/system/league-analyzer.service`:

```ini
[Unit]
Description=League Analyzer FastAPI Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/league_analyzer
Environment="PATH=/path/to/league_analyzer/venv/bin"
ExecStart=/path/to/league_analyzer/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start league-analyzer

# Enable on boot
sudo systemctl enable league-analyzer

# Check status
sudo systemctl status league-analyzer

# View logs
sudo journalctl -u league-analyzer -f
```

**Pros:**
- Automatic restart on crash
- Starts on boot
- Process management
- Logging via journalctl

---

### Option 3: Gunicorn + Uvicorn Workers (Production-Ready)

**Why:** Gunicorn is a process manager, Uvicorn is the ASGI server.

```bash
# Install
pip install gunicorn

# Run with Uvicorn workers
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

**With systemd:**
```ini
[Service]
ExecStart=/path/to/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/league-analyzer/access.log \
    --error-logfile /var/log/league-analyzer/error.log
```

**Pros:**
- Process management
- Worker management
- Better for production
- Graceful restarts

---

### Option 4: Docker (Cross-Platform)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Build and run:**
```bash
# Build
docker build -t league-analyzer .

# Run
docker run -d -p 8000:8000 --name league-analyzer league-analyzer

# With docker-compose
docker-compose up -d
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./database:/app/database
    environment:
      - DATABASE_PATH=/app/database/db_real.csv
    restart: unless-stopped
```

**Pros:**
- Same environment on Windows and Linux
- Easy deployment
- Isolation
- Easy scaling

---

## Windows-Specific Considerations

### 1. Path Separators

FastAPI/Python handles this automatically, but be aware:

```python
# Works on both Windows and Linux
from pathlib import Path
data_path = Path("database") / "data" / "db_real.csv"
```

### 2. Line Endings

Git usually handles this, but if issues:

```bash
# In .gitattributes
* text=auto
*.py text eol=lf
```

### 3. File Permissions

Windows doesn't have Unix permissions, but Linux does:

```python
# Use pathlib for cross-platform
from pathlib import Path
data_file = Path("database/data/db_real.csv")
if data_file.exists():
    # Works on both
    pass
```

---

## Recommended Setup

### Development (Windows 11)

```bash
# Simple development server
uvicorn main:app --reload
```

Or use `run_dev.py` script for convenience.

### Production (Linux VM)

**Option A: Systemd (Simple)**
- Use systemd service file
- Automatic restarts
- Easy management

**Option B: Docker (Recommended)**
- Same environment everywhere
- Easy deployment
- Easy scaling

---

## Process Management Comparison

| Method | Windows Dev | Linux Prod | Complexity | Recommended |
|--------|-------------|------------|------------|-------------|
| **Uvicorn direct** | ✅ Yes | ✅ Yes | Low | Dev only |
| **Systemd** | ❌ No | ✅ Yes | Medium | Linux prod |
| **Gunicorn** | ⚠️ Possible | ✅ Yes | Medium | Linux prod |
| **Docker** | ✅ Yes | ✅ Yes | Medium | Both |

---

## Quick Start Commands

### Windows 11 Development

```bash
# 1. Create venv
python -m venv venv
venv\Scripts\activate

# 2. Install
pip install fastapi uvicorn[standard] pandas

# 3. Run
uvicorn main:app --reload
```

### Linux Production

```bash
# 1. Create venv
python3 -m venv venv
source venv/bin/activate

# 2. Install
pip install fastapi uvicorn[standard] gunicorn pandas

# 3. Run with systemd (recommended)
sudo systemctl start league-analyzer

# OR run with Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Testing on Windows Before Deployment

### 1. Test Production Mode Locally

```bash
# Run without --reload (production mode)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

### 2. Test with Gunicorn (if using)

```bash
# Install gunicorn on Windows (works but not recommended for production)
pip install gunicorn

# Test
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

**Note:** Gunicorn on Windows has limitations. Use Uvicorn directly on Windows, Gunicorn on Linux.

---

## Reverse Proxy (Nginx)

For production, use Nginx as reverse proxy:

**Nginx config (`/etc/nginx/sites-available/league-analyzer`):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable:**
```bash
sudo ln -s /etc/nginx/sites-available/league-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Summary

### Development (Windows 11)
```bash
uvicorn main:app --reload
```
Simple, auto-reload, perfect for development.

### Production (Linux VM)
**Recommended:** Systemd service or Docker
- Systemd: Native Linux, automatic restarts
- Docker: Same environment, easy deployment

**Both work the same way** - FastAPI is cross-platform! 🚀

