import os
from typing import Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from AccesoDatos.CartasRepositorio import CartasRepositorio
from AccesoDatos.AuditoriaRepositorio import AuditoriaRepositorio
from AccesoDatos.ArchivosRepositorio import ArchivosRepositorio
from Esquemas.CartasEsquema import CartaCreate
from Servicios.utilidades.catalogo.EmbeddingService import EmbeddingService
from Servicios.validaciones.CatalogoValidacion import CatalogoValidacion

"""Lógica de negocio para el alta de cartas en el catálogo.

Este módulo orquesta el flujo completo de alta de cartas, coordinando
validaciones, persistencia de archivos, generación de embeddings y auditoría.
"""

DATA_ROOT = os.path.join("Datos", "catalogo")


class CatalogoServicio:
    """Orquesta el alta de cartas y sus efectos colaterales asociados."""

    # ============================= Lógica endpoints =============================

    @staticmethod
    def agregar_carta(
        db: Session,
        carta_data: CartaCreate,
        imagen_frontal: UploadFile,
        imagen_reverso: UploadFile,
    ) -> dict:
        """Valida, persiste y audita una carta nueva.

        La secuencia es:
        1. Validar datos de entrada (identidad, display, autor, imágenes)
        2. Verificar que no exista una carta con la misma identidad
        3. Generar card_id y guardar imágenes
        4. Generar y persistir embeddings
        5. Crear carta y registro de auditoría en transacción
        """
        # 1. Validar datos de entrada
        errores = {}
        
        # Validar campos de identidad
        identidad = CatalogoValidacion.validar_identidad(carta_data, errores)
        
        # Validar campos de display
        display = CatalogoValidacion.validar_display(carta_data, errores)
        
        # Validar autor
        autor = CatalogoValidacion.validar_autor(carta_data.autor, errores)
        
        # Validar listas de valores permitidos
        CatalogoValidacion.validar_listas(identidad, display, errores)
        
        # Validar imágenes
        CatalogoValidacion.validar_imagen(imagen_frontal, "imagen_frontal", errores)
        CatalogoValidacion.validar_imagen(imagen_reverso, "imagen_reverso", errores)
        
        # Si hay errores, lanzar excepción
        if errores:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errores": errores}
            )

        # 2. Verificar unicidad de la carta
        #repositorio = CartasRepositorio()
        if CartasRepositorio.get_carta_by_identidad(db, identidad=identidad):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La carta con la misma combinación de set, número, edición, idioma y acabado ya existe.",
            )

        # 3. Generar identificador y guardar imágenes
        card_id = ArchivosRepositorio.generar_card_id()
        try:
            image_front_path, image_back_path = ArchivosRepositorio.guardar_imagenes(
                card_id=card_id,
                imagen_frontal=imagen_frontal,
                imagen_reverso=imagen_reverso,
            )
        except Exception as e:
            # En caso de error al guardar imágenes, limpiar directorio si se creó
            card_dir = os.path.join(DATA_ROOT, card_id)
            if os.path.exists(card_dir):
                ArchivosRepositorio.borrar_directorio_carta(card_dir)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar las imágenes: {str(e)}",
            )

        # 4. Preparar datos para persistencia
        carta_payload = {**identidad, **display, "autor": autor}
        auditoria_payload = {
            **carta_payload,
            "card_id": card_id,
            "image_front_path": image_front_path,
            "image_back_path": image_back_path,
        }

        # 5. Procesar embeddings y persistir en base de datos
        auditoria_repo = AuditoriaRepositorio()
        try:
            # Generar y persistir embeddings
            CatalogoServicio._procesar_embeddings(
                card_id=card_id,
                image_front_path=image_front_path,
                image_back_path=image_back_path,
            )

            # Crear carta y auditoría en transacción
            nueva_carta = CartasRepositorio.create_carta(
                db=db,
                carta_data=carta_payload,
                card_id=card_id,
                image_front_path=image_front_path,
                image_back_path=image_back_path,
                estado="ACTIVA",
            )
            
            auditoria_repo.create_auditoria(
                db=db,
                carta_id=nueva_carta.id,
                card_id=card_id,
                autor=autor,
                datos=auditoria_payload,
            )
            
            db.commit()
            db.refresh(nueva_carta)
            return nueva_carta
            
        except HTTPException:
            db.rollback()
            CatalogoServicio._limpiar_en_error(card_id, image_front_path, image_back_path)
            raise
            
        except Exception as e:
            db.rollback()
            CatalogoServicio._limpiar_en_error(card_id, image_front_path, image_back_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno al guardar la carta: {str(e)}",
            )

    # ============================= Métodos auxiliares =============================

    @staticmethod
    def _procesar_embeddings(card_id: str, image_front_path: str, image_back_path: Optional[str]) -> None:
        """Genera y persiste embeddings para las imágenes de la carta."""
        try:
            emb_svc = EmbeddingService(catalogo_dir=DATA_ROOT)
            
            # Leer y procesar imagen frontal usando ArchivosRepositorio
            front_bytes = ArchivosRepositorio.leer_imagen(image_front_path)
            
            # Leer y procesar imagen reverso (si existe)
            back_bytes = None
            if image_back_path:
                back_bytes = ArchivosRepositorio.leer_imagen(image_back_path)
            
            # Generar embeddings
            front_emb = emb_svc.embed_image_bytes(front_bytes)
            back_emb = emb_svc.embed_image_bytes(back_bytes) if back_bytes is not None else None
            
            # Persistir embeddings
            card_dir = os.path.join(DATA_ROOT, card_id)
            emb_svc.persist_embeddings(
                card_id=card_id,
                front_emb=front_emb,
                back_emb=back_emb,
                card_dir=card_dir
            )
            
        except Exception as e:
            # Limpiar archivos en caso de error
            card_dir = os.path.join(DATA_ROOT, card_id)
            if os.path.exists(card_dir):
                ArchivosRepositorio.borrar_directorio_carta(card_dir)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar embeddings: {str(e)}",
            )

    @staticmethod
    def _limpiar_en_error(card_id: str, image_front_path: str, image_back_path: Optional[str]) -> None:
        """Limpia recursos creados en caso de error durante el proceso."""
        # Borrar archivos de imágenes si existen
        ArchivosRepositorio.borrar_archivo(image_front_path)
        if image_back_path:
            ArchivosRepositorio.borrar_archivo(image_back_path)
        
        # Borrar directorio de la carta
        card_dir = os.path.join(DATA_ROOT, card_id)
        ArchivosRepositorio.borrar_directorio_carta(card_dir)
