# Development Roadmap
**Project:** Agri Bantay Presyo

## Phase 1: Foundation & "Hello World" Prototype
*   [ ] Set up FastAPI project structure with PostgreSQL connection.
*   [ ] Create basic PDF Scraper for one document type (e.g., Daily Prevailing).
*   [ ] Implement "Spatial Table Extraction" using `pdfplumber`.
*   [ ] Verify data extraction accuracy (parsing tabular data correctly).

## Phase 2: Core Backend & Database
*   [ ] Implement full Database Schema (Commodities, Markets, PriceEntries).
*   [ ] Expand Scraper to handle Weekly Average and Supply Index PDFs.
*   [ ] Build `map.json` for commodity standardization.
*   [ ] Develop API endpoints (`/prices`, `/commodities`).

## Phase 3: Frontend Development (Next.js)
*   [ ] Initialize Next.js project with a mobile-first design system.
*   [ ] Build "Price Ticker" and "Commodity Search" components.
*   [ ] Integrate Charting library (e.g., Recharts) for trend visualization.
*   [ ] Connect Frontend to Backend API.

## Phase 4: Automation & Deployment
*   [ ] Configure Celery + Redis for scheduled daily scraping tasks.
*   [ ] Deploy Backend and Database (e.g., Heroku, Railway, or VPS).
*   [ ] Deploy Frontend (e.g., Vercel).
*   [ ] Setup monitoring for scraper failures (since PDF formats change).
