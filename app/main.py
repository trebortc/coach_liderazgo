from dotenv import load_dotenv
load_dotenv()

import os
import random
import markdown
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.rag import determinar_tecnica
from app.vectorstore import crear_vectorstore

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")
)

templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "..", "chroma")

@app.on_event("startup")
def startup_event():
    if not os.path.exists(CHROMA_DIR):
        print("Creando vectorstore...")
        crear_vectorstore()
    else:
        print("Vectorstore ya existe")

# ─────────────────────────────────────────────
#  PREGUNTAS PRINCIPALES (Q1 – Q11)
# ─────────────────────────────────────────────
PREGUNTAS = {
    "Q1":  "¿Cómo te sientes hoy?",
    "Q2":  "Si tuvieras que elegir una palabra para describir tu día, ¿cuál sería?",
    "Q3":  (
        "¿Tu emoción principal ahora es más bien:\n\n"
        "😊 positiva\n\n"
        "😐 neutra\n\n"
        "😟 difícil"
    ),
    "Q4":  "¿Qué está pasando en tu vida que te hace sentir así?",
    "Q5":  "En una escala del 1 al 10, ¿qué tan fuerte es ese sentimiento?",
    "Q6":  "¿Es algo que apareció hoy o llevas varios días sintiéndolo?",
    "Q7":  (
        "¿En qué área sientes más dificultad ahora?\n\n"
        "📚 estudios\n\n"
        "👥 amigos\n\n"
        "🏠 familia\n\n"
        "💭 autoestima\n\n"
        "⚡ motivación\n\n"
        "🎯 futuro o metas"
    ),
    "Q8":  "¿Qué pensamiento se repite más en tu mente últimamente?",
    "Q9":  "¿Hay algo que te preocupe o te haga dudar de ti mismo?",
    "Q10": "¿Qué te gustaría que cambiara en esta situación?",
    "Q11": "Si pudieras mejorar una cosa hoy, ¿cuál sería?",
}

SECUENCIA_PRINCIPAL = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Q10","Q11"]

# ─────────────────────────────────────────────
#  TÉCNICAS DE COACHING
# ─────────────────────────────────────────────
INTRO_TECNICAS = {
    "GROW": (
        "Acá te recomiendo aplicar la siguiente técnica que te ayudará "
        "a visualizar tu meta: **Técnica GROW**\n\n"
        "Contesta las siguientes preguntas:"
    ),
    "RESPIRACION": (
        "Acá te recomiendo aplicar la siguiente técnica que te ayudará "
        "a regular tu mente y pensamiento: **Técnica de respiración + escritura emocional**"
    ),
    "AUTOESTIMA": (
        "Acá te recomiendo aplicar la siguiente técnica que te ayudará "
        "a mejorar tu situación: **Técnica de fortalezas**"
    ),
    "MOTIVACION": (
        "Acá te recomiendo aplicar la siguiente técnica que te ayudará "
        "a mejorar tu situación: **Aplicar técnica de micro-acciones**"
    ),
}

PREGUNTAS_TECNICAS = {
    "GROW_Q1":  "¿Qué meta te gustaría lograr?",
    "GROW_Q2":  "¿Dónde estás ahora con respecto a esa meta?",
    "GROW_Q3":  "¿Qué opciones tienes para avanzar?",
    "GROW_Q4":  "¿Qué primer paso puedes dar hoy?",
    "GROW_Q5":  "¿Te gustaría hablar con alguien de confianza sobre esto?",

    "RESP_Q1":  "¿Te gustaría intentar un ejercicio corto para calmar tu mente?",
    "RESP_Q2":  "¿Qué pensamiento te preocupa más ahora? Escríbelo aquí.",
    "RESP_Q3":  "Ahora escribe una posible solución o una forma más amable de verlo.",

    "AUTO_Q1":  "¿Qué cosas haces bien aunque a veces no lo reconozcas?",
    "AUTO_Q2":  "¿Qué diría un amigo sobre tus cualidades?",
    "AUTO_Q3":  "¿Qué logro pequeño tuviste esta semana?",
    "AUTO_Q4":  "¿Te gustaría hablar con alguien de confianza sobre esto?",

    "MOTIV_Q1": "¿Qué tarea estás evitando?",
    "MOTIV_Q2": "¿Cuál sería la versión más pequeña de esa tarea?",
    "MOTIV_Q3": "¿Puedes hacerla en 5 o 10 minutos?",
    "MOTIV_Q4": "¿Te gustaría hablar con alguien de confianza sobre esto?",
}

