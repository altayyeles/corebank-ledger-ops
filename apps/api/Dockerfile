
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir ".[dev]"
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic
COPY src /app/src
EXPOSE 8000
