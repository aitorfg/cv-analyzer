import reflex as rx
import httpx
import base64
from typing import Optional

# ── Config ──────────────────────────────────────────────────────────────────
API_URL = "http://localhost:8080/api/v1/analyze"  # Change to Cloud Run URL in production


# ── State ────────────────────────────────────────────────────────────────────
class State(rx.State):
    job_offer: str = ""
    is_loading: bool = False
    error_message: str = ""

    # Results
    match_score: int = 0
    strengths: list[str] = []
    gaps: list[str] = []
    recommendations: str = ""
    summary: str = ""
    seniority_match: str = ""
    has_result: bool = False

    # File
    cv_filename: str = ""
    cv_bytes: str = ""  # base64 encoded

    def handle_upload(self, files: list[rx.UploadFile]):
        pass  # handled via on_upload

    async def process_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        file = files[0]
        upload_data = await file.read()
        self.cv_filename = file.filename
        self.cv_bytes = base64.b64encode(upload_data).decode("utf-8")
        self.error_message = ""

    async def analyze(self):
        if not self.cv_bytes:
            self.error_message = "Por favor, sube tu CV en formato PDF."
            return
        if not self.job_offer.strip():
            self.error_message = "Por favor, escribe la descripción de la oferta."
            return

        self.is_loading = True
        self.has_result = False
        self.error_message = ""

        try:
            pdf_bytes = base64.b64decode(self.cv_bytes)
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    API_URL,
                    files={"cv_file": (self.cv_filename, pdf_bytes, "application/pdf")},
                    data={"job_offer": self.job_offer},
                )

            if response.status_code == 200:
                data = response.json()
                self.match_score = data.get("match_score", 0)
                self.strengths = data.get("strengths", [])
                self.gaps = data.get("gaps", [])
                self.recommendations = data.get("recommendations", "")
                self.summary = data.get("summary", "")
                self.seniority_match = data.get("seniority_match", "")
                self.has_result = True
            else:
                detail = response.json().get("detail", "Error desconocido")
                self.error_message = f"Error del servidor: {detail}"

        except httpx.ConnectError:
            self.error_message = "No se pudo conectar con el servidor. Verifica que el backend esté corriendo."
        except Exception as e:
            self.error_message = f"Error inesperado: {str(e)}"
        finally:
            self.is_loading = False

    def reset_form(self):
        self.cv_filename = ""
        self.cv_bytes = ""
        self.job_offer = ""
        self.has_result = False
        self.error_message = ""
        self.match_score = 0
        self.strengths = []
        self.gaps = []
        self.recommendations = ""
        self.summary = ""
        self.seniority_match = ""


# ── Design tokens ────────────────────────────────────────────────────────────
BG = "#0a0a0f"
SURFACE = "#13131a"
SURFACE2 = "#1a1a24"
BORDER = "#2a2a3a"
ACCENT = "#6ee7b7"       # mint green
ACCENT2 = "#818cf8"      # soft indigo
TEXT = "#e2e8f0"
TEXT_MUTED = "#64748b"
DANGER = "#f87171"
WARNING = "#fbbf24"


def score_color(score: int) -> str:
    if score >= 75:
        return ACCENT
    elif score >= 50:
        return WARNING
    else:
        return DANGER


# ── Components ───────────────────────────────────────────────────────────────

def nav() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.text("A", color=ACCENT, font_size="1rem", font_weight="800"),
                    width="32px", height="32px",
                    border_radius="8px",
                    bg=f"rgba(110,231,183,0.1)",
                    border=f"1px solid {ACCENT}",
                    display="flex", align_items="center", justify_content="center",
                ),
                rx.text(
                    "CV Analyzer",
                    color=TEXT,
                    font_size="1rem",
                    font_weight="600",
                    font_family="'JetBrains Mono', monospace",
                    letter_spacing="-0.02em",
                ),
                spacing="3",
                align="center",
            ),
            rx.spacer(),
            rx.link(
                rx.text("afarina.dev", color=TEXT_MUTED, font_size="0.8rem",
                        font_family="'JetBrains Mono', monospace",
                        _hover={"color": ACCENT}, transition="color 0.2s"),
                href="https://afarina.dev",
                is_external=True,
            ),
            align="center",
        ),
        width="100%",
        max_width="900px",
        margin="0 auto",
        padding="1.25rem 1.5rem",
    )


