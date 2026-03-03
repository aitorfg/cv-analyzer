FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run
ENV PORT=8080
EXPOSE 8080

# Asegura que escucha en 0.0.0.0 y en el puerto de Cloud Run
CMD ["sh", "-c", "reflex run --env prod --host 0.0.0.0 --port ${PORT}"]