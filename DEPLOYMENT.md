# Deployment Guide: Inventory Management System

This guide covers deploying the Inventory Management System to an Ubuntu cloud server using Podman and SQLite.

## Prerequisites

- Ubuntu 22.04 or 24.04 LTS server
- Domain name (optional but recommended)
- SSH access to the server
- Minimum 1GB RAM, 1 vCPU, 10GB storage

## Step 1: Server Preparation

### Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### Install Required Dependencies

```bash
sudo apt install -y curl git nginx certbot python3-certbot-nginx
```

## Step 2: Install Podman

### Install Podman and Podman Compose

```bash
# Install Podman
sudo apt install -y podman

# Install podman-compose for managing multi-container setups
sudo apt install -y podman-compose

# Verify installation
podman --version
podman-compose --version
```

### Enable Rootless Podman (Optional but Recommended)

```bash
# Enable linger for your user to allow containers to run after logout
sudo loginctl enable-linger $USER
```

## Step 3: Project Setup

### Create Application Directory

```bash
# Create directory structure
mkdir -p ~/inventory-system/{frontend,backend,data}
cd ~/inventory-system
```

### Clone/Upload Your Project

```bash
# If using git
git clone <your-repo-url> temp
cp -r temp/backend/* backend/
cp -r temp/src/* frontend/
cp temp/package.json temp/bun.lock frontend/
rm -rf temp
```

Or use SCP to upload files from your local machine:
```bash
# From your local machine
scp -r backend/ user@server-ip:~/inventory-system/
scp -r src/ package.json bun.lock user@server-ip:~/inventory-system/frontend/
```

## Step 4: Backend Container Setup

### Create Backend Dockerfile (SQLite Optimized)

Create `~/inventory-system/backend/Containerfile`:

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim AS production

WORKDIR /app

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/

# Create data directory for SQLite with proper permissions
RUN mkdir -p /app/data && chown -R appuser:appgroup /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DATABASE_URL=sqlite+aiosqlite:///./data/inventory.db

# Change to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create Backend Environment File

Create `~/inventory-system/backend/.env`:

```bash
# Application
APP_NAME="Inventory Management System"
APP_VERSION="1.0.0"
DEBUG=false

# Database - SQLite in container
DATABASE_URL=sqlite+aiosqlite:///./data/inventory.db
DATABASE_ECHO=false

# Security - CHANGE THESE IN PRODUCTION!
SECRET_KEY=your-super-secret-key-change-this-immediately
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS - Update with your domain
CORS_ORIGINS=["https://your-domain.com", "https://www.your-domain.com"]

# File Upload
MAX_UPLOAD_SIZE=10485760
```

### Build and Run Backend Container

```bash
cd ~/inventory-system/backend

# Build the container image
podman build -t inventory-backend:latest -f Containerfile .

# Run the container
podman run -d \
  --name inventory-backend \
  --restart unless-stopped \
  -p 127.0.0.1:8000:8000 \
  -v ~/inventory-system/data:/app/data:Z \
  --env-file .env \
  inventory-backend:latest

# Check container status
podman ps
podman logs inventory-backend
```

## Step 5: Frontend Setup

### Configure Next.js for Static Export

Update `next.config.ts` to enable static export:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  distDir: 'dist',
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
```

### Create Frontend Environment

Create `~/inventory-system/frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://your-domain.com/api
```

### Build Frontend (Two Options)

#### Option A: Build Locally and Upload

Build on your local machine and upload the `dist` folder.

#### Option B: Build with Node.js Container

```bash
cd ~/inventory-system/frontend

# Run Node container to build
podman run --rm -it \
  -v $(pwd):/app:Z \
  -w /app \
  node:20-alpine \
  sh -c "npm install && npm run build"

# Or if using Bun
podman run --rm -it \
  -v $(pwd):/app:Z \
  -w /app \
  oven/bun:latest \
  sh -c "bun install && bun run build"
```

### Serve Frontend with Nginx

The built frontend will be in `~/inventory-system/frontend/dist` and served via Nginx (configured in Step 7).

## Step 6: Database Migrations

### Run Alembic Migrations

```bash
# Execute migration command inside the backend container
podman exec -it inventory-backend \
  alembic upgrade head

# Verify database was created
ls -la ~/inventory-system/data/
```

### Create Initial Admin User (Optional)

```bash
# Create a script to add admin user
podman exec -it inventory-backend \
  python -c "
import asyncio
from app.core.database import async_session_maker
from app.models.user import User
from app.core.security import get_password_hash

async def create_admin():
    async with async_session_maker() as session:
        admin = User(
            email='admin@your-domain.com',
            username='admin',
            hashed_password=get_password_hash('your-admin-password'),
            full_name='Administrator',
            is_active=True,
            is_admin=True
        )
        session.add(admin)
        await session.commit()
        print('Admin user created!')

asyncio.run(create_admin())
"
```

## Step 7: Nginx Reverse Proxy Setup

### Create Nginx Configuration

Create `/etc/nginx/sites-available/inventory-system`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend - Static files
    location / {
        root /home/your-user/inventory-system/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Docs (optional - remove in production)
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
```

### Enable the Site

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/inventory-system /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Step 8: SSL with Let's Encrypt

### Obtain SSL Certificate

```bash
# Install certbot if not already installed
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow the prompts to complete SSL setup

# Test auto-renewal
sudo certbot renew --dry-run
```

## Step 9: Systemd Service for Auto-Start

### Create Systemd Service File