def upload_zone() -> rx.Component:
    return rx.upload(
        rx.box(
            rx.cond(
                State.cv_filename != "",
                rx.vstack(
                    rx.box(
                        rx.text("✓", color=ACCENT, font_size="1.5rem"),
                        width="48px", height="48px",
                        border_radius="12px",
                        bg=f"rgba(110,231,183,0.1)",
                        border=f"1px solid {ACCENT}",
                        display="flex", align_items="center", justify_content="center",
                    ),
                    rx.text(State.cv_filename, color=ACCENT, font_size="0.9rem",
                            font_family="'JetBrains Mono', monospace",
                            font_weight="500"),
                    rx.text("Haz clic para cambiar el archivo", color=TEXT_MUTED,
                            font_size="0.75rem"),
                    spacing="2", align="center",
                ),
                rx.vstack(
                    rx.box(
                        rx.text("PDF", color=TEXT_MUTED, font_size="0.75rem",
                                font_family="'JetBrains Mono', monospace",
                                font_weight="700", letter_spacing="0.1em"),
                        width="48px", height="48px",
                        border_radius="12px",
                        bg=SURFACE2,
                        border=f"1px solid {BORDER}",
                        display="flex", align_items="center", justify_content="center",
                    ),
                    rx.text("Arrastra tu CV aquí", color=TEXT,
                            font_size="0.95rem", font_weight="500"),
                    rx.text("o haz clic para seleccionar · Solo PDF",
                            color=TEXT_MUTED, font_size="0.75rem"),
                    spacing="2", align="center",
                ),
            ),
            width="100%",
            padding="2rem",
            border=f"1.5px dashed {BORDER}",
            border_radius="12px",
            bg=SURFACE,
            display="flex",
            align_items="center",
            justify_content="center",
            cursor="pointer",
            _hover={
                "border_color": ACCENT,
                "bg": f"rgba(110,231,183,0.03)",
            },
            transition="all 0.2s ease",
            min_height="140px",
        ),
        id="cv_upload",
        accept={"application/pdf": [".pdf"]},
        max_files=1,
        on_drop=State.process_upload,
        width="100%",
    )


def tag(label: str, color: str, bg: str) -> rx.Component:
    return rx.box(
        rx.text(label, color=color, font_size="0.7rem",
                font_family="'JetBrains Mono', monospace",
                font_weight="600", letter_spacing="0.08em"),
        padding="0.2rem 0.6rem",
        border_radius="6px",
        bg=bg,
        border=f"1px solid {color}",
        display="inline-flex",
        align_items="center",
    )


def score_ring() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                State.match_score.to_string() + "%",
                font_size="3rem",
                font_weight="800",
                font_family="'JetBrains Mono', monospace",
                color=ACCENT,
                letter_spacing="-0.04em",
            ),
            rx.text("compatibilidad", color=TEXT_MUTED,
                    font_size="0.75rem", letter_spacing="0.08em",
                    font_family="'JetBrains Mono', monospace"),
            spacing="0",
            align="center",
        ),
        width="160px",
        height="160px",
        border_radius="50%",
        border=f"3px solid {ACCENT}",
        bg=f"rgba(110,231,183,0.05)",
        display="flex",
        align_items="center",
        justify_content="center",
        box_shadow=f"0 0 40px rgba(110,231,183,0.15)",
    )


def seniority_badge() -> rx.Component:
    return rx.cond(
        State.seniority_match == "match",
        tag("Seniority ✓ match", ACCENT, f"rgba(110,231,183,0.08)"),
        rx.cond(
            State.seniority_match == "above",
            tag("Seniority ↑ por encima", ACCENT2, f"rgba(129,140,248,0.08)"),
            tag("Seniority ↓ por debajo", WARNING, f"rgba(251,191,36,0.08)"),
        )
    )


