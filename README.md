# Agri Bantay Presyo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127.1-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

Agri Bantay Presyo is a modernized agricultural price monitoring system designed to centralize and automate the collection of commodity price data from scattered government PDF reports in the Philippines. The platform scrapes data from Department of Agriculture - Agricultural Marketing Assistance Service (DA-AMAS) sources and uses deterministic, layout-aware parsing for PDF extraction. Data is stored in a structured PostgreSQL database for easy querying and analysis.

Built as a full-stack web application, it features:
- **Backend**: FastAPI (Python) with deterministic PDF processing, robust data standardization, RESTful API endpoints, and server-rendered Jinja2 templates.
- **Data Processing**: Intelligent mapping of commodity names, automated backfilling of historical data (2018-Present), and conflict resolution for duplicate entries.

The system provides farmers, consumers, policymakers, and developers with real-time access to agricultural price trends, enabling better decision-making and research through an open API and user-friendly visualization tools.

## Tech Stack

### Backend
- **Framework**: FastAPI 0.127.1 (Python)
- **Database**: PostgreSQL 16
- **PDF Processing**: pdfplumber (for text extraction) + deterministic parsing
- **Language**: Python 3.12

### Frontend
- **Framework**: Jinja2 Templates (Server-rendered)
- **Styling**: Tailwind CSS
- **Interactivity**: Alpine.js + HTMX
- **Charts**: Chart.js

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git
- **CI/CD**: GitHub Actions (lint, test, build, deploy)

## Project Structure

- `app/` - FastAPI application with scraping logic, database models, and Jinja2 templates.
- `docs/` - Project documentation, requirements, and architecture.

## Getting Started

### Prerequisites
- **Docker** and **Docker Compose** (for local development)
- **Python 3.12+** (for backend development)
- **PostgreSQL** (handled by Docker, or install locally for development)

### Local Development

1. Clone the repository
2. Run the stack with Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. Or run services individually:

   **Backend:**
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. Access the application:
   - **Web UI**: http://localhost:8000
   - **Backend API**: http://localhost:8000/api/v1
   - **API Documentation**: http://localhost:8000/docs

## Deployment

Deploy to Heroku, Railway, or VPS with PostgreSQL.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
