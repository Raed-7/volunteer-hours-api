# Volunteer Hours Management API

A coursework-friendly backend API for managing volunteers and events with JWT authentication and role-based access.

## Stack
- Python 3.11+
- FastAPI
- SQLAlchemy ORM
- Alembic migrations
- Pydantic schemas
- SQLite (local dev)
- Pytest
- JWT auth (`python-jose` + `passlib`)

## Project Structure
```text
app/
  main.py
  core/
  db/
  models/
  schemas/
  routers/
  services/
  utils/
tests/
alembic/
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run Migrations
```bash
alembic upgrade head
```

## Run API Locally
```bash
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## Run Tests
```bash
pytest -q
```

## Implemented Today
- JWT auth endpoints: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- Volunteer CRUD endpoints under `/volunteers`
- Event CRUD endpoints under `/events`
- Role model support: `admin`, `organiser`
- Protected volunteer/event routes
