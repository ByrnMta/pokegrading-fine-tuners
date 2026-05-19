from fastapi import APIRouter, Depends, HTTPException, Form, Request
from sqlalchemy.orm import Session
from Base_de_Datos.db_session import get_db
from Servicios.Usuario_Servicio import UsuarioServicio
import os
import socket

router = APIRouter(prefix="/usuario", tags=["usuarios"])

# ----------------------------------------------------------------------
# Endpoint: registro nuevo usuario
# ----------------------------------------------------------------------
@router.post("/registro")
def registrar_usuario(
        nombre_usuario: str = Form(...),
        correo: str = Form(...),
        contrasena: str = Form(...),
        db: Session = Depends(get_db)
    ):

    # Se llama al servicio de registro de usuario nuevo
    resultado = UsuarioServicio.registrar_usuario_servicio(
        db=db, 
        nombre_usuario=nombre_usuario, 
        correo=correo, 
        contrasena=contrasena
    )
    if 'errores' in resultado:
        raise HTTPException(status_code=400, detail=resultado['errores'])
    return resultado
