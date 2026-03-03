# frontend/Dockerfile

FROM python:3.11-slim AS build
WORKDIR /app

RUN apt-get update && apt-get install -y curl unzip \
  && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
  && apt-get install -y nodejs \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exporta SOLO el frontend (estático) sin zip -> queda en .web/build/client/
RUN reflex export --frontend-only --no-zip

FROM nginx:alpine
# Nginx por defecto escucha en 80; lo cambiamos a 8080 para Cloud Run
RUN sed -i 's/listen\s\+80;/listen 8080;/' /etc/nginx/conf.d/default.conf

COPY --from=build /app/.web/build/client /usr/share/nginx/html

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]