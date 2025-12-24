## Database migrations

Set `DATABASE_URL` in `.env` (or your shell) before running Alembic.

```bash
alembic upgrade head
```

## Seeding the database (development)

1. Ensure `DATABASE_URL` is set to your Postgres database (example):

	- Unix / macOS:

	  ```bash
	  export DATABASE_URL=postgresql://user:password@localhost:5432/moviedb
	  ```

	- Windows PowerShell:

	  ```powershell
	  $env:DATABASE_URL = 'postgresql://user:password@localhost:5432/moviedb'
	  ```

2. Run migrations:

	```bash
	alembic upgrade head
	```

3. Load the seed SQL file with `psql` (or any Postgres client):

	```bash
	psql "$DATABASE_URL" -f scripts/seeddb.sql
	```

	- On PowerShell you can use the same `psql` command once `$env:DATABASE_URL` is set.

4. Install the DB client dependency for the lightweight check script (optional but recommended):

	```bash
	pip install psycopg[binary]
	# or
	pip install psycopg2-binary
	```

5. Run the quick seed check which prints counts per table:

	```bash
	python scripts/seed_check.py
	```

This seed setup is intentionally minimal and meant for development/grading purposes. The `scripts/seeddb.sql` file inserts sample directors, genres, movies, movie_genres, and movie_ratings. The `scripts/seed_check.py` script connects using `DATABASE_URL` and prints row counts for those tables.
