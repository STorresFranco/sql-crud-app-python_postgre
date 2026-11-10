# 💸 Expense Tracker | PostgreSQL · FastAPI · Streamlit

A full-stack expense tracking application built to explore relational database operations, REST APIs, and interactive analytics.

Users can create, retrieve, update, and delete expense records, run custom filtered queries, and explore spending summaries through a Streamlit interface. The backend uses FastAPI and PostgreSQL. **The current demo runs locally using Docker Compose; the former Railway deployment is no longer required.**

## Application preview

| CRUD operations | Analytics dashboard |
|---|---|
| ![CRUD interface](assets/crud_example.png) | ![Analytics dashboard](assets/analytics_dashboard.png) |

## Architecture

```mermaid
flowchart LR
    A[Streamlit UI] -->|HTTP requests| B[FastAPI REST API]
    B -->|SQL via psycopg2| C[(PostgreSQL 16)]
    D[Docker Compose] -.->|Runs and initializes| C
    E[expense_pg_clean.sql] -.->|Seeds first run| C
```

## Features

- Create expense records with date, amount, category, and notes
- Retrieve expenses by date or using custom filters
- Update and delete records through filtered requests
- Explore expense summaries and charts across a selected date range
- Inspect API endpoints using FastAPI's interactive Swagger documentation
- Start a seeded PostgreSQL database locally without a hosted database account

## Technology

| Layer | Tools |
|---|---|
| Frontend | Streamlit, Pandas, Plotly |
| API | FastAPI, Pydantic, Uvicorn |
| Database | PostgreSQL 16, psycopg2 |
| Local infrastructure | Docker Compose |
| Tests | pytest |

## Run locally (Windows PowerShell)

**Prerequisites:** Git, Docker Desktop with Linux containers enabled, and Python 3.12. The dependencies must be tested in a clean Python 3.12 environment before treating this setup as verified.

### 1. Clone the repository

```powershell
git clone https://github.com/STorresFranco/sql-crud-app-python_postgre.git
cd sql-crud-app-python_postgre
```

### 2. Configure local settings

```powershell
Copy-Item .env.example .env
```

The example should contain:

```dotenv
DATABASE_URL=postgresql://expense_user:expense_local_dev@127.0.0.1:5433/expense_db
```

These are **local-only development credentials**, matching the Docker Compose configuration; do not reuse them in an internet-accessible deployment. The application loads `.env` in the database helper via `python-dotenv`. `.env.example` is a template and is **not** automatically loaded by the application.

The Streamlit frontend should use `http://127.0.0.1:8000` as its default API URL (with an optional `API_URL` environment-variable override). No Streamlit secrets file is needed for local execution.

### 3. Start the database

Ensure Docker Desktop is running, then:

```powershell
docker compose up -d
docker compose ps
```

Wait until the `expense_postgres` container is healthy. The database listens on **127.0.0.1:5433** on your computer and **5432** inside Docker. The `backend/expense_pg_clean.sql` file initializes and seeds the database **only when the Docker data volume is first created**.

To inspect the database:

```powershell
docker exec -it expense_postgres psql -U expense_user -d expense_db
```

Within `psql`, run `SELECT COUNT(*) FROM expenses;` and leave with `\q`.

### 4. Install Python dependencies

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

### 5. Start FastAPI

From the repository root, in the first terminal:

```powershell
python -m uvicorn backend.server:server --host 127.0.0.1 --port 8000
```

Open the API documentation at **http://127.0.0.1:8000/docs** and check `GET /`.

### 6. Start Streamlit

From the repository root, in a **second terminal** with the same Python environment activated:

```powershell
python -m streamlit run frontend/streamlit_app.py
```

Open **http://localhost:8501**. Keep Docker and FastAPI running while using the app.

### 7. Verify the workflow

1. Retrieve the seeded expense records using the **Fetch Records** tab.
2. Create one test expense using the **Create Records** tab.
3. Update and delete that test record using a **specific filter** (such as its unique notes value).
4. Run the analytics dashboard using the seeded data's date range.

**Caution:** Until empty-filter validation is enforced in the backend, never run update or delete with an empty `where_info` object.

### Stop the database

```powershell
docker compose down
```

This stops and removes the container but **preserves** the named database volume. Avoid `docker compose down -v` unless you intentionally want to delete all locally stored database data and start fresh.

## Repository structure

```text
sql-crud-app-python_postgre/
├── assets/                       # Screenshots
├── backend/
│   ├── db_helper_postgre.py      # Database access and query logic
│   ├── expense_pg_clean.sql      # Database schema and sample data
│   └── server.py                 # FastAPI routes
├── frontend/
│   └── streamlit_app.py          # Web UI
├── test/                         # Python tests
├── docker-compose.yml           # Local PostgreSQL service
├── .env.example                 # Local configuration template
├── requirements.txt
└── readme.md
```

## Notes and limitations

- The former Railway deployment is not part of the current reproducible setup.
- The demo uses local sample records, not a multiuser hosted database.
- The project is intended to demonstrate SQL CRUD operations, API integration, and basic analytics. It is not presented as a production-hardened expense management service.
- Tests should be run against a disposable test database because they may create or modify records.
