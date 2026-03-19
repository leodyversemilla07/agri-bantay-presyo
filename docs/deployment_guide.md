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

Copy `.env.example` to `.env` for local work or `.env.production` for VPS deployment:

```env
# Runtime
APP_ENV=development
LOG_LEVEL=INFO
LOG_AS_JSON=false

# Auth
SERVICE_API_KEYS={"local-service":"change-me"}
ADMIN_API_KEYS={"local-admin":"change-me-admin"}

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/bantay_presyo
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=bantay_presyo

# Redis
REDIS_URL=redis://localhost:6379/0

# Rate limiting
RATE_LIMIT_STORAGE_URL=memory://

# Celery runtime
CELERY_WORKER_POOL=solo
CELERY_WORKER_CONCURRENCY=1
CELERY_BEAT_SCHEDULE_FILE=celerybeat-schedule.local
# Operational checks
WAIT_FOR_SERVICES_TIMEOUT_SECONDS=60
INGESTION_STALENESS_HOURS=36
INGESTION_ANOMALY_LOOKBACK_RUNS=5
INGESTION_ANOMALY_ROW_COUNT_RATIO_THRESHOLD=0.6
INGESTION_ANOMALY_MISSING_PREVAILING_RATIO_THRESHOLD=0.25
INGESTION_ALERT_MAX_ANOMALIES=0
```

### Variable Descriptions

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string for Celery |
| `APP_ENV` | No | Runtime environment (`development` or `production`) |
| `LOG_LEVEL` | No | Standard log level (`INFO`, `WARNING`, etc.) |
| `LOG_AS_JSON` | No | Emit structured JSON logs (enabled by default in production) |
| `SERVICE_API_KEYS` | No | JSON object of service-scoped API keys for protected write routes |
| `ADMIN_API_KEYS` | No | JSON object of admin-scoped API keys for operational endpoints |
| `RATE_LIMIT_STORAGE_URL` | No | Storage backend for rate limiting (default: `memory://`, set to Redis for shared limits) |
| `CELERY_WORKER_POOL` | No | Celery worker pool mode (`solo` locally on Windows, `prefork` in production) |
| `CELERY_WORKER_CONCURRENCY` | No | Celery worker concurrency (`2` by default in production) |
| `CELERY_BEAT_SCHEDULE_FILE` | No | Beat schedule filename (defaults to `/app/data/celerybeat-schedule` in production) |
| `WAIT_FOR_SERVICES_TIMEOUT_SECONDS` | No | Timeout for dependency wait checks before process startup |
| `INGESTION_STALENESS_HOURS` | No | Maximum age for the latest successful ingestion before health checks fail |
| `INGESTION_ANOMALY_LOOKBACK_RUNS` | No | Number of recent healthy scrapes used as the row-count anomaly baseline |
| `INGESTION_ANOMALY_ROW_COUNT_RATIO_THRESHOLD` | No | Minimum fraction of baseline row count before a scrape is flagged as anomalously small |
| `INGESTION_ANOMALY_MISSING_PREVAILING_RATIO_THRESHOLD` | No | Maximum allowed share of rows missing `price_prevailing` before a scrape is flagged |
| `INGESTION_ALERT_MAX_ANOMALIES` | No | Maximum allowed anomaly count on the latest successful ingestion before alerts fail |
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

This starts 2 infrastructure services:
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
python scripts/start_celery_beat.py
```

On Windows, the default Celery configuration uses a `solo` worker pool. The beat launcher resets the local schedule file before startup to avoid stale shelve/dbm state.

### 4. Access the Application

- **API Root**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Test Suite**: `pytest -q` (defaults to in-memory SQLite unless `TEST_DATABASE_URL` is set)
- **Admin Health Script**: `python scripts/health_check.py`
- **Readiness Probe**: `GET /health/ready`
- **Admin Runs API**: `GET /api/v1/admin/ingestion-runs` with an admin-scoped `X-API-Key`

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

For local development, rate limiting uses in-memory storage by default. To use Redis-backed shared limits, set:

```env
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/0
```

Local admin tooling:

```bash
python scripts/preflight_duplicates.py
python scripts/cleanup_duplicates.py --apply
python scripts/backfill_prices.py --start-date 2026-03-01 --end-date 2026-03-05
python scripts/health_check.py
python scripts/health_check.py --mode ready
```

### 6. Start Celery Worker

```bash
# In a separate terminal
celery -A app.core.celery_app worker --loglevel=info
```

### 7. Start Celery Beat (Scheduler)

```bash
# In another separate terminal
python scripts/start_celery_beat.py
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

