from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from Modelos.Rol import Rol
from Modelos.Usuario import Usuario

# Importación de routers
from Controladores.Usuario_Controlador import router as usuario_router
from Routers import CatalogoRouter


# Dependencia para obtener la sesión de base de datos
from Base_de_Datos.db_session import get_db

# Inicialización de FastAPI
app = FastAPI(title="IntelliHome API", description="API para autenticación y gestión de propiedades")


@app.get("/")
def read_root():
    return {"message": "¡API funcionando correctamente!"}

# --- REGISTRO DE ROUTERS ---
app.include_router(usuario_router)
app.include_router(CatalogoRouter.router)
