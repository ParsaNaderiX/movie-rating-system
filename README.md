# Movie Rating System

## Overview
Movie Rating System is a FastAPI service for listing movies, retrieving details, creating movies, updating movies, deleting movies, and recording ratings. It uses PostgreSQL for persistence and SQLAlchemy for data access.

Technology stack:
- API: FastAPI
- ORM: SQLAlchemy 2.x
- Migrations: Alembic
- Configuration: Pydantic Settings + `.env`
- Database: PostgreSQL
- Server: Uvicorn

## Features
API:
- List movies with pagination and optional filters (title, release year, genre)
- Retrieve detailed movie information including director, genres, and rating aggregates
- Create, update, and delete movies
- Submit ratings for movies with validation

Database:
- Normalized schema for movies, directors, genres, and ratings
- Many-to-many relationship between movies and genres
- Rating aggregates via SQL queries

Observability and errors:
- Structured logging with context-aware fields
- Consistent success and failure response envelopes
- Centralized exception handling for validation and domain errors

Developer tooling:
- Alembic migrations
- Seed SQL and optional Python seed utilities
- Docker Compose for local PostgreSQL

## Architecture
Request flow:

```
Client
  |
  v
FastAPI (app/main.py)
  |
  v
Controllers (app/controller)
  |
  v
Services (app/services)
  |
  v
Repositories (app/repositories)
  |
  v
SQLAlchemy ORM (app/models, app/db)
  |
  v
PostgreSQL
```

Key components:
- Controllers define HTTP routes and request/response models.
- Services enforce business rules and orchestrate repository calls.
- Repositories contain SQLAlchemy queries and aggregates.
- Exception handlers normalize error responses.
- Logging is configured once at app startup.

## Installation
Prerequisites:
- Python 3.14 or newer (per `pyproject.toml`)
- Poetry
- PostgreSQL 16 (or Docker)

Step-by-step setup:
1. Install dependencies:

```bash
poetry install
```

2. Configure the database URL in `.env`:

```env
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/movierating
```

3. Start PostgreSQL (Docker Compose is provided):

```bash
docker-compose up -d
```

4. Run migrations:

```bash
poetry run alembic upgrade head
```

## Usage
Run the API server:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

Response:

```json
{"status":"success","data":{"ok":true}}
```

### Database seeding
Seed with SQL (requires `psql`):

```bash
psql "$DATABASE_URL" -f scripts/seeddb.sql
```

Seed without `psql`:

```bash
poetry run python scripts/run_seed.py
```

Seed verification:

```bash
poetry run python scripts/seed_check.py
```

## API Documentation
Base path: `/api/v1/movies`

Response envelopes:

```json
{"status":"success","data":{}}
```

```json
{"status":"failure","error":{"code":422,"message":"Validation error"}}
```

Endpoints:

| Method | Path | Description | Status Codes |
| --- | --- | --- | --- |
| GET | `/api/v1/movies` | List movies with filters and pagination | 200, 422 |
| GET | `/api/v1/movies/{movie_id}` | Retrieve movie details | 200, 404 |
| POST | `/api/v1/movies` | Create a movie | 201, 404, 422 |
| PUT | `/api/v1/movies/{movie_id}` | Update a movie | 200, 404, 422 |
| DELETE | `/api/v1/movies/{movie_id}` | Delete a movie | 204, 404 |
| POST | `/api/v1/movies/{movie_id}/ratings` | Create a rating for a movie | 201, 404, 422 |
| GET | `/health` | Service health check | 200 |

### List movies
Query parameters:

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | integer | No | Page number (default 1) |
| `page_size` | integer | No | Page size (default 10) |
| `title` | string | No | Substring match on title |
| `release_year` | integer | No | Exact release year |
| `genre` | string | No | Exact genre name (case-insensitive) |

Example:

```bash
curl "http://localhost:8000/api/v1/movies?page=1&page_size=2&genre=Drama"
```

Example response (using `scripts/seeddb.sql`):

```json
{
  "status": "success",
  "data": {
    "page": 1,
    "page_size": 2,
    "total_items": 3,
    "items": [
      {
        "id": 1,
        "title": "Inception",
        "release_year": 2010,
        "director": {"id": 1, "name": "Christopher Nolan"},
        "genres": ["Sci-Fi", "Drama"],
        "average_rating": 8.5,
        "ratings_count": 2
      },
      {
        "id": 2,
        "title": "Little Women",
        "release_year": 2019,
        "director": {"id": 2, "name": "Greta Gerwig"},
        "genres": ["Drama", "Comedy"],
        "average_rating": 7.0,
        "ratings_count": 1
      }
    ]
  }
}
```

### Get movie detail
Example:

```bash
curl http://localhost:8000/api/v1/movies/1
```

