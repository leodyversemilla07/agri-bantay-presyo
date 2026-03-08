# API Specification
**Project:** Agri Bantay Presyo (Daily Retail Price Monitoring)
**Base URL:** `http://localhost:8000/api/v1` (Local Dev)

## Endpoints

## Authentication
Protected write routes require the `X-API-Key` header. Configure the server key with `API_KEY`.

### Service Meta
*   `GET /`: API metadata and discovery links.
*   `GET /health`: Basic health check.

### Commodities (`/commodities`)
*   `GET /`: List tracked commodities. Returns `items`, `total`, `skip`, and `limit`. Supports `category`, `skip`, `limit`, and `q`.
*   `GET /{id}`: Get details for a specific commodity.
*   `GET /{id}/history`: Get historical prices for a specific commodity.
*   `POST /`: Create a commodity. Requires `X-API-Key`. Returns `201 Created` and a `Location` header.

### Markets (`/markets`)
*   `GET /`: List monitored markets/trading centers. Returns `items`, `total`, `skip`, and `limit`. Supports `skip`, `limit`, and `q`.
*   `GET /{id}`: Get details for a specific market.
*   `POST /`: Create a market. Requires `X-API-Key`. Returns `201 Created` and a `Location` header.

### Price Data (`/prices`)
*   `GET /`: Returns paginated price entries with `items`, `total`, `skip`, and `limit`, optionally filtered by `report_date`.
*   `GET /export`: Export price data as CSV.

### Analytics & Stats (`/stats`)
*   `GET /dashboard`: Returns aggregate counts for Commodities, Markets, and Prices.

## Notes
All prices are from **Daily Retail Price Range** reports only.
Legacy aliases such as `/prices/daily` and `/trends/history/{commodity_id}` remain available for backward compatibility.
