FROM python:3.11-slim AS build
WORKDIR /app

RUN apt-get update && apt-get install -y curl unzip \
  && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
  && apt-get install -y nodejs \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN reflex export --frontend-only --no-zip \
 && OUT="$(find /app -maxdepth 6 -type d -name client | head -n 1)" \
 && echo "Export output client dir: $OUT" \
 && test -n "$OUT" \
 && mkdir -p /out \
 && cp -r "$OUT"/. /out/

FROM nginx:alpine
RUN sed -i 's/listen\s\+80;/listen 8080;/' /etc/nginx/conf.d/default.conf
COPY --from=build /out /usr/share/nginx/html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]