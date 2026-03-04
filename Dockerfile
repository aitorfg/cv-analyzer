FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias mínimas típicas (Pillow/pdfplumber suelen ir bien sin mucho extra,
# pero esto evita sustos con builds nativos en algunos entornos)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run expone el puerto en $PORT
CMD ["sh", "-c", "reflex run --env prod --host 0.0.0.0 --port ${PORT:-8080}"]