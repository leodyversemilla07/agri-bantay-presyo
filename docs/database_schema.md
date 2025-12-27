# Database Schema
**Project:** Agri Bantay Presyo

## Table A: commodities (The Standardizer)
*   **id (PK):** UUID
*   **name:** String (Standardized Name, e.g., "Red Onion")
*   **category:** String (e.g., "Vegetables - Lowland", "Fish")
*   **variant:** String (e.g., "Imported", "Local", "Medium Size")
*   **unit:** String (e.g., "kg", "pc", "tray")

## Table B: markets (The Locations)
*   **id (PK):** UUID
*   **name:** String (e.g., "Commonwealth Market")
*   **region:** String (e.g., "NCR")
*   **city:** String (e.g., "Quezon City")

## Table C: price_entries (The Core Data)
*   **id (PK):** UUID
*   **commodity_id (FK):** Links to commodities
*   **market_id (FK):** Links to markets
*   **report_date:** Date
*   **price_low:** Decimal
*   **price_high:** Decimal
*   **price_prevailing:** Decimal
*   **report_type:** Enum ("DAILY_PREVAILING", "WEEKLY_AVERAGE")
*   **source_file:** String (e.g., "Price-Monitoring-December-22-2025.pdf")

## Table D: supply_indices (The Context)
*   **id (PK):** UUID
*   **date:** Date
*   **commodity_id (FK):** Links to commodities
*   **volume_metric_tons:** Decimal
*   **wholesale_price:** Decimal