EJERCICIOS_RESPIRACION = [
    (
        "**RESPIRACIÓN 4–4 (EQUILIBRIO RÁPIDO)**\n\n"
        "Te servirá para calmar ansiedad y centrar la mente.\n\n"
        "**Pasos:**\n\n"
        "- Inhala por la nariz durante 4 segundos.\n"
        "- Exhala por la boca durante 4 segundos.\n"
        "- Repite 6 a 10 veces.\n\n"
        "💡 *Respira lento. Imagina que inflas un globo al inhalar y lo desinflas al exhalar.*\n\n"
        "Duración aproximada: 1 minuto\n\n"
        "Cuando termines el ejercicio escribe: **Siguiente**"
    ),
    (
        "**RESPIRACIÓN 4–2–6 (RELAJACIÓN PROFUNDA)**\n\n"
        "Te ayuda a reducir tensión mental y física.\n\n"
        "**Pasos:**\n\n"
        "- Inhala por la nariz 4 segundos.\n"
        "- Mantén el aire 2 segundos.\n"
        "- Exhala lentamente por la boca 6 segundos.\n"
        "- Repetir 5–8 veces.\n\n"
        "💡 *La exhalación más larga ayuda a activar el sistema nervioso relajante.*\n\n"
        "Duración: 1–2 minutos\n\n"
        "Cuando termines el ejercicio escribe: **Siguiente**"
    ),
    (
        "**RESPIRACIÓN CUADRADA (BOX BREATHING)**\n\n"
        "Muy usada en psicología y entrenamiento mental para recuperar control emocional.\n\n"
        "**Pasos:**\n\n"
        "- Inhala 4 segundos\n"
        "- Mantén el aire 4 segundos\n"
        "- Exhala 4 segundos\n"
        "- Mantén sin aire 4 segundos\n"
        "- Repetir 5 ciclos.\n\n"
        "💡 *Imagina que dibujas un cuadrado con tu respiración.*\n\n"
        "Duración: 1–2 minutos\n\n"
        "Cuando termines el ejercicio escribe: **Siguiente**"
    ),
]

MENSAJE_FINAL = (
    "> Si te sientes muy abrumado, buscar ayuda es una buena opción<<.\n\n"
    "Gracias por compartir este momento conmigo. Me alegra haber podido "
    "acompañarte y escuchar cómo te sientes. Recuerda que siempre puedes "
    "volver cuando necesites reflexionar, ordenar tus ideas o simplemente "
    "hablar un poco.\n\n"
    "Estaré aquí cuando quieras continuar la conversación. 🌱"
)

# ─────────────────────────────────────────────
#  LÓGICA DE PROGRESO
# ─────────────────────────────────────────────
# Estado → (explorar, entender, identificar, dirigir)
PROGRESO_POR_ESTADO = {
    "Q1":  (True,  False, False, False),
    "Q2":  (True,  False, False, False),
    "Q3":  (True,  False, False, False),
    "Q4":  (True,  False, False, False),
    "Q5":  (True,  False, False, False),
    "Q6":  (True,  False, False, False),
    "Q7":  (True,  True,  False, False),
    "Q8":  (True,  True,  False, False),
    "Q9":  (True,  True,  False, False),
    "Q10": (True,  True,  True,  False),
    "Q11": (True,  True,  True,  False),
}

TECNICA_ESTADOS = {
    "GROW_Q1", "GROW_Q2", "GROW_Q3", "GROW_Q4", "GROW_Q5",
    "RESP_Q1", "RESP_EJERCICIO", "RESP_Q2", "RESP_Q3",
    "AUTO_Q1", "AUTO_Q2", "AUTO_Q3", "AUTO_Q4",
    "MOTIV_Q1", "MOTIV_Q2", "MOTIV_Q3", "MOTIV_Q4",
    "FINAL",
}

def calcular_progreso(estado: str) -> dict:
    if estado in TECNICA_ESTADOS:
        return {"explorar": True, "entender": True, "identificar": True, "dirigir": True}
    vals = PROGRESO_POR_ESTADO.get(estado, (False, False, False, False))
    return {
        "explorar":   vals[0],
        "entender":   vals[1],
        "identificar": vals[2],
        "dirigir":    vals[3],
    }

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def md(texto: str) -> str:
    return markdown.markdown(texto)

def inicializar_sesion(request: Request):
    if "estado" not in request.session:
        request.session["estado"] = "Q1"
    if "historial" not in request.session:
        request.session["historial"] = [{
            "rol": "asistente",
            "contenido": md(
                "👋 Hola, soy tu coach emocional. "
                "Estoy aquí para acompañarte y ayudarte a entender mejor cómo te sientes.\n\n"
                + PREGUNTAS["Q1"]
            )
        }]
    if "progreso" not in request.session:
        request.session["progreso"] = calcular_progreso("Q1")

# ─────────────────────────────────────────────
#  RUTAS
# ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    inicializar_sesion(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "historial": request.session["historial"],
        "progreso":  request.session["progreso"],
    })


@app.post("/chat")
def chat(request: Request, pregunta: str = Form(...)):
    estado   = request.session.get("estado", "Q1")
    historial = request.session.get("historial", [])
    pregunta  = pregunta.strip()

    # Agregar mensaje del usuario
    historial.append({"rol": "usuario", "contenido": pregunta})

    nuevo_estado, respuesta_md = procesar_estado(estado, pregunta, historial)

    respuesta_html = md(respuesta_md)
    historial.append({"rol": "asistente", "contenido": respuesta_html})

    request.session["estado"]   = nuevo_estado
    request.session["historial"] = historial
    progreso = calcular_progreso(nuevo_estado)
    request.session["progreso"] = progreso

    return JSONResponse({"respuesta": respuesta_html, "progreso": progreso})


