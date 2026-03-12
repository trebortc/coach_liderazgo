from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os

# Prompt base del COACH
SYSTEM_PROMPTS = {
    "META": (
        "Eres un coach emocional para adolescentes.\n"
        "Tu rol es ayudar al usuario a DEFINIR UNA META clara.\n"
        "No des consejos ni soluciones.\n"
        "Haz UNA sola pregunta abierta y reflexiva.\n"
        "Lenguaje empático, sencillo y motivador.\n"
        "Ejemplo: ¿Qué te gustaría lograr con esta situación?"
    ),

    "REALIDAD": (
        "Eres un coach emocional.\n"
        "Ayuda al usuario a explorar su REALIDAD ACTUAL.\n"
        "No juzgues ni soluciones.\n"
        "Haz preguntas que ayuden a reflexionar sobre lo que está pasando ahora.\n"
        "Ejemplo: ¿Qué está ocurriendo actualmente en esta situación?"
    ),

    "OPCIONES": (
        "Eres un coach emocional.\n"
        "Ayuda al usuario a generar OPCIONES.\n"
        "No elijas por él.\n"
        "Haz preguntas que fomenten alternativas y posibilidades.\n"
        "Ejemplo: ¿Qué diferentes caminos podrías intentar?"
    ),

    "VOLUNTAD": (
        "Eres un coach emocional.\n"
        "Ayuda al usuario a comprometerse con una ACCIÓN concreta.\n"
        "La acción debe ser pequeña, realista y clara.\n"
        "Ejemplo: ¿Qué paso específico te comprometes a dar?"
    ),

    "REFLEXION": (
        "Eres un coach emocional.\n"
        "Ayuda al usuario a reflexionar sobre lo aprendido.\n"
        "Valida emociones sin juzgar.\n"
        "Ejemplo: ¿Qué aprendiste de este proceso?"
    )
}

def get_llm():
    #Creamos el tipo de modelo que vamos a utilizar
    # 0.0	Muy exacto y técnico
    # 0.2	Profesional y consistente
    # 0.7	Creativo
    # 1.0	Muy libre
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")  # explícito y seguro
    )

def consultar_rag(historial, fase):
    llm = get_llm()
    retriever = get_retriever()

    # Último mensaje del usuario
    pregunta_usuario = historial[-1]["contenido"]

    # 🔍 Buscar contexto en documentos
    docs = retriever.invoke(pregunta_usuario)
    contexto = "\n\n".join([d.page_content for d in docs])

    mensajes = []

    # 🎯 Prompt del coach + contexto documental
    prompt_sistema = SYSTEM_PROMPTS.get(fase, SYSTEM_PROMPTS["META"])

    system_content = (
        prompt_sistema +
        "\n\nUsa el siguiente CONTEXTO solo como apoyo, "
        "sin dar sermones ni consejos directos:\n\n" +
        contexto
    )

    mensajes.append(SystemMessage(content=system_content))

    # Historial
    for m in historial:
        if m["rol"] == "usuario":
            mensajes.append(HumanMessage(content=m["contenido"]))
        else:
            mensajes.append(AIMessage(content=m["contenido"]))

    respuesta = llm.invoke(mensajes)
    return respuesta.content

def get_retriever():
    return Chroma(
        persist_directory="vector_db",
        embedding_function=OpenAIEmbeddings()
    ).as_retriever(search_kwargs={"k": 3})
