# ScoutMyCar - Project Rules & Guidelines for Antigravity

This repository contains **ScoutMyCar**, a web application designed to connect car buyers in Uttarakhand with authorized **Mahindra dealerships across Haldwani (UK-04) and Rudrapur (UK-06)**.

## Architecture Overview

- **Backend**: Python 3.12 with FastAPI (`app/main.py`), SQLite (`scoutmycar.db`), and Pydantic models (`app/models.py`).
- **Database Layer**: `app/database.py` defines schemas for `dealerships`, `cars`, `variants`, `inventory`, `inquiries`, and `stock_alerts`.
- **Seed Data**: `app/seed_data.py` seeds authentic dealership information for:
  - Dee Kay Motors (Mahindra Haldwani)
  - Nainital Motors (Mahindra Haldwani)
  - Dee Kay Motors (Mahindra Rudrapur)
  - Ananya Mahindra (Rudrapur)
- **Frontend**:
  - `app/templates/index.html`: Customer portal with live stock explorer, bank & finance partners, WhatsApp connect, and Google Sheet inquiries.
  - `app/static/css/styles.css`: Styling with Tailwind CSS and Lucide icons.
- **Tests**: `tests/test_app.py` contains automated test cases.

## Development Commands

- Virtual environment: `.venv\Scripts\Activate.ps1`
- Start server: `python run.py` (serves at http://127.0.0.1:8000)
- Run tests: `python -m unittest tests/test_app.py`
- Re-seed database: `python -m app.seed_data`
