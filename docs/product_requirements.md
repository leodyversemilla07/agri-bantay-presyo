# Product Requirements Document (PRD)
**Project:** Agri Bantay Presyo (Daily Retail Price Monitoring)
**Version:** 2.0 (Simplified - Daily Retail Only)

## 1. Executive Summary
*   **The Problem:** Currently, crucial agricultural price data is locked in static PDF reports scattered across government websites. This makes it difficult for consumers to track daily retail prices effectively.
*   **The Solution:** A unified web portal that automates the extraction of Daily Retail Price Range data from DA-AMAS PDFs, stores it in a structured database, and presents it via an interactive dashboard and public API.

## 2. Project Objectives
*   **Centralize Data:** Aggregate Daily Retail Price Range PDFs into a single search engine.
*   **Automate Ingestion:** Eliminate manual data entry by building a scraper that parses DA-AMAS PDF tables.
*   **Visualize Trends:** Transform static number tables into dynamic line charts.
*   **Open Access:** Provide a clean API for developers and researchers.

## 3. Functional Requirements
*   **Data Ingestion Module:** Source Monitoring (scan DA website daily), PDF Parsing (Daily Retail Price Range), and Standardization (map inconsistent names to a single Commodity ID).
*   **Database & Storage:** Store historical data for Year-over-Year comparison and maintain a Market Master List.
*   **Web Dashboard (Frontend):** Price Ticker, Commodity Search, Interactive Charts, and Market Filters.
*   **API Access:** Public endpoints for latest prices, historical prices, and commodities.

## 4. Scope (v2.0 - Simplified)
**In Scope:**
- Daily Retail Price Range PDF scraping
- Basic commodity/market data storage
- Interactive dashboard with charts
- REST API

**Out of Scope (for now):**
- Weekly Average PDFs
- Supply Index data
- Complex commodity standardization (map.json)
