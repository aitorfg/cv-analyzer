# CV Analyzer 🔍

Herramienta que analiza la compatibilidad de un CV con una oferta de trabajo usando **Gemini API + LangChain**, desplegada en **Google Cloud Run** con frontend en **Reflex**.

## Stack técnico

- **Backend**: FastAPI + LangChain + Gemini API (Cloud Run)
- **Frontend**: Reflex (Python)
- **Cloud**: GCP — Cloud Run, Secret Manager
- **Extracción PDF**: pdfplumber

## Arquitectura

```
Frontend Reflex (Cloud Run)
        ↓  HTTP POST /api/v1/analyze
Backend FastAPI (Cloud Run)
        ↓
  pdfplumber → extracción texto PDF
        ↓
  LangChain + Gemini 1.5 Flash
        ↓
  JSON estructurado → frontend
```

## Output del análisis

```json
{
  "match_score": 78,
  "strengths": ["GCP", "Python avanzado", "automatización event-driven"],
  "gaps": ["Kubernetes", "Apache Spark"],
  "recommendations": "Reforzar experiencia en...",
  "summary": "Perfil sólido para el rol...",
  "seniority_match": "match"
}
```

---

## Ejecución en local

### 1. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
export GEMINI_API_KEY="tu_api_key_aqui"

# Arrancar servidor
uvicorn app.main:app --reload --port 8080
```

Backend disponible en: `http://localhost:8080`
Documentación Swagger: `http://localhost:8080/docs`

### 2. Frontend

```bash
cd frontend

# Instalar dependencias
pip install -r requirements.txt

# Inicializar Reflex (solo la primera vez)
reflex init

# Arrancar en desarrollo
reflex run
```

Frontend disponible en: `http://localhost:3000`

> ⚠️ Asegúrate de que el backend esté corriendo antes de usar el frontend.

---

## Despliegue en GCP (Cloud Run)

### Pre-requisitos
- `gcloud` CLI instalado y autenticado
- Proyecto GCP configurado
- Gemini API key guardada en Secret Manager

### Backend

```bash
cd backend

# Build y push a Artifact Registry
gcloud builds submit --tag gcr.io/TU_PROYECTO/cv-analyzer-backend

# Deploy en Cloud Run
gcloud run deploy cv-analyzer-backend \
  --image gcr.io/TU_PROYECTO/cv-analyzer-backend \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --memory 512Mi
```

Anota la URL del servicio desplegado (la necesitarás para el frontend).

### Frontend

1. Actualiza `API_URL` en `cv_analyzer_ui/cv_analyzer_ui.py` con la URL del backend de Cloud Run.

```python
API_URL = "https://cv-analyzer-backend-xxxx-ew.a.run.app/api/v1/analyze"
```

2. Despliega:

```bash
cd frontend

gcloud builds submit --tag gcr.io/TU_PROYECTO/cv-analyzer-frontend

gcloud run deploy cv-analyzer-frontend \
  --image gcr.io/TU_PROYECTO/cv-analyzer-frontend \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 3000
```

---

## Obtener la Gemini API Key

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crea una nueva API key
3. Guárdala en Secret Manager:

```bash
echo -n "tu_api_key" | gcloud secrets create gemini-api-key --data-file=-
```

---

## Estructura del proyecto

```
cv-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app + CORS
│   │   ├── router.py      # Endpoint /analyze
│   │   ├── analyzer.py    # LangChain + Gemini lógica
│   │   └── parser.py      # Extracción texto PDF
│   ├── Dockerfile
│   └── requirements.txt
│
└── frontend/
    ├── cv_analyzer_ui/
    │   └── cv_analyzer_ui.py  # App Reflex completa
    ├── rxconfig.py
    ├── Dockerfile
    └── requirements.txt
```

---

Desarrollado por [Aitor Fariña](https://afarina.dev) · Proyecto portfolio open source
