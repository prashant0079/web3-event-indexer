FROM python:3.11-slim

RUN pip install --no-cache-dir poetry==1.8.2

WORKDIR /app
COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
 && poetry install --only main --no-root --no-interaction

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]