def strength_item(item: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="6px", height="6px",
            border_radius="50%",
            bg=ACCENT,
            flex_shrink="0",
            margin_top="0.4rem",
        ),
        rx.text(item, color=TEXT, font_size="0.875rem", line_height="1.6"),
        spacing="3",
        align="start",
        width="100%",
    )


def gap_item(item: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="6px", height="6px",
            border_radius="50%",
            bg=DANGER,
            flex_shrink="0",
            margin_top="0.4rem",
        ),
        rx.text(item, color=TEXT, font_size="0.875rem", line_height="1.6"),
        spacing="3",
        align="start",
        width="100%",
    )


def result_card(title: str, accent_color: str, content: rx.Component) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(width="3px", height="18px", bg=accent_color, border_radius="2px"),
                rx.text(title, color=TEXT, font_size="0.8rem",
                        font_weight="700", letter_spacing="0.06em",
                        font_family="'JetBrains Mono', monospace",
                        text_transform="uppercase"),
                spacing="3", align="center",
            ),
            content,
            spacing="4",
            align="start",
            width="100%",
        ),
        padding="1.5rem",
        bg=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius="12px",
        width="100%",
    )


def results_section() -> rx.Component:
    return rx.cond(
        State.has_result,
        rx.vstack(
            # Score + seniority
            rx.box(
                rx.vstack(
                    rx.hstack(
                        score_ring(),
                        rx.vstack(
                            rx.text("Análisis completado",
                                    color=TEXT_MUTED,
                                    font_size="0.75rem",
                                    font_family="'JetBrains Mono', monospace",
                                    letter_spacing="0.08em",
                                    text_transform="uppercase"),
                            seniority_badge(),
                            rx.text(State.summary,
                                    color=TEXT,
                                    font_size="0.875rem",
                                    line_height="1.7",
                                    max_width="500px"),
                            spacing="3",
                            align="start",
                        ),
                        spacing="8",
                        align="start",
                        wrap="wrap",
                    ),
                    spacing="4",
                    align="start",
                    width="100%",
                ),
                padding="2rem",
                bg=SURFACE,
                border=f"1px solid {BORDER}",
                border_radius="12px",
                width="100%",
            ),
            # Strengths + Gaps grid
            rx.grid(
                result_card(
                    "Fortalezas",
                    ACCENT,
                    rx.vstack(
                        rx.foreach(State.strengths, strength_item),
                        spacing="2",
                        width="100%",
                    ),
                ),
                result_card(
                    "Gaps",
                    DANGER,
                    rx.vstack(
                        rx.foreach(State.gaps, gap_item),
                        spacing="2",
                        width="100%",
                    ),
                ),
                columns="2",
                spacing="4",
                width="100%",
            ),
            # Recommendations
            result_card(
                "Recomendaciones",
                ACCENT2,
                rx.text(State.recommendations, color=TEXT,
                        font_size="0.875rem", line_height="1.7"),
            ),
            # Reset button
            rx.button(
                "Nuevo análisis",
                on_click=State.reset_form,
                variant="ghost",
                color=TEXT_MUTED,
                font_family="'JetBrains Mono', monospace",
                font_size="0.8rem",
                cursor="pointer",
                _hover={"color": TEXT},
            ),
            spacing="4",
            width="100%",
            align="start",
        ),
        rx.box(),
    )


