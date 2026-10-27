# Healthcare Backend

REST API for managing patients, doctors, and their assignments. Built with Django 5.2, Django REST Framework, and PostgreSQL.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.2 + DRF 3.16 |
| Database | PostgreSQL 16 via psycopg3 (binary protocol) |
| Auth | JWT via djangorestframework-simplejwt |
| Server | Granian (Rust HTTP/ASGI) |
| JSON | orjson (Rust-backed renderer/parser) |
| Compression | Brotli + Zstd via django-compression-middleware |
| Docs | drf-spectacular (OpenAPI 3.0) |
| Linting | ruff + mypy + django-stubs |
| Testing | pytest + factory-boy + pytest-xdist |

## Quick Start

### Prerequisites

- Python 3.13+
- Docker (for PostgreSQL)
- [uv](https://docs.astral.sh/uv/) package manager

### 1. Start PostgreSQL

```bash
docker run -d \
  --name healthcare_pg \
  -e POSTGRES_USER=healthcare_user \
  -e POSTGRES_PASSWORD=healthcare_pass \
  -e POSTGRES_DB=healthcare_db \
  -p 5433:5432 \
  --restart unless-stopped \
  postgres:16-alpine \
  -c shared_buffers=256MB \
  -c work_mem=16MB
```

### 2. Install & Configure

```bash
uv sync
cp .env.example .env
```

### 3. Migrate & Run

```bash
make migrate
make serve
```

The API is now at `http://localhost:8000`. Swagger docs at `/api/docs/`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register with email, name, password |
| POST | `/api/auth/login/` | Get JWT access + refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh JWT token |
| GET/POST | `/api/patients/` | List (own) / Create patient |
| GET/PUT/DELETE | `/api/patients/<id>/` | Retrieve / Update / Delete patient |
| GET/POST | `/api/doctors/` | List (all) / Create doctor |
| GET/PUT/DELETE | `/api/doctors/<id>/` | Retrieve / Update / Delete doctor |
| GET/POST | `/api/mappings/` | List / Assign doctor to patient |
| GET/DELETE | `/api/mappings/<id>/` | Retrieve / Remove mapping |
| GET | `/api/health/` | Health check (DB connectivity) |
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/schema/` | OpenAPI schema (JSON) |

## Development

```bash
make lint              # ruff check + format
make test              # pytest with coverage
make lint-migrations   # django-migration-linter
make security-check    # Django deploy checks
make check             # all of the above
```

## Project Structure

```
config/                 # Django settings (base/dev/prod/test)
apps/
  accounts/             # Custom User model, JWT auth, permissions
  patients/             # Patient CRUD (user-scoped)
  doctors/              # Doctor CRUD (all-visible)
  mappings/             # Patient-Doctor assignments (select_for_update)
  core/                 # Shared: orjson renderer/parser, UUID7 mixin
```
