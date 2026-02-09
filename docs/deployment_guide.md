# Deployment Guide - Agri Bantay Presyo

This guide covers deploying the Agri Bantay Presyo application for both development and production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Quick Start (Docker)](#quick-start-docker)
- [Manual Deployment](#manual-deployment)
- [Database Setup](#database-setup)
- [Production Deployment](#production-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 20.10+ | Container runtime |
| Docker Compose | 2.0+ | Multi-container orchestration |
| Python | 3.12+ | Application runtime (manual deployment) |
| PostgreSQL | 16+ | Database (manual deployment) |
| Redis | 7+ | Message broker for Celery |

## Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/bantay_presyo
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=bantay_presyo

# Redis
REDIS_URL=redis://localhost:6379/0

```

### Variable Descriptions

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string for Celery |
| `POSTGRES_SERVER` | No | PostgreSQL host (default: localhost) |
| `POSTGRES_USER` | No | PostgreSQL user (default: postgres) |
| `POSTGRES_PASSWORD` | No | PostgreSQL password (default: password) |
| `POSTGRES_DB` | No | Database name (default: bantay_presyo) |

---

## Quick Start (Docker)

### 1. Clone the Repository

```bash
git clone https://github.com/leodyversemilla07/agri-bantay-presyo.git
cd agri-bantay-presyo
```

### 2. Start Infrastructure Services

```bash
docker-compose up -d
```

This starts 2 services:
- **db** - PostgreSQL 16 database (port 5432)
- **redis** - Redis 7 message broker (port 6379)

### 3. Run the Application Locally

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

```bash
# Run migrations
alembic upgrade head

# Optional seed
python -c "from app.db.seed import seed_initial_data; seed_initial_data()"
```

```bash
# Start API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
# Start Celery worker (separate terminal)
celery -A app.core.celery_app worker --loglevel=info

# Start Celery beat (separate terminal)
celery -A app.core.celery_app beat --loglevel=info
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Manual Deployment

### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL

```bash
# Create database
psql -U postgres -c "CREATE DATABASE bantay_presyo;"
```

### 3. Set Up Redis

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or install locally (Ubuntu)
sudo apt install redis-server
sudo systemctl start redis
```

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start the Application

```bash
# Development (with auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Start Celery Worker

```bash
# In a separate terminal
celery -A app.core.celery_app worker --loglevel=info
```

### 7. Start Celery Beat (Scheduler)

```bash
# In another separate terminal
celery -A app.core.celery_app beat --loglevel=info
```

---

## Database Setup

### Running Migrations

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Database Schema

The application uses the following main tables:
- `commodities` - Agricultural products (rice, vegetables, meat, etc.)
- `markets` - Trading centers across the Philippines
- `price_entries` - Daily price data with ranges

---

## Production Deployment

### Docker Compose (Production)

Create a `docker-compose.prod.yml`:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: always
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  celery-worker:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: always
    command: celery -A app.core.celery_app worker --loglevel=warning --concurrency=2

  celery-beat:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
      - celery-worker
    restart: always
    command: celery -A app.core.celery_app beat --loglevel=warning

volumes:
  postgres_data:
```

### Nginx Reverse Proxy

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Environment Variables (Production)

For production, use strong passwords and secure your environment variables:

```env
DATABASE_URL=postgresql://bantay_user:STRONG_PASSWORD_HERE@db:5432/bantay_presyo
REDIS_URL=redis://redis:6379/0
```

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f db
docker-compose logs -f redis
```

### Check Service Health

```bash
# API health check
curl http://localhost:8000/api/v1/stats/dashboard

# Check running containers
docker-compose ps
```

### Database Backup

```bash
# Backup
docker-compose exec db pg_dump -U postgres bantay_presyo > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20260110.sql | docker-compose exec -T db psql -U postgres bantay_presyo
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart db
docker-compose restart redis
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart infrastructure
docker-compose up -d

# Update local dependencies
pip install -r requirements.txt

# Run any new migrations
alembic upgrade head
```

---

## Scheduled Tasks

The application uses Celery Beat to run scheduled tasks:

| Task | Schedule | Description |
|------|----------|-------------|
| `discover_new_pdfs` | Daily at 8:00 AM | Scans DA website for new Price Monitoring PDFs |

To manually trigger PDF discovery:

```bash
python -c "
from app.scraper.discovery import discover_new_pdfs
discover_new_pdfs()
"
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

```
sqlalchemy.exc.OperationalError: connection refused
```

**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct.

```bash
# Check if db container is running
docker-compose ps db

# Restart database
docker-compose restart db
```

#### 2. Redis Connection Error

```
redis.exceptions.ConnectionError: Connection refused
```

**Solution**: Ensure Redis is running.

```bash
docker-compose restart redis
```

#### 3. Migration Errors

```
alembic.util.exc.CommandError: Can't locate revision
```

**Solution**: Reset migrations if needed.

```bash
# Stamp current state
alembic stamp head

# Or fresh start (CAUTION: drops all data)
alembic downgrade base
alembic upgrade head
```

#### 5. Port Already in Use

```
Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use
```

**Solution**: Stop the conflicting process or change the port.

```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/macOS

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

### Useful Commands

```bash
# View container resource usage
docker stats

# Check database contents
python scripts/show_data.py

# Wipe database (CAUTION!)
python scripts/wipe_db.py
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                     │
│                      Port 80/443                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│                       Port 8000                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  REST API   │  │   Views     │  │   Static Files      │  │
│  │  /api/v1/*  │  │  (Jinja2)   │  │   /static/*         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────┬──────────────────────────────────┬───────────────┘
           │                                  │
           ▼                                  ▼
┌─────────────────────┐              ┌─────────────────────┐
│   PostgreSQL 16     │              │    Redis 7          │
│   Port 5432         │              │    Port 6379        │
│                     │              │                     │
│  - commodities      │              │  - Task Queue       │
│  - markets          │              │  - Beat Schedule    │
│  - price_entries    │              │                     │
└─────────────────────┘              └──────────┬──────────┘
                                               │
                              ┌────────────────┴────────────────┐
                              │                                 │
                              ▼                                 ▼
                   ┌─────────────────────┐        ┌─────────────────────┐
                   │   Celery Worker     │        │   Celery Beat       │
                   │  (optional local)   │        │  (optional local)   │
                   │  - PDF Download     │        │  - Schedule Tasks   │
                   │  - Parsing          │        │  - Daily Discovery  │
                   │  - Data Ingestion   │        │                     │
                   └─────────────────────┘        └─────────────────────┘
                              │
                              ▼
```

---

## Support

For issues and feature requests, please open an issue on GitHub:
https://github.com/leodyversemilla07/agri-bantay-presyo/issues