Create `~/.config/systemd/user/inventory-backend.service`:

```ini
[Unit]
Description=Inventory Management System Backend
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=5
WorkingDirectory=/home/your-user/inventory-system/backend
ExecStart=/usr/bin/podman run \
    --rm \
    --name inventory-backend \
    -p 127.0.0.1:8000:8000 \
    -v /home/your-user/inventory-system/data:/app/data:Z \
    --env-file /home/your-user/inventory-system/backend/.env \
    inventory-backend:latest
ExecStop=/usr/bin/podman stop -t 10 inventory-backend
ExecStopPost=/usr/bin/podman rm inventory-backend

[Install]
WantedBy=default.target
```

### Enable and Start Service

```bash
# Create directory if needed
mkdir -p ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

# Enable service to start on boot
systemctl --user enable inventory-backend

# Start the service
systemctl --user start inventory-backend

# Check status
systemctl --user status inventory-backend
```

### Enable Lingering (Required for Rootless)

```bash
# Allow user services to run after logout
sudo loginctl enable-linger $USER
```

## Step 10: Backup Strategy

### Create Backup Script

Create `~/inventory-system/backup.sh`:

```bash
#!/bin/bash

# Backup script for SQLite database

BACKUP_DIR="/home/your-user/inventory-system/backups"
DB_FILE="/home/your-user/inventory-system/data/inventory.db"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
podman exec inventory-backend sqlite3 /app/data/inventory.db ".backup /app/data/inventory_backup.db"
cp ~/inventory-system/data/inventory_backup.db $BACKUP_DIR/inventory_$DATE.db

# Keep only last 7 days of backups
find $BACKUP_DIR -name "inventory_*.db" -mtime +7 -delete

echo "Backup completed: inventory_$DATE.db"
```

Make it executable:
```bash
chmod +x ~/inventory-system/backup.sh
```

### Setup Cron Job for Automated Backups

```bash
# Edit crontab
crontab -e

# Add line for daily backup at 2 AM
0 2 * * * /home/your-user/inventory-system/backup.sh >> /home/your-user/inventory-system/backups/backup.log 2>&1
```

## Step 11: Monitoring and Maintenance

### View Container Logs

```bash
# View logs
podman logs inventory-backend

# Follow logs
podman logs -f inventory-backend

# View last 100 lines
podman logs --tail 100 inventory-backend
```

### Update Application

```bash
cd ~/inventory-system

# Stop container
podman stop inventory-backend

# Remove old container
podman rm inventory-backend

# Pull latest code (if using git)
cd backend && git pull
cd ../frontend && git pull

# Rebuild backend
podman build -t inventory-backend:latest -f Containerfile .

# Restart container
podman run -d \
  --name inventory-backend \
  --restart unless-stopped \
  -p 127.0.0.1:8000:8000 \
  -v ~/inventory-system/data:/app/data:Z \
  --env-file .env \
  inventory-backend:latest

# Rebuild frontend and copy to nginx directory
# ... (build steps)

# Reload nginx
sudo systemctl reload nginx
```

## Step 12: Security Hardening

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Check status
sudo ufw status
```

### Update Secret Keys

Make sure to change the following in `~/inventory-system/backend/.env`:
- `SECRET_KEY`: Generate a strong random key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Adjust as needed
- Update CORS_ORIGINS to your actual domain

Generate a secure secret:
```bash
openssl rand -hex 32
```

### Disable Debug Mode

Ensure `DEBUG=false` in your `.env` file.

## Troubleshooting

### Container Won't Start

```bash
# Check logs
podman logs inventory-backend

# Check if port is already in use
sudo netstat -tlnp | grep 8000

# Restart container
podman restart inventory-backend
```

### Database Permission Issues

```bash
# Fix SELinux labels
podman run -v ~/inventory-system/data:/app/data:Z ...

# Or fix permissions manually
chmod 755 ~/inventory-system/data
```

### Nginx 502 Error

```bash
# Check if backend is running
podman ps

# Check backend logs
podman logs inventory-backend

# Test backend directly
curl http://127.0.0.1:8000/health
```

### Frontend Not Loading

```bash
# Check if dist folder exists
ls -la ~/inventory-system/frontend/dist/

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Verify Nginx config
sudo nginx -t
```

## Directory Structure Summary

```
~/inventory-system/
├── backend/
│   ├── Containerfile
│   ├── .env
│   ├── app/
│   ├── alembic/
│   └── alembic.ini
├── frontend/
│   ├── dist/          # Built frontend files
│   ├── src/
│   └── package.json
├── data/
│   └── inventory.db   # SQLite database
├── backups/
│   └── inventory_*.db # Backup files
└── backup.sh          # Backup script
```

## Useful Commands Reference

```bash
# Container management
podman ps                    # List running containers
podman ps -a                 # List all containers
podman logs container-name   # View container logs
podman exec -it container-name sh  # Enter container shell
podman stop container-name   # Stop container
podman start container-name  # Start container
podman rm container-name     # Remove container
podman images                # List images

# Service management
systemctl --user status inventory-backend
systemctl --user restart inventory-backend
systemctl --user stop inventory-backend

# Nginx
sudo nginx -t                # Test configuration
sudo systemctl reload nginx  # Reload configuration
sudo systemctl restart nginx # Restart Nginx
```

## Next Steps

1. Configure automated backups
2. Set up log rotation
3. Configure monitoring (Prometheus/Grafana optional)
4. Set up log aggregation
5. Consider using a managed database for production scale
