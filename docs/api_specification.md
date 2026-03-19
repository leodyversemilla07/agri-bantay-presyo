# API Specification
**Project:** Agri Bantay Presyo (Daily Retail Price Monitoring)
**Base URL:** `http://localhost:8000/api/v1` (Local Dev)

## Endpoints

## Authentication
Protected write routes require the `X-API-Key` header. Configure the server key with `API_KEY`.

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
*   `GET /`: Returns paginated price entries with `items`, `total`, `skip`, and `limit`, optionally filtered by `report_date`. Without a `report_date`, the endpoint returns only the latest report snapshot.
*   `GET /export`: Export price data as CSV.

### Analytics & Stats (`/stats`)
*   `GET /dashboard`: Returns aggregate counts for Commodities, Markets, and Prices plus `latest_report_date`, `previous_report_date`, and snapshot deltas.

### Trends (`/trends`)
*   `GET /commodities/{id}/summary`: Returns the latest and previous available commodity snapshot, with absolute and percent change. Supports optional `market_id` and `report_date`.
*   `GET /commodities/{id}/series`: Returns chronological trend points for a commodity. Supports optional `market_id`; otherwise the API averages prevailing prices across markets per report date.

## Notes
All prices are from **Daily Retail Price Range** reports only.
Legacy aliases such as `/prices/daily` and `/trends/history/{commodity_id}` remain available for backward compatibility.
