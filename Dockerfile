FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml .

RUN python - <<'PY'
import subprocess
import sys
import tomllib

with open("pyproject.toml", "rb") as handle:
    data = tomllib.load(handle)

deps = data.get("project", {}).get("dependencies", [])
if not deps:
    raise SystemExit("No dependencies found in [project.dependencies]")

cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir", *deps]
subprocess.check_call(cmd)
PY

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
