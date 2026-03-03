FROM python:3.11-slim AS build
WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl unzip \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exporta SOLO el frontend (Reflex 0.6.0 genera un zip)
RUN reflex export --frontend-only \
 && ls -la \
 && mkdir -p /out \
 && unzip -o "*.zip" -d /out \
 && find /out -maxdepth 3 -type f -name "index.html" -print

FROM nginx:alpine
# Cloud Run espera 8080
RUN sed -i 's/listen\s\+80;/listen 8080;/' /etc/nginx/conf.d/default.conf

# Copia el build exportado
COPY --from=build /out /usr/share/nginx/html

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]