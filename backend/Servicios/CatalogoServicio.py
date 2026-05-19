import os
import uuid
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from Repositorios.CartasRepositorio import CartasRepositorio
from Esquemas.CartasEsquema import CartaCreate

class CatalogoServicio:
    def __init__(self):
        self.repositorio = CartasRepositorio()
        self.upload_dir = "uploads"
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    #============================= Lógica endpoints =============================
    @staticmethod
    def agregar_carta(db: Session, nombre: str, numero: int, set_name: str, imagen: UploadFile):
        # Lógica de negocio para agregar una nueva carta al catálogo.
        CatalogoServicio._validar_imagen(imagen)

        repositorio = CartasRepositorio()
        carta_existente = repositorio.get_carta_by_nombre_and_numero(db, nombre=nombre, numero=numero)
        if carta_existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La carta ya existe en el catálogo.")

        if not all([nombre, numero, set_name]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La metadata de la carta está incompleta.")

        try:
            ruta_imagen = CatalogoServicio._guardar_imagen(imagen)
            carta_data = CartaCreate(nombre=nombre, numero=numero, set_name=set_name)
            return repositorio.create_carta(db=db, carta=carta_data, image_path=ruta_imagen)
        except Exception as e:
            # En caso de error, se podría implementar un rollback para eliminar la imagen guardada si es necesario.
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Fallo de persistencia: {e}")


    #============================= Validaciones =============================
    @staticmethod
    def _validar_imagen(imagen: UploadFile):
        # Valida la extensión y el tipo de contenido de la imagen.
        if not imagen:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se ha subido ninguna imagen.")
        allowed_extensions = {"png", "jpg", "jpeg"}
        extension = imagen.filename.split(".")[-1]
        if extension.lower() not in allowed_extensions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Extensión de archivo no permitida.")

    #============================= Utilidadeds =============================
    @staticmethod
    def _guardar_imagen(imagen: UploadFile) -> str:
        # Guarda la imagen en el almacenamiento local y devuelve la ruta.
        try:
            extension = imagen.filename.split(".")[-1]
            nombre_archivo = f"{uuid.uuid4()}.{extension}"
            upload_dir = "uploads"
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            ruta_archivo = os.path.join(upload_dir, nombre_archivo)
            with open(ruta_archivo, "wb") as buffer:
                buffer.write(imagen.file.read())
            return ruta_archivo
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al guardar la imagen: {e}")

    
