# Technical Architecture & Scraper Logic
**Project:** Agri Bantay Presyo

## Recommended Tech Stack (The "Agri-Stack")
*   **Backend API:** FastAPI (Python) - High performance; native support for `pdfplumber`.
*   **Database:** PostgreSQL - Relational data (linking Commodities to Markets).
*   **Scraper Engine:** Celery + Redis - Scheduled daily PDF downloads.
*   **Frontend:** Next.js (React) - Fast, SEO-friendly, and mobile-responsive.

## Scraper Logic Specification
1.  **Spatial Table Extraction:** Uses `pdfplumber` to map specific X-coordinates to data columns.
2.  **Stateful Parsing:** Remembers the "Category" (e.g., "FISH") of the previous row to apply it to indented commodities (e.g., "Bangus").
3.  **Standardization Map:** Uses a `map.json` file for normalization rules (e.g., mapping "Rice Special (Imp.)" to a standard ID) and typo correction.
4.  **Multi-File Handling:** Separate logic for Weekly Average (File Type A), Daily Prevailing (File Type B), and Daily Price Index (File Type C) to extract volume or retail prices accordingly.
