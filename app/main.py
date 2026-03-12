from dotenv import load_dotenv
load_dotenv() #Permite cargar las variables de entorno, que se encuentra en el archivo .env

import os #Permite importar utilidades del Sistema
import markdown
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Form, Request #Permite crear la aplicacion web, Permite recibir datos enviados desde un formulario HTML, Permite representar la peticion del navegador
from fastapi.responses import HTMLResponse, JSONResponse #Permite indicar que las respuesta de las peticiones sean en HTML
from fastapi.templating import Jinja2Templates #Permite hacer uso de plantillas HTML para la parte visual
from starlette.middleware.sessions import SessionMiddleware #Permite guardar la informacion del usuario entre las peticiones

from app.rag import consultar_rag #Permite obtener la logica de OPENIA
from app.coaching import siguiente_fase
from app.vectorstore import crear_vectorstore

app = FastAPI() #Creamos la aplicacion FastAPI
app.mount("/static", StaticFiles(directory="static"), name="static")

#Permite activar sesiones para los usuarios con cookies
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")
)

#Permite establecer en donde estan mis archivos de vista HTML
templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "..", "chroma")

@app.on_event("startup")
def startup_event():
    if not os.path.exists(CHROMA_DIR):
        print("🔧 Creando vectorstore...")
        crear_vectorstore()
    else:
        print("✅ Vectorstore ya existe")

# ---------- INICIALIZAR SESIÓN ----------
def inicializar_sesion(request: Request):
    if "fase" not in request.session:
        request.session["fase"] = "META"

    if "historial" not in request.session:
        request.session["historial"] = [{
            "rol": "asistente",
            "contenido": "👋 Bienvenido. Para comenzar, ¿qué meta personal o académica te gustaría trabajar hoy?"
        }]

    if "progreso" not in request.session or not isinstance(request.session["progreso"], dict):
        request.session["progreso"] = {
            "meta": False,
            "accion": False,
            "reflexion": False
        }

# INICIO
@app.get("/", response_class=HTMLResponse)
def index(request: Request):

    if "historial" not in request.session:
        print("no esta")
        request.session["fase"] = "META"
        
        contenido_md = (
            "**Bienvenido a tu coaching emocional**\n\n"
            "¿Qué situación de coaching te gustaría trabajar hoy?\n\n"
            "\t\t• Arte\n\n"
            "\t\t• Karate\n\n"
            "\t\t• Robotica\n\n"
            "\t\t• Programacion\n\n"
            "\t\t• Manualidades\n\n"
            "\t\t• Psicologia\n\n"
            "\t\t• Cocinar\n\n"
            "\t\t• Escribir poemas\n\n"
            "\t\t• Visitar zonas rurales\n\n"
            "\t\t• Anime\n\n"
            "\t\t• Manga\n\n"
            "\t\t• La cultura Japonesa y de Guatemala\n\n"
        )

        contenido_html = markdown.markdown(contenido_md)

        request.session["historial"] = [{
            "rol": "asistente",
            "contenido": contenido_html
        }]
        request.session["progreso"] = {
            "meta": False,
            "accion": False,
            "reflexion": False
        }
        
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "historial": request.session["historial"],
            "progreso": request.session["progreso"]
        }
    )


@app.post("/chat")
def chat(request: Request, pregunta: str = Form(...)):
    fase = request.session.get("fase", "META")
    historial = request.session.get("historial", [])
    progreso = request.session.get("progreso", {
        "meta": False,
        "accion": False,
        "reflexion": False
    })

    historial.append({
        "rol": "usuario",
        "contenido": pregunta
    })

    if fase == "META" and not progreso["meta"]:
        progreso["meta"] = True
        request.session["fase"] = "VOLUNTAD"

    elif fase == "VOLUNTAD" and not progreso["accion"]:
        progreso["accion"] = True
        request.session["fase"] = "REFLEXION"

    elif fase == "REFLEXION":
        progreso["reflexion"] = True

    respuesta = consultar_rag(historial, fase)

    respuesta_html = markdown.markdown(respuesta)

    historial.append({
        "rol": "asistente",
        "contenido": respuesta_html
    })

    request.session["historial"] = historial
    request.session["progreso"] = progreso

    return JSONResponse({
        "respuesta": respuesta_html,
        "progreso": progreso
    })