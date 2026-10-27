# Healthcare Backend

A production-grade REST API for managing patients, doctors, and their assignments — built as a take-home assessment to demonstrate real-world Django engineering beyond basic CRUD.

Every non-trivial decision is deliberate: UUID7 primary keys prevent IDOR, object-level permissions enforce ownership, `select_for_update` eliminates race conditions on mapping creation, and query counts are enforced in tests so N+1 regressions are caught in CI, not in production.

---

## Quick Start

```bash
git clone https://github.com/Lakshit-Gupta/Healthcare_Backend.git
cd Healthcare_Backend
docker-compose up --build
```

API → [http://localhost:8000](http://localhost:8000)  
Swagger UI → [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

That's it. Compose boots PostgreSQL with tuned settings, runs migrations, and starts the API server automatically.

---

## What This Is

A backend system with three domain models — `User`, `Patient`, and `Doctor` — and an explicit many-to-many `PatientDoctorMapping` through-model. Users register with email, authenticate via JWT, and can only see and manage their own patients. Any authenticated user can view and create doctors. Mappings are user-scoped: you can only assign a doctor to a patient you own.

---

## Architecture

| Layer | Choice | Why |
|---|---|---|
| Framework | Django 5.2 + DRF 3.16 | Spec requirement |
| Database | PostgreSQL 16 via psycopg3 binary protocol | 2–3× faster than psycopg2 on large result sets |
| Auth | JWT (djangorestframework-simplejwt) | Spec requirement; 30 min access / 7 day refresh with rotation |
| ASGI server | Granian (Rust/hyper) | Replaces gunicorn + uvicorn; built-in multiprocess, lower tail latency |
| JSON | orjson (Rust) | 10–40× faster than stdlib; serializes UUID and datetime natively |
| Compression | Brotli + Zstd | 20–30% smaller payloads than gzip at same CPU cost |
| Primary keys | UUID7 (time-ordered) | Prevents IDOR; time-ordered avoids B-tree page splits unlike UUID4 |
| Permissions | Custom `IsOwner` / `IsPatientOwner` | Object-level auth; most candidates only use `IsAuthenticated` |
| Concurrency | `select_for_update()` on mapping create | Eliminates race condition before `UniqueConstraint` fires |
| Docs | drf-spectacular (OpenAPI 3.0) | Auto-generated Swagger; reviewers can test without Postman |
| Linting | ruff + mypy + django-stubs | Strict type checking on every view, serializer, and model |
| Testing | pytest + factory-boy + assertNumQueries | Query count assertions catch N+1 in CI |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | ✗ | Register with email, name, password |
| POST | `/api/auth/login/` | ✗ | Get JWT access + refresh tokens |
| POST | `/api/auth/token/refresh/` | ✗ | Refresh access token |
| GET / POST | `/api/patients/` | ✓ | List own patients / create patient |
| GET / PUT / DELETE | `/api/patients/<id>/` | ✓ owner | Retrieve / update / delete |
| GET / POST | `/api/doctors/` | ✓ | List all doctors / create doctor |
| GET / PUT / DELETE | `/api/doctors/<id>/` | ✓ owner | Retrieve / update / delete |
| GET / POST | `/api/mappings/` | ✓ | List / assign doctor to patient |
| GET / DELETE | `/api/mappings/<id>/` | ✓ owner | Retrieve / remove mapping |
| GET | `/api/health/` | ✗ | Health check with DB connectivity |
| GET | `/api/docs/` | ✗ | Swagger UI |

---

## Project Structure

```
config/
  settings/           # base / development / production / test
  urls.py             # root router
apps/
  core/               # orjson renderer+parser, UUID7+timestamp mixins, health check
  accounts/           # custom User model, JWT endpoints, IsOwner permissions
  patients/           # Patient CRUD — user-scoped, composite index, soft delete
  doctors/            # Doctor CRUD — specialization filtering
  mappings/           # PatientDoctorMapping — UniqueConstraint, select_for_update
```

---

## Local Development (without Docker)

```bash
uv sync
cp .env.example .env   # edit DB_HOST/PORT if needed
make migrate
make serve
```

```bash
make test              # pytest with coverage
make lint              # ruff + mypy
make lint-migrations   # django-migration-linter
make check             # all of the above
```
