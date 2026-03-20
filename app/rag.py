from dotenv import load_dotenv
load_dotenv()

import re
import json
import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ─────────────────────────────────────────────
#  LLM / RETRIEVER
# ─────────────────────────────────────────────
def get_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY")
    )

def get_retriever():
    return Chroma(
        persist_directory="vector_db",
        embedding_function=OpenAIEmbeddings()
    ).as_retriever(search_kwargs={"k": 3})


# ─────────────────────────────────────────────
#  DETERMINAR TÉCNICA (se llama después de Q11)
# ─────────────────────────────────────────────
PROMPT_DETERMINAR_TECNICA = """Eres un coach emocional especializado en adolescentes.
Analiza la siguiente conversación de evaluación y determina qué técnica de coaching es la más adecuada.

Opciones de técnica (elige EXACTAMENTE una):
- "GROW"        → cuando el problema principal es falta de metas, dirección o enfoque en el futuro
- "RESPIRACION" → cuando el problema principal es ansiedad, estrés alto, sobrepensamiento o tensión emocional
- "AUTOESTIMA"  → cuando el problema principal es baja autoestima, inseguridad o falta de reconocimiento propio
- "MOTIVACION"  → cuando el problema principal es falta de motivación, procrastinación o dificultad para actuar

Responde ÚNICAMENTE con un objeto JSON válido, sin texto extra, así:
{"tecnica": "GROW", "confianza": "alta"}
"""

def determinar_tecnica(historial: list) -> tuple[str, str]:
    """
    Analiza el historial de Q1-Q11 y devuelve (tecnica, mensaje_intro).
    tecnica es uno de: GROW, RESPIRACION, AUTOESTIMA, MOTIVACION
    """
    llm = get_llm()

    # Construir resumen de la conversación
    lineas = []
    for m in historial:
        rol = "Usuario" if m["rol"] == "usuario" else "Coach"
        # Usar solo texto plano (el historial puede contener HTML)
        contenido = re.sub(r"<[^>]+>", "", m["contenido"]).strip()
        if contenido:
            lineas.append(f"{rol}: {contenido}")

    resumen = "\n".join(lineas)

    mensajes = [
        SystemMessage(content=PROMPT_DETERMINAR_TECNICA),
        HumanMessage(content=f"Conversación:\n\n{resumen}\n\nDetermina la técnica adecuada."),
    ]

    try:
        respuesta = llm.invoke(mensajes)
        content = respuesta.content.strip()
        match = re.search(r"\{.*?\}", content, re.DOTALL)
        if match:
            data = json.loads(match.group())
            tecnica = data.get("tecnica", "GROW").upper()
            if tecnica not in ("GROW", "RESPIRACION", "AUTOESTIMA", "MOTIVACION"):
                tecnica = "GROW"
            return tecnica, ""
    except Exception as e:
        print(f"Error determinando técnica: {e}")

    # Fallback por palabra clave en Q7 (área de dificultad)
    texto_completo = resumen.lower()
    if any(w in texto_completo for w in ["autoestima", "insegur", "dudar"]):
        return "AUTOESTIMA", ""
    if any(w in texto_completo for w in ["motivaci", "evitand", "procrastin"]):
        return "MOTIVACION", ""
    if any(w in texto_completo for w in ["ansied", "estres", "sobrepens", "angust"]):
        return "RESPIRACION", ""
    return "GROW", ""


# ─────────────────────────────────────────────
#  RAG (mantenido para uso futuro)
# ─────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "META": (
        "Eres un coach emocional para adolescentes.\n"
        "Tu rol es ayudar al usuario a DEFINIR UNA META clara.\n"
        "No des consejos ni soluciones directas.\n"
        "Haz UNA sola pregunta abierta y reflexiva.\n"
        "Lenguaje empático, sencillo y motivador."
    ),
    "REALIDAD": (
        "Eres un coach emocional.\n"
        "Ayuda al usuario a explorar su REALIDAD ACTUAL.\n"
        "No juzgues ni soluciones.\n"
        "Haz preguntas que ayuden a reflexionar sobre lo que está pasando ahora."
    ),
    "OPCIONES": (
        "Eres un coach emocional.\n"
        "Ayuda al usuario a generar OPCIONES.\n"
        "No elijas por él.\n"
        "Haz preguntas que fomenten alternativas y posibilidades."
    ),
    "VOLUNTAD": (
        "Eres un coach emocional.\n"
        "Ayuda al usuario a comprometerse con una ACCIÓN concreta.\n"
        "La acción debe ser pequeña, realista y clara."
    ),
    "REFLEXION": (
        "Eres un coach emocional.\n"
        "Ayuda al usuario a reflexionar sobre lo aprendido.\n"
        "Valida emociones sin juzgar."
    ),
}

def consultar_rag(historial, fase):
    llm = get_llm()
    retriever = get_retriever()

    pregunta_usuario = historial[-1]["contenido"]
    docs = retriever.invoke(pregunta_usuario)
    contexto = "\n\n".join([d.page_content for d in docs])

    prompt_sistema = SYSTEM_PROMPTS.get(fase, SYSTEM_PROMPTS["META"])
    system_content = (
        prompt_sistema
        + "\n\nUsa el siguiente CONTEXTO solo como apoyo, "
        "sin dar sermones ni consejos directos:\n\n"
        + contexto
    )

    mensajes = [SystemMessage(content=system_content)]
    for m in historial:
        if m["rol"] == "usuario":
            mensajes.append(HumanMessage(content=m["contenido"]))
        else:
            mensajes.append(AIMessage(content=m["contenido"]))

    respuesta = llm.invoke(mensajes)
    return respuesta.content
