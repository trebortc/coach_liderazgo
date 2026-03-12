from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "documents")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma")


def crear_vectorstore():
    documentos = []

    for archivo in os.listdir(DATA_DIR):
        ruta = os.path.join(DATA_DIR, archivo)

        if archivo.lower().endswith(".pdf"):
            loader = PyMuPDFLoader(ruta)
            documentos.extend(loader.load())

        elif archivo.lower().endswith(".txt"):
            loader = TextLoader(ruta, encoding="utf-8")
            documentos.extend(loader.load())

    if not documentos:
        print("⚠️ No se encontraron documentos")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documentos)

    embeddings = OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    print(f"Vectorstore creado con {len(chunks)} fragmentos")
