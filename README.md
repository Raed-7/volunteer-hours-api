# Volunteer Hours API

FastAPI + SQLAlchemy + Alembic REST API for volunteer, event, shift, attendance, and analytics management with JWT auth and CSV import tools.

## Features
- JWT auth with organiser/admin roles
- CRUD endpoints for volunteers, events, and shifts
- Attendance check-in/check-out workflow with validations
- Analytics endpoints (leaderboard, awards tiers, event coverage, reliability)
- CSV import scripts and admin import endpoint
- Alembic migrations
- Pytest test suite + GitHub Actions CI

## Tech Stack
- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic
- python-jose + passlib[bcrypt]
- pytest + httpx

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Open docs: `http://127.0.0.1:8000/docs`

## Environment Variables
See `.env.example`.
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

## Migrations
```bash
alembic upgrade head
```

## Run Tests
```bash
pytest
```

## Example cURL
```bash
# Register
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Admin","email":"admin@example.com","password":"password123","role":"admin"}'

# Login
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Create volunteer
curl -X POST http://127.0.0.1:8000/volunteers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Jane Doe","email":"jane@example.com"}'
```

## Demo Script Commands
```bash
python scripts/import_volunteers.py
python scripts/import_events.py
python scripts/import_attendance.py
python scripts/import_all.py
```

## Import Notes
- CSV files are read from `data/` using `utf-8-sig`.
- Volunteer duplicate strategy: if email exists, dedupe by email; otherwise dedupe by full_name.

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
tests/
scripts/
docs/
```

## Documentation Export
API docs guide: `docs/API_DOCUMENTATION.md`
