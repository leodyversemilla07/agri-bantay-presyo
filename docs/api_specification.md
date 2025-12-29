# API Specification
**Project:** Agri Bantay Presyo
**Base URL:** `http://localhost:8000/api/v1` (Local Dev)

## Endpoints

### Commodities (`/commodities`)
*   `GET /`: List all tracked commodities (supports filtering by category).
*   `GET /{id}`: Get details for a specific commodity.

### Markets (`/markets`)
*   `GET /`: List all monitored trading centers/markets.
*   `GET /{id}`: Get details for a specific market.

### Price Data (`/prices`)
*   `GET /latest`: Returns the most recent price entries for all commodities.
*   `GET /history`: Returns historical price points (supports `commodity_id` and `date_range` filters).

### Analytics & Stats (`/stats`, `/trends`)
*   `GET /stats/dashboard`: Returns aggregate counts for Commodities, Markets, and Prices.
*   `GET /trends/summary`: Returns "Top Gainers" and "Top Losers" summary.
