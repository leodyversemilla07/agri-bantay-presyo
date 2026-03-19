# API Specification
**Project:** Agri Bantay Presyo (Daily Retail Price Monitoring)
**Base URL:** `http://localhost:8000/api/v1` (Local Dev)

## Endpoints

## Authentication
Protected routes use the `X-API-Key` header. Configure `SERVICE_API_KEYS` and `ADMIN_API_KEYS` as JSON maps. Legacy `API_KEY` remains supported as a service-scoped compatibility fallback.

### Service Meta
*   `GET /`: API metadata and discovery links.
*   `GET /health`: Basic health check.
*   `GET /health/ready`: Readiness check for PostgreSQL, Redis, and Alembic head state. Returns `503` until all checks are healthy.

### Commodities (`/commodities`)
*   `GET /`: List tracked commodities. Returns `items`, `total`, `skip`, and `limit`. Supports `category`, `skip`, `limit`, and `q`.
*   `GET /{id}`: Get details for a specific commodity. Malformed UUIDs return `422`.
*   `GET /{id}/history`: Get historical prices for a specific commodity. Malformed UUIDs return `422`.
*   `POST /`: Create a commodity. Requires `X-API-Key`. Returns `201 Created` and a `Location` header.

### Markets (`/markets`)
*   `GET /`: List monitored markets/trading centers. Returns `items`, `total`, `skip`, and `limit`. Supports `skip`, `limit`, and `q`.
*   `GET /{id}`: Get details for a specific market. Malformed UUIDs return `422`.
*   `POST /`: Create a market. Requires `X-API-Key`. Returns `201 Created` and a `Location` header.

### Price Data (`/prices`)
*   `GET /`: Returns paginated price entries with `items`, `total`, `skip`, and `limit`. Supports `report_date`, `start_date`, `end_date`, `commodity_id`, `market_id`, `category`, `region`, `sort_by`, and `sort_order`. Without any date parameters, the endpoint returns only the latest report snapshot within the filtered slice. Use `view=compact` to return flat price rows instead of nested commodity and market objects.
*   `GET /export`: Export price data as CSV using the same filter and sorting contract as `GET /prices`.

### Admin (`/admin`)
*   `GET /ingestion-runs`: Returns paginated recent ingestion-run summaries for operators. Supports optional `task_name` and `status` filters. Requires an admin-scoped `X-API-Key`.

### Analytics & Stats (`/stats`)
*   `GET /dashboard`: Returns aggregate counts for Commodities, Markets, and Prices plus `latest_report_date`, `previous_report_date`, and snapshot deltas.

### Trends (`/trends`)
*   `GET /commodities/{id}/summary`: Returns the latest and previous available commodity snapshot, with absolute and percent change. Supports optional `market_id` and `report_date`.
*   `GET /commodities/{id}/series`: Returns chronological trend points for a commodity. Supports optional `market_id`; otherwise the API averages prevailing prices across markets per report date.
*   `GET /markets/{id}/summary`: Returns the latest and previous available market snapshot, with absolute and percent change. Supports optional `commodity_id` and `report_date`.
*   `GET /markets/{id}/series`: Returns chronological trend points for a market. Supports optional `commodity_id`; otherwise the API averages prevailing prices across commodities per report date.

## Notes
All prices are from **Daily Retail Price Range** reports only.
Legacy aliases such as `/prices/daily` and `/trends/history/{commodity_id}` remain available for backward compatibility.
Operational health tooling treats stale, failed, or anomalous ingestion runs as alert conditions.
