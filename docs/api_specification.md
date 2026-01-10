# API Specification
**Project:** Agri Bantay Presyo (Daily Retail Price Monitoring)
**Base URL:** `http://localhost:8000/api/v1` (Local Dev)

## Endpoints

### Commodities (`/commodities`)
*   `GET /`: List all tracked commodities.
*   `GET /{id}`: Get details for a specific commodity.

### Markets (`/markets`)
*   `GET /`: List all monitored markets/trading centers.
*   `GET /{id}`: Get details for a specific market.

### Price Data (`/prices`)
*   `GET /latest`: Returns the most recent price entries.
*   `GET /history`: Returns historical price points (supports `commodity_id` and `date_range` filters).

### Analytics & Stats (`/stats`)
*   `GET /stats/dashboard`: Returns aggregate counts for Commodities, Markets, and Prices.

## Notes
All prices are from **Daily Retail Price Range** reports only.