def input_section() -> rx.Component:
    return rx.cond(
        ~State.has_result,
        rx.vstack(
            # Upload
            rx.vstack(
                rx.text("01 — Tu CV",
                        color=TEXT_MUTED,
                        font_size="0.7rem",
                        font_family="'JetBrains Mono', monospace",
                        letter_spacing="0.1em",
                        text_transform="uppercase"),
                upload_zone(),
                spacing="2",
                width="100%",
                align="start",
            ),
            # Job offer
            rx.vstack(
                rx.text("02 — Descripción de la oferta",
                        color=TEXT_MUTED,
                        font_size="0.7rem",
                        font_family="'JetBrains Mono', monospace",
                        letter_spacing="0.1em",
                        text_transform="uppercase"),
                rx.text_area(
                    placeholder="Pega aquí la descripción completa de la oferta de trabajo...",
                    value=State.job_offer,
                    on_change=State.set_job_offer,
                    min_height="180px",
                    width="100%",
                    bg=SURFACE,
                    border=f"1px solid {BORDER}",
                    border_radius="12px",
                    color=TEXT,
                    font_size="0.875rem",
                    padding="1rem",
                    _placeholder={"color": TEXT_MUTED},
                    _focus={
                        "border_color": ACCENT,
                        "box_shadow": f"0 0 0 2px rgba(110,231,183,0.1)",
                        "outline": "none",
                    },
                    resize="vertical",
                ),
                spacing="2",
                width="100%",
                align="start",
            ),
            # Error
            rx.cond(
                State.error_message != "",
                rx.box(
                    rx.text(State.error_message, color=DANGER, font_size="0.8rem"),
                    padding="0.75rem 1rem",
                    bg=f"rgba(248,113,113,0.08)",
                    border=f"1px solid rgba(248,113,113,0.3)",
                    border_radius="8px",
                    width="100%",
                ),
                rx.box(),
            ),
            # Submit
            rx.button(
                rx.cond(
                    State.is_loading,
                    rx.hstack(
                        rx.spinner(size="2", color=BG),
                        rx.text("Analizando...", color=BG),
                        spacing="2",
                    ),
                    rx.text("Analizar compatibilidad →", color=BG),
                ),
                on_click=State.analyze,
                bg=ACCENT,
                color=BG,
                font_weight="700",
                font_family="'JetBrains Mono', monospace",
                font_size="0.875rem",
                padding="0.75rem 2rem",
                border_radius="10px",
                cursor="pointer",
                disabled=State.is_loading,
                _hover={"bg": "#a7f3d0", "transform": "translateY(-1px)"},
                _disabled={"opacity": "0.5", "cursor": "not-allowed"},
                transition="all 0.15s ease",
                align_self="flex-start",
            ),
            spacing="6",
            width="100%",
            align="start",
        ),
        rx.box(),
    )


def hero() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            tag("Powered by Gemini + LangChain", ACCENT2, f"rgba(129,140,248,0.08)"),
            tag("GCP · Cloud Run", TEXT_MUTED, f"rgba(100,116,139,0.08)"),
            spacing="2",
            wrap="wrap",
        ),
        rx.heading(
            "Analiza tu CV contra cualquier oferta",
            size="7",
            color=TEXT,
            font_family="'JetBrains Mono', monospace",
            font_weight="800",
            letter_spacing="-0.03em",
            line_height="1.2",
        ),
        rx.text(
            "Sube tu CV en PDF, pega la oferta de trabajo y obtén un análisis detallado "
            "de compatibilidad con fortalezas, gaps y recomendaciones concretas.",
            color=TEXT_MUTED,
            font_size="0.95rem",
            line_height="1.7",
            max_width="600px",
        ),
        spacing="4",
        align="start",
        width="100%",
    )


def index() -> rx.Component:
    return rx.box(
        # Google Font import
        rx.html(
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
        ),
        rx.vstack(
            nav(),
            rx.box(
                rx.vstack(
                    hero(),
                    rx.box(
                        width="100%",
                        height="1px",
                        bg=BORDER,
                        margin="0.5rem 0",
                    ),
                    input_section(),
                    results_section(),
                    spacing="8",
                    align="start",
                    width="100%",
                ),
                width="100%",
                max_width="900px",
                margin="0 auto",
                padding="2rem 1.5rem 4rem",
            ),
            spacing="0",
            min_height="100vh",
        ),
        bg=BG,
        min_height="100vh",
        font_family="'JetBrains Mono', monospace",
    )


# ── App ──────────────────────────────────────────────────────────────────────
app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&display=swap"
    ],
    style={
        "background_color": BG,
        "*": {"box_sizing": "border-box"},
    },
)
app.add_page(index, route="/", title="CV Analyzer | afarina.dev")