The repo now includes a production stack in `docker-compose.prod.yml` with:
- `api` - FastAPI application behind readiness checks
- `worker` - Celery worker using production defaults
- `beat` - Celery beat with a persistent schedule path in `/app/data`
- `db` - PostgreSQL 16 with a persistent volume
- `redis` - Redis 7 with append-only persistence
- `caddy` - reverse proxy and TLS termination

### VPS Deployment Flow

1. Copy `.env.example` to `.env.production` and set real credentials.
2. Set `APP_DOMAIN` and `APP_IMAGE` for the target environment.
3. Keep the repo checked out on the VPS.
4. Run:

```bash
./scripts/deploy_prod.sh
```

The deploy script performs:
- dependency startup for Postgres and Redis
- dependency waiting via `python scripts/wait_for_services.py`
- logical backup via `./scripts/backup_db.sh`
- duplicate preflight via `python scripts/preflight_duplicates.py`
- `alembic upgrade head`
- restart of `api`, `worker`, `beat`, and `caddy`
- post-deploy readiness and operational health checks

### Environment Variables (Production)

For production, use strong passwords and secure your environment variables:

```env
APP_ENV=production
LOG_AS_JSON=true
SERVICE_API_KEYS={"deploy":"change-me"}
ADMIN_API_KEYS={"ops":"change-me-admin"}
APP_DOMAIN=prices.example.com
APP_IMAGE=ghcr.io/owner/agri-bantay-presyo:sha-<git-sha>
DATABASE_URL=postgresql://bantay_user:STRONG_PASSWORD_HERE@db:5432/bantay_presyo
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_STORAGE_URL=redis://redis:6379/1
CELERY_WORKER_POOL=prefork
CELERY_WORKER_CONCURRENCY=2
CELERY_BEAT_SCHEDULE_FILE=/app/data/celerybeat-schedule
INGESTION_ALERT_MAX_ANOMALIES=0
```

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f

# Specific service
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f api
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f worker
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f beat
```

### Check Service Health

```bash
# API liveness
curl http://localhost:8000/health

# API readiness
curl http://localhost:8000/health/ready

# Full operational check from inside the API container
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T api \
  python scripts/health_check.py --production

# Recent ingestion runs through the admin API
curl -H "X-API-Key: <admin-key>" http://localhost:8000/api/v1/admin/ingestion-runs

# Check running containers
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

### Database Backup

```bash
# Backup
./scripts/backup_db.sh

# Restore
cat backups/predeploy-20260110-120000.sql | docker compose -f docker-compose.prod.yml --env-file .env.production exec -T db \
  psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```

### Restart Services

```bash
# Restart all
docker compose -f docker-compose.prod.yml --env-file .env.production restart

# Restart specific service
docker compose -f docker-compose.prod.yml --env-file .env.production restart api
docker compose -f docker-compose.prod.yml --env-file .env.production restart worker
docker compose -f docker-compose.prod.yml --env-file .env.production restart beat
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Re-deploy through the hardened production path
./scripts/deploy_prod.sh
```

---

## Scheduled Tasks

The application uses Celery Beat to run scheduled tasks:

| Task | Schedule | Description |
|------|----------|-------------|
| `app.scraper.tasks.discover_and_scrape` | Daily at 8:00 AM | Scans DA website for new Price Monitoring PDFs and queues scrape jobs |

To manually trigger PDF discovery:

```bash
python -c "
from app.scraper.discovery import discover_and_scrape
discover_and_scrape()
"
```

To fail a cron or monitoring check when ingestion is stale, failed, or anomalous:

```bash
python scripts/check_alerts.py
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
docker compose -f docker-compose.prod.yml --env-file .env.production ps db

# Restart database
docker compose -f docker-compose.prod.yml --env-file .env.production restart db
```

#### 2. Redis Connection Error

```
redis.exceptions.ConnectionError: Connection refused
```

**Solution**: Ensure Redis is running.

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production restart redis
```

#### 3. Migration Errors

```
alembic.util.exc.CommandError: Can't locate revision
```

**Solution**: Reset migrations if needed.

```bash
# Stamp current state
alembic stamp head

# Or verify the schema state through the readiness endpoint
curl http://localhost:8000/health/ready
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
│                    Caddy (Reverse Proxy)                     │
│                      Port 80/443                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│                       Port 8000                              │
│  ┌──────────────────────────────┐  ┌───────────────────┐  │
│  │ REST API + OpenAPI Docs      │  │ Health Endpoints  │  │
│  │ /api/v1/*, /docs, /redoc     │  │ /, /health        │  │
│  └──────────────────────────────┘  └───────────────────┘  │
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