Example response (using `scripts/seeddb.sql`):

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "Inception",
    "release_year": 2010,
    "director": {
      "id": 1,
      "name": "Christopher Nolan",
      "birth_year": 1970,
      "description": "Writer/director known for complex high-concept films"
    },
    "genres": ["Sci-Fi", "Drama"],
    "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt",
    "average_rating": 8.5,
    "ratings_count": 2
  }
}
```

### Create a movie
Request body (`app/schemas/movie.py`):

```json
{
  "title": "New Movie",
  "director_id": 1,
  "release_year": 2024,
  "cast": "Actor A, Actor B",
  "genres": [1, 2]
}
```

Example:

```bash
curl -X POST http://localhost:8000/api/v1/movies \
  -H "Content-Type: application/json" \
  -d '{"title":"New Movie","director_id":1,"release_year":2024,"cast":"Actor A, Actor B","genres":[1,2]}'
```

### Update a movie
Request body (`app/schemas/movie.py`):

```json
{
  "title": "Updated Title",
  "genres": [1, 3]
}
```

Example:

```bash
curl -X PUT http://localhost:8000/api/v1/movies/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","genres":[1,3]}'
```

### Delete a movie
Example:

```bash
curl -X DELETE http://localhost:8000/api/v1/movies/1
```

### Create a rating
Request body (`app/schemas/movie.py`):

```json
{
  "score": 9
}
```

Example:

```bash
curl -X POST http://localhost:8000/api/v1/movies/1/ratings \
  -H "Content-Type: application/json" \
  -d '{"score":9}'
```

### Error codes

| Code | When it occurs | Response shape |
| --- | --- | --- |
| 404 | Movie or related resource not found | `{"status":"failure","error":{"code":404,"message":"..."}}` |
| 422 | Validation error (request body or domain rule) | `{"status":"failure","error":{"code":422,"message":"..."}}` |

## Configuration
Environment variables:

| Variable | Required | Description | Example |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | SQLAlchemy database URL | `postgresql+psycopg2://user:pass@localhost:5432/movierating` |

Settings are loaded via `app/config.py` from `.env` in the repository root.

## Database schema
Tables:

| Table | Columns | Notes |
| --- | --- | --- |
| `directors` | `id`, `name`, `birth_year`, `description` | One-to-many with `movies` |
| `movies` | `id`, `title`, `director_id`, `release_year`, `cast` | `director_id` FK to `directors` |
| `genres` | `id`, `name`, `description` | Unique `name` |
| `movie_genres` | `movie_id`, `genre_id` | Join table for many-to-many |
| `movie_ratings` | `id`, `movie_id`, `score`, `created_at` | `movie_id` FK to `movies` |

Relationships:
- One director has many movies.
- One movie has many ratings.
- Movies and genres are many-to-many via `movie_genres`.

## Project structure
```
.
├─ alembic/
│  ├─ versions/
│  │  └─ 0001_initial.py
│  ├─ env.py
│  └─ script.py.mako
├─ app/
│  ├─ controller/
│  │  ├─ __init__.py
│  │  └─ movies.py
│  ├─ db/
│  │  ├─ __init__.py
│  │  └─ database.py
│  ├─ exceptions/
│  │  ├─ __init__.py
│  │  ├─ handlers.py
│  │  └─ http_exceptions.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ director.py
│  │  ├─ genre.py
│  │  ├─ movie.py
│  │  └─ movie_rating.py
│  ├─ repositories/
│  │  ├─ __init__.py
│  │  ├─ movie.py
│  │  └─ movies_repository.py
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ common.py
│  │  └─ movie.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ movie.py
│  │  └─ movies_service.py
│  ├─ __init__.py
│  ├─ config.py
│  ├─ logging_config.py
│  └─ main.py
├─ scripts/
│  ├─ run_seed.py
│  ├─ seed_check.py
│  └─ seeddb.sql
├─ .env
├─ .env.example
├─ alembic.ini
├─ docker-compose.yml
├─ poetry.lock
├─ pyproject.toml
└─ README.md
```

## Design decisions
- Service and repository layers separate business logic from persistence, making query logic explicit and reducing controller complexity.
- Rating aggregates are calculated with SQL queries rather than computed in Python, which avoids N+1 issues and keeps list endpoints performant.
- Pydantic response models use field aliases (`avg_rating` to `average_rating`, `rating_count` to `ratings_count`) to align internal naming with API output.
- Centralized exception handlers in `app/exceptions/handlers.py` enforce a consistent error shape for both validation and domain errors.
- Logging uses a safe extra filter to ensure context fields exist, enabling structured logs without format errors.

## Troubleshooting
- `DATABASE_URL` not set: set it in `.env` or your shell; `app/config.py` requires it at startup.
- Connection refused to PostgreSQL: ensure the Docker container is running (`docker-compose up -d`) and `DATABASE_URL` matches the port.
- `psql` not found: use the Python seeder (`scripts/run_seed.py`) instead.
- Validation errors on rating: `score` must be between 1 and 10.
- 404 on movie endpoints: verify the `movie_id` exists in the database.
