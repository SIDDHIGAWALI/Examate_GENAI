FROM python:3.12-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=10 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]