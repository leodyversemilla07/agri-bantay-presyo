# Agri Bantay Presyo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127.1-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-black.svg)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

Agri Bantay Presyo is a modernized agricultural price monitoring system designed to centralize and automate the collection of commodity price data from scattered government PDF reports in the Philippines. The platform scrapes data from Department of Agriculture - Agricultural Marketing Assistance Service (DA-AMAS) sources and uses **Google Gemini AI** to intelligently parse complex, inconsistent PDF layouts. Data is stored in a structured PostgreSQL database for easy querying and analysis.

Built as a full-stack web application, it features:
- **Backend**: FastAPI (Python) with **AI-powered PDF processing**, robust data standardization, and RESTful API endpoints.
- **Frontend**: Next.js (React) dashboard with a multi-page interface (Overview, Markets, Analytics), interactive charts, and real-time search.
- **Data Processing**: Intelligent mapping of commodity names, automated backfilling of historical data (2018-Present), and conflict resolution for duplicate entries.

The system provides farmers, consumers, policymakers, and developers with real-time access to agricultural price trends, enabling better decision-making and research through an open API and user-friendly visualization tools.

## Tech Stack

### Backend
- **Framework**: FastAPI 0.127.1 (Python)
- **Database**: PostgreSQL 16
- **AI Engine**: Google Gemini 3 Flash Preview (via Google Gen AI SDK)
- **PDF Processing**: pdfplumber (for text extraction) + Gemini (for parsing)
- **Language**: Python 3.12

### Frontend
- **Framework**: Next.js 16.1.1 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **Visualization**: Recharts
- **Icons**: Lucide React
- **Runtime**: Node.js 20

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git
- **CI/CD**: GitHub Actions (planned)

## Project Structure

This is a monorepo containing both backend and frontend code:

- `backend/` - FastAPI application with scraping logic, AI integration, and database models.
- `frontend/` - Next.js application with `analytics`, `markets`, and `overview` pages.
- `docs/` - Project documentation, requirements, and architecture.

## Getting Started

### Prerequisites
- **Docker** and **Docker Compose** (for local development)
- **Node.js 20+** (for frontend development)
- **Python 3.12+** (for backend development)
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