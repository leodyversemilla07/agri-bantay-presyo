# Database Schema
**Project:** Agri Bantay Presyo (Daily Retail Price Monitoring)

## Table A: commodities
*   **id (PK):** UUID
*   **name:** String (e.g., "Red Onion", "Cabbage")
*   **category:** String (e.g., "Vegetables", "Fish")
*   **variant:** String (e.g., "Imported", "Local")
*   **unit:** String (e.g., "kg", "pc")

## Table B: markets
*   **id (PK):** UUID
*   **name:** String (e.g., "Commonwealth Market")
*   **region:** String (e.g., "NCR")
*   **city:** String (e.g., "Quezon City")

## Table C: price_entries (Daily Retail Prices)
*   **id (PK):** UUID
*   **commodity_id (FK):** Links to commodities
*   **market_id (FK):** Links to markets
*   **report_date:** Date
*   **price_low:** Decimal (Low end of price range)
*   **price_high:** Decimal (High end of price range)
*   **price_prevailing:** Decimal (Calculated average or prevailing price)
*   **report_type:** String ("DAILY_RETAIL")
*   **source_file:** String (PDF filename)

## Notes
- Only Daily Retail Price Range data is stored.
- `report_type` is always "DAILY_RETAIL".
