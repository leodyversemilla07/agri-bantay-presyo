# Product Requirements Document (PRD)
**Project:** Agri Bantay Presyo (Modernized Agricultural Price Monitoring System)
**Version:** 1.0 (Draft)

## 1. Executive Summary
*   **The Problem:** Currently, crucial agricultural price data is locked in static PDF reports scattered across government websites. This makes it difficult for farmers, consumers, and policymakers to track trends, compare prices, or analyze historical data effectively.
*   **The Solution:** A unified web portal that automates the extraction of data from these PDFs, stores it in a structured database, and presents it via an interactive dashboard and public API.

## 2. Project Objectives
*   **Centralize Data:** Aggregate disjointed PDF reports (Weekly Average, Daily Prevailing, Supply Index) into a single search engine.
*   **Automate Ingestion:** Eliminate manual data entry by building a scraper that parses DA-AMAS PDF tables.
*   **Visualize Trends:** Transform static number tables into dynamic line charts.
*   **Open Access:** Provide a clean API for other developers and researchers to use official price data.

## 3. Functional Requirements
*   **Data Ingestion Module:** Source Monitoring (scan DA websites daily), PDF Parsing (Weekly, Daily, and Index Handlers), and Standardization (map inconsistent names to a single Commodity ID).
*   **Database & Storage:** Store historical data for Year-over-Year comparison and maintain a Market Master List.
*   **Web Dashboard (Frontend):** Price Ticker, Commodity Search, Interactive Charts, and Market Filters.
*   **API Access:** Public endpoints for latest prices, historical prices, and commodities.
