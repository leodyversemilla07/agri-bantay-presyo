# API Specification
**Project:** Bantay Presyo
**Base URL:** `https://api.bantaypresyo.gov.ph/v1`

## Endpoints

### Commodities & Markets
*   `GET /commodities`: Retrieves master list of agricultural products.
*   `GET /markets`: Retrieves list of monitored markets.

### Price Data
*   `GET /prices/daily`: Returns Prevailing Price for a specific date.
*   `GET /prices/weekly`: Returns Average Price data for trend analysis.

### Analytics & Trends
*   `GET /trends/history`: Returns historical data points for line charts.
*   `GET /stats/movers`: Returns "Top Gainers" and "Top Losers" for the homepage ticker.
