from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from Base_de_Datos.db import Base, engine
from Modelos.Rol import Rol
from Modelos.Usuario import Usuario
from Modelos.Cartas import Carta
from Modelos.EvaluacionCarta import EvaluacionCarta
from Modelos.AuditoriaCarta import AuditoriaCarta

# Importación de routers
from Controladores.Usuario_Controlador import router as usuario_router
from Controladores.Catalogo_Controlador import router as admin_router
from Controladores.Buscar_Carta_Controlador import router as submitter_router
from Controladores.EvaluacionCarta_Controlador import router as evaluacion_carta_router

# Dependencia para obtener la sesión de base de datos
from Datos.db_session import get_db

# Inicialización de FastAPI
app = FastAPI(title="Pokegrading", description="API para autenticación y gestión de propiedades")
# Configuración de CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables() -> None:
    """Ensure the local SQLite schema exists before serving requests."""
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "¡API funcionando correctamente!"}

# --- REGISTRO DE ROUTERS ---
app.include_router(usuario_router)
app.include_router(evaluacion_carta_router)
app.include_router(submitter_router)
app.include_router(admin_router)
