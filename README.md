# Agri Bantay Presyo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127.1-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

Agri Bantay Presyo is a modernized agricultural price monitoring system designed to centralize and automate the collection of commodity price data from scattered government PDF reports in the Philippines. The platform scrapes data from Department of Agriculture - Agricultural Marketing Assistance Service (DA-AMAS) sources and uses deterministic, layout-aware parsing for PDF extraction. Data is stored in a structured PostgreSQL database for easy querying and analysis.

Built as an API-first backend service, it features:
- **Backend**: FastAPI (Python) with deterministic PDF processing, robust data standardization, and RESTful API endpoints.
- **Data Processing**: Intelligent mapping of commodity names, automated backfilling of historical data (2018-Present), and conflict resolution for duplicate entries.

The system provides farmers, consumers, policymakers, and developers with real-time access to agricultural price trends through an open API suitable for web, mobile, and analytics clients.

## Tech Stack

### Backend
- **Framework**: FastAPI 0.127.1 (Python)
- **Database**: PostgreSQL 16
- **PDF Processing**: pdfplumber (for text extraction) + deterministic parsing
- **Language**: Python 3.12

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git
- **CI/CD**: GitHub Actions (lint, test, build, deploy)

## Project Structure

- `app/` - FastAPI application with scraping logic, database models, and REST API routes.
- `docs/` - Project documentation, requirements, and architecture.

## Getting Started

### Prerequisites
- **Docker** and **Docker Compose** (for local development)
- **Python 3.12+** (for backend development)
- **PostgreSQL** (optional if you use Docker for infrastructure)

### Local Development

1. Clone the repository
2. Start infrastructure services:
   ```bash
   docker-compose up -d
   ```
3. Install Python dependencies and run the API:
   ```bash
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```
4. Optional: run Celery processes in separate terminals:
   ```bash
   celery -A app.core.celery_app worker --loglevel=info
   python scripts/start_celery_beat.py
   ```
   On Windows, the app defaults the worker to a `solo` pool. The beat launcher resets the local schedule file before startup to avoid stale-shelve failures.
5. Run the test suite:
   ```bash
   pytest -q
   ```
   Tests default to in-memory SQLite and do not require local PostgreSQL or Redis.

6. Access the application:
   - **API Root**: http://localhost:8000/
   - **Backend API**: http://localhost:8000/api/v1
   - **API Documentation**: http://localhost:8000/docs

### Core REST Endpoints

- `GET /health` - Service health check
- `GET /health/ready` - Readiness check for Postgres, Redis, and migration head state
- `GET /api/v1/commodities` - Paginated commodities with `items`, `total`, `skip`, `limit`; filter with `category` or search with `q`
- `GET /api/v1/commodities/{commodity_id}/history` - Commodity price history
- `GET /api/v1/markets` - Paginated markets with `items`, `total`, `skip`, `limit`; search with `q`
- `GET /api/v1/prices` - Paginated prices filtered by snapshot/date range, commodity, market, category, and region; supports `sort_by`, `sort_order`, and `view=compact`
- `GET /api/v1/prices/export` - CSV export with the same filter and sorting contract as `/api/v1/prices`
- `GET /api/v1/stats/dashboard` - Aggregate counts plus `latest_report_date`, `previous_report_date`, and snapshot deltas
- `GET /api/v1/trends/commodities/{commodity_id}/summary` - Commodity trend summary, optionally scoped to a market
- `GET /api/v1/trends/commodities/{commodity_id}/series` - Chronological commodity trend points, aggregated across markets by default
- `GET /api/v1/trends/markets/{market_id}/summary` - Market trend summary, optionally scoped to a commodity
- `GET /api/v1/trends/markets/{market_id}/series` - Chronological market trend points, aggregated across commodities by default
- `GET /api/v1/admin/ingestion-runs` - Recent ingestion-run summaries for operations; requires an admin-scoped `X-API-Key`
- `POST /api/v1/commodities` and `POST /api/v1/markets` - Create resources, returning `201 Created`; requires a service- or admin-scoped `X-API-Key`

### Authentication

- Protected routes use the `X-API-Key` header.
- Configure service and admin keys with `SERVICE_API_KEYS` and `ADMIN_API_KEYS` as JSON maps in `.env`.
- Legacy `API_KEY` remains supported as a compatibility fallback and is treated as a service-scoped key.
- Rate limiting uses in-memory storage by default for local development. Set `RATE_LIMIT_STORAGE_URL` to a Redis URL for shared/distributed rate limits.
- Example: `X-API-Key: your-secret-key`

## Deployment

The supported production target is a single Linux VPS running Docker Compose.

1. Copy `.env.example` to `.env.production` and fill in production secrets.
2. Ensure the VPS has the repo checked out and Docker Compose v2 available.
3. Set `APP_IMAGE` to the image tag you want to deploy, or let CI export it during the CD workflow.
4. Run:
   ```bash
   ./scripts/deploy_prod.sh
   ```

Production uses:
- `docker-compose.prod.yml` for `api`, `worker`, `beat`, `db`, `redis`, and `caddy`
- `scripts/wait_for_services.py` before service startup
- `scripts/preflight_duplicates.py` before migrations
- `scripts/backup_db.sh` before deploy-time migrations
- `scripts/health_check.py --mode ready --production` for post-deploy verification

## Admin Scripts

- `python scripts/preflight_duplicates.py` - Non-destructive duplicate scan before applying uniqueness migrations
- `python scripts/cleanup_duplicates.py --apply` - Deterministic duplicate cleanup for local/admin use
- `python scripts/backfill_prices.py --start-date 2026-03-01 --end-date 2026-03-05` - Backfill DA PDFs over a date range
- `python scripts/backfill_prices.py --url <pdf-url>` - Backfill explicit PDF URLs
- `python scripts/health_check.py` - Check Postgres, Redis, schema head state, worker reachability, beat freshness, ingestion freshness, and ingestion anomalies
- `python scripts/health_check.py --mode ready` - Readiness-only check for API health probes
- `python scripts/check_alerts.py` - Exit non-zero when ingestion is stale, anomalous, or the latest ingestion run failed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
