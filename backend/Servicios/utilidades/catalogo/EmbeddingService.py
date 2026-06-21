import os
import logging
from typing import Any, Dict, List, Optional

from AccesoDatos.ArchivosRepositorio import ArchivosRepositorio
from Servicios.utilidades.catalogo.EmbeddingGenerator import EmbeddingGenerator
from Servicios.utilidades.catalogo.EmbeddingSearcher import EmbeddingSearcher

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Servicio que orquesta la generación, persistencia y búsqueda de embeddings de imágenes.

    Layout on disk:
    Datos/catalogo/{card_id}/images
    Datos/catalogo/{card_id}/embeds
    """

    def __init__(self, catalogo_dir: str = os.path.join("Datos", "catalogo")):
        self.catalogo_dir = catalogo_dir
        os.makedirs(self.catalogo_dir, exist_ok=True)
        
        self.generator = EmbeddingGenerator()
        self.searcher = EmbeddingSearcher()
        self.archivos_repo = ArchivosRepositorio()

    def create_card_directory(self, card_id: str) -> str:
        """Crea Datos/catalogo/{card_id}/images y /embeds y retorna el directorio de la carta."""
        return self.archivos_repo.crear_directorio_carta(card_id, self.catalogo_dir)

    def embed_image_bytes(self, image_bytes: bytes) -> Any:
        """Retorna un vector de embedding numpy L2-normalizado para los bytes de imagen dados."""
        return self.generator.embed_image_bytes(image_bytes)

    def persist_embeddings(
        self,
        card_id: str,
        front_emb: Any,
        back_emb: Optional[Any],
        card_dir: Optional[str] = None,
    ) -> None:
        """Persiste embeddings frontal/trasero como archivos .npy dentro de Datos/catalogo/card_id/embeds."""
        try:
            card_dir = card_dir or os.path.join(self.catalogo_dir, card_id)
            
            # Guardar embedding frontal
            self.archivos_repo.guardar_embedding(
                card_id=card_id,
                sufijo="front",
                embedding=front_emb,
                catalogo_dir=self.catalogo_dir
            )
            
            # Guardar embedding trasero si existe
            if back_emb is not None:
                self.archivos_repo.guardar_embedding(
                    card_id=card_id,
                    sufijo="back",
                    embedding=back_emb,
                    catalogo_dir=self.catalogo_dir
                )
            
            logger.info(f"Embeddings persistidos para {card_id}")
        except Exception as e:
            logger.error(f"Fallo al persistir embeddings para {card_id}: {e}")
            raise

    def search(self, query_emb: Any, catalogo_dir: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Busca embeddings persistidos por similitud coseno y retorna lista top_k de {card_id, score}."""
        catalogo_dir = catalogo_dir or self.catalogo_dir
        return self.searcher.search(query_emb, catalogo_dir, top_k)

    def search_with_archivos_repositorio(self, query_emb: Any, top_k: int = 3) -> List[Dict[str, Any]]:
        """Busca embeddings usando ArchivosRepositorio para leer los archivos."""
        return self.searcher.search_with_archivos_repositorio(
            query_emb=query_emb,
            archivos_repositorio=self.archivos_repo,
            catalogo_dir=self.catalogo_dir,
            top_k=top_k
        )

    def evaluate_candidates(self, candidates: List[Dict[str, Any]], threshold: float = 0.85) -> Dict[str, Any]:
        """Evalúa candidatos de búsqueda y retorna decisión."""
        return self.searcher.evaluate_candidates(candidates, threshold)

    def process_and_persist_embeddings(
        self,
        card_id: str,
        front_image_bytes: bytes,
        back_image_bytes: Optional[bytes] = None,
    ) -> None:
        """Procesa imágenes y persiste sus embeddings."""
        try:
            # Generar embeddings
            front_emb = self.generator.embed_image_bytes(front_image_bytes)
            back_emb = None
            if back_image_bytes is not None:
                back_emb = self.generator.embed_image_bytes(back_image_bytes)
            
            # Persistir embeddings
            self.persist_embeddings(
                card_id=card_id,
                front_emb=front_emb,
                back_emb=back_emb
            )
            
        except Exception as e:
            logger.error(f"Error procesando y persistiendo embeddings para {card_id}: {e}")
            raise

    def search_similar_images(
        self,
        query_image_bytes: bytes,
        top_k: int = 3,
        threshold: float = 0.85
    ) -> Dict[str, Any]:
        """Busca imágenes similares dado un query y retorna resultados evaluados."""
        try:
            # Generar embedding para la imagen de query
            query_emb = self.generator.embed_image_bytes(query_image_bytes)
            
            # Buscar candidatos similares
            candidates = self.search(query_emb, top_k=top_k)
            
            # Evaluar candidatos
            evaluation = self.evaluate_candidates(candidates, threshold)
            
            return {
                "query_embedding": query_emb,
                "candidates": candidates,
                "evaluation": evaluation
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda de imágenes similares: {e}")
            raise