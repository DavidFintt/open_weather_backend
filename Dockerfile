FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY tests/ tests/
COPY .env.example .env

RUN mkdir -p logs

RUN python -m pytest tests/ -v --tb=short

EXPOSE 8500

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8500"]
