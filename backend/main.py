from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from Modelos.Rol import Rol
from Modelos.Usuario import Usuario
from Modelos.Cartas import Carta

# Importación de routers
from Controladores.Usuario_Controlador import router as usuario_router
from Controladores.Catalogo_Controlador import router as catalogo_router

# Dependencia para obtener la sesión de base de datos
from Base_de_Datos.db_session import get_db

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
@app.get("/")
def read_root():
    return {"message": "¡API funcionando correctamente!"}

# --- REGISTRO DE ROUTERS ---
app.include_router(usuario_router)
app.include_router(catalogo_router)