# ─────────────────────────────────────────────
#  MÁQUINA DE ESTADOS
# ─────────────────────────────────────────────
def procesar_estado(estado: str, respuesta_usuario: str, historial: list) -> tuple[str, str]:
    """Devuelve (nuevo_estado, texto_respuesta_markdown)."""

    # ── Preguntas principales Q1–Q10 ─────────────────────────────────────
    if estado in ("Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Q10"):
        idx = SECUENCIA_PRINCIPAL.index(estado)
        siguiente = SECUENCIA_PRINCIPAL[idx + 1]
        return siguiente, PREGUNTAS[siguiente]

    # ── Q11: última pregunta principal → determinar técnica ───────────────
    if estado == "Q11":
        tecnica, msg_intro = determinar_tecnica(historial)
        primer_q_tecnica = _primer_estado_tecnica(tecnica)
        primera_pregunta = PREGUNTAS_TECNICAS[primer_q_tecnica]
        return primer_q_tecnica, (
            INTRO_TECNICAS[tecnica] + "\n\n" + primera_pregunta
        )

    # ── GROW ──────────────────────────────────────────────────────────────
    if estado == "GROW_Q1":
        return "GROW_Q2", PREGUNTAS_TECNICAS["GROW_Q2"]
    if estado == "GROW_Q2":
        return "GROW_Q3", PREGUNTAS_TECNICAS["GROW_Q3"]
    if estado == "GROW_Q3":
        return "GROW_Q4", PREGUNTAS_TECNICAS["GROW_Q4"]
    if estado == "GROW_Q4":
        return "FINAL", MENSAJE_FINAL
    if estado == "GROW_Q5":
        return "FINAL", MENSAJE_FINAL

    # ── RESPIRACIÓN ───────────────────────────────────────────────────────
    if estado == "RESP_Q1":
        lower = respuesta_usuario.lower()
        if any(w in lower for w in ["sí", "si", "yes", "claro", "quiero", "ok", "dale"]):
            ejercicio = random.choice(EJERCICIOS_RESPIRACION)
            return "RESP_EJERCICIO", ejercicio
        else:
            return "RESP_Q2", PREGUNTAS_TECNICAS["RESP_Q2"]

    if estado == "RESP_EJERCICIO":
        if "siguiente" in respuesta_usuario.lower():
            return "RESP_Q2", PREGUNTAS_TECNICAS["RESP_Q2"]
        else:
            return "RESP_EJERCICIO", (
                "Cuando termines el ejercicio, escribe **Siguiente** para continuar."
            )

    if estado == "RESP_Q2":
        return "RESP_Q3", PREGUNTAS_TECNICAS["RESP_Q3"]
    if estado == "RESP_Q3":
        return "FINAL", MENSAJE_FINAL

    # ── AUTOESTIMA ────────────────────────────────────────────────────────
    if estado == "AUTO_Q1":
        return "AUTO_Q2", PREGUNTAS_TECNICAS["AUTO_Q2"]
    if estado == "AUTO_Q2":
        return "AUTO_Q3", PREGUNTAS_TECNICAS["AUTO_Q3"]
    if estado == "AUTO_Q3":
        return "AUTO_Q4", PREGUNTAS_TECNICAS["AUTO_Q4"]
    if estado == "AUTO_Q4":
        return "FINAL", MENSAJE_FINAL

    # ── MOTIVACIÓN ────────────────────────────────────────────────────────
    if estado == "MOTIV_Q1":
        return "MOTIV_Q2", PREGUNTAS_TECNICAS["MOTIV_Q2"]
    if estado == "MOTIV_Q2":
        return "MOTIV_Q3", PREGUNTAS_TECNICAS["MOTIV_Q3"]
    if estado == "MOTIV_Q3":
        return "MOTIV_Q4", PREGUNTAS_TECNICAS["MOTIV_Q4"]
    if estado == "MOTIV_Q4":
        return "FINAL", MENSAJE_FINAL

    # ── FINAL ─────────────────────────────────────────────────────────────
    if estado == "FINAL":
        return "FINAL", (
            "La sesión ha concluido. Cuando quieras iniciar un nuevo proceso, recarga la página. 🌱"
        )

    # Fallback
    return "Q1", PREGUNTAS["Q1"]


def _primer_estado_tecnica(tecnica: str) -> str:
    mapa = {
        "GROW":       "GROW_Q1",
        "RESPIRACION": "RESP_Q1",
        "AUTOESTIMA":  "AUTO_Q1",
        "MOTIVACION":  "MOTIV_Q1",
    }
    return mapa.get(tecnica, "GROW_Q1")
