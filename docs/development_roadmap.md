# Development Roadmap
**Project:** Agri Bantay Presyo (Daily Retail Price Monitoring)

## Phase 1: Foundation & Prototype ✅ DONE
*   [x] Set up FastAPI project structure with PostgreSQL connection.
*   [x] Create PDF Scraper for Daily Retail Price Range.
*   [x] Implement "Spatial Table Extraction" using `pdfplumber`.
*   [x] Verify data extraction accuracy (parsing tabular data correctly).

## Phase 2: Core Backend & Database ✅ DONE
*   [x] Implement Database Schema (Commodities, Markets, PriceEntries).
*   [x] Build API endpoints (`/prices`, `/commodities`, `/markets`).
*   [x] Connect scraper to database.

## Phase 3: Frontend Dashboard ✅ DONE (Jinja2)
*   [x] Build Jinja2 templates with Tailwind CSS.
*   [x] Implement Price Ticker component.
*   [x] Build Commodity Search and Market Filters.
*   [x] Integrate Chart.js for trend visualization.

## Phase 4: Automation & Monitoring
*   [x] Configure Celery + Redis for scheduled scraping.
*   [ ] Setup monitoring for scraper failures (PDF format changes).
*   [ ] Deploy to production.

## Future Enhancements (Backlog)
*   [ ] CSV/Excel export functionality
*   [ ] Price change alerts/notifications
*   [ ] Regional price comparison
*   [ ] Mobile app
