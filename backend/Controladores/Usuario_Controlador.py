from fastapi import APIRouter, Depends, HTTPException, Form, Request
from sqlalchemy.orm import Session
from Base_de_Datos.db_session import get_db
from Servicios.logica.Usuario_Servicio import UsuarioServicio
from modelos.Usuario import UsuarioCreate
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
        pais: str = Form(...),
        idioma: str = Form(...),
        db: Session = Depends(get_db)
    ):

    # Se crea un objeto de usuario con los datos recibidos del formulario
    nuevo_usuario = UsuarioCreate(
        nombre_usuario=nombre_usuario,
        correo=correo,
        contrasena=contrasena,
        pais=pais,
        idioma=idioma,
    )

    # Se llama al servicio de registro de usuario nuevo
    resultado = UsuarioServicio.registrar_usuario_servicio(
        db=db, 
        nombre_usuario=nombre_usuario, 
        correo=correo, 
        contrasena=contrasena
    )
    if 'errores' in resultado:
        # Si el servicio devuelve errores, se lanza una excepción HTTP con el detalle de los errores
        raise HTTPException(status_code=400, detail=resultado['errores'])
    return resultado
