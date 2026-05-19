from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from Modelos import db

# Dependencia para obtener la sesión de base de datos
from Base_de_Datos.db_session import get_db

# Inicialización de FastAPI
app = FastAPI(title="IntelliHome API", description="API para autenticación y gestión de propiedades")


@app.get("/")
def read_root():
    return {"message": "¡API funcionando correctamente!"}

# --- REGISTRO DE ROUTERS ---
from Routers import CatalogoRouter
app.include_router(CatalogoRouter.router)