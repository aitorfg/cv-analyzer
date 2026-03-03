import reflex as rx

config = rx.Config(
    app_name="cv_analyzer_ui",
    frontend_port=8080,
    backend_port=8080,
    api_url="https://cv-analyzer-869270551654.europe-west1.run.app/api/v1/analyze"
)
