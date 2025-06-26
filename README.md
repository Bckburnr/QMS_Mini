# QMS Mini — Issue Tracking & Audit Log System

A minimal Flask/SQLite app for tracking issues (deviations, CAPAs, equipment problems) with full audit logging, designed to mimic real-world pharma/biotech validation logic.

## Features

- Log new issues (title, description, status)
- Change status (Open, In Progress, Closed)
- Automatic audit trail for every change
- Dashboard of all issues and their history
- Soft delete/close issues (full traceability)
- Persistent data (SQLite)

## How to Run

1. Clone this repo and `cd` into the folder:

    ```bash
    git clone <your-link-here>
    cd qms-mini
    ```

2. (Recommended) Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\\Scripts\\activate
    ```

3. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```

4. Start the app:
    ```bash
    python app.py
    ```

5. Visit `http://localhost:5000` in your browser.

## Why?

- Real CRUD logic, SQLite database
- Compliance-style audit logging
- Easy to expand (users, reporting, exports, etc.)

---

Made by [Charles Kwena]
