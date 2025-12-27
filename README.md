# Bantay Presyo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Bantay Presyo is a modernized agricultural price monitoring system designed to centralize and automate the collection of commodity price data from scattered government PDF reports in the Philippines. The platform scrapes data from Department of Agriculture - Agricultural Marketing Assistance Service (DA-AMAS) sources, including weekly averages, daily prevailing prices, and supply indices, then stores it in a structured PostgreSQL database for easy querying and analysis.

Built as a full-stack web application, it features:
- **Backend**: FastAPI (Python) with automated PDF parsing using pdfplumber, scheduled scraping via Celery + Redis, and RESTful API endpoints
- **Frontend**: Next.js (React) dashboard with interactive price charts, commodity tables, market filters, and a live price ticker
- **Data Processing**: Intelligent standardization of commodity names, spatial table extraction from PDFs, and support for multiple report types

The system provides farmers, consumers, policymakers, and developers with real-time access to agricultural price trends, enabling better decision-making and research through an open API and user-friendly visualization tools.

## Project Structure

This is a monorepo containing both backend and frontend code:

- `backend/` - FastAPI application with scraping, API, and database logic
- `frontend/` - Next.js dashboard application
- `docs/` - Project documentation, requirements, and architecture

## Getting Started

### Prerequisites
- **Docker** and **Docker Compose** (for local development)
- **Node.js 20+** (for frontend development)
- **Python 3.12+** (for backend development)
- **PostgreSQL** (handled by Docker, or install locally for development)
- **PostgreSQL** (handled by Docker, or install locally for development)

### Local Development

1. Clone the repository
2. Run the full stack with Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. Or run services individually:

   **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Deployment

The backend and frontend are designed to be deployed separately:

- **Backend**: Deploy to Heroku, Railway, or VPS with PostgreSQL
- **Frontend**: Deploy to Vercel, Netlify, or similar static hosting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.