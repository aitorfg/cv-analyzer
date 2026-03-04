FROM python:3.12-slim

# --- System deps needed by Reflex (frontend build) ---
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8080

CMD ["bash", "-lc", "reflex run --env prod --single-port --backend-host 0.0.0.0 --backend-port ${PORT} --frontend-port ${PORT}"]