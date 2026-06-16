import os
import logging
from typing import Any, Dict, List, Optional

try:
    import numpy as np
except Exception:
    np = None

logger = logging.getLogger(__name__)


class EmbeddingSearcher:
    """Busca y evalúa embeddings de imágenes."""

    def __init__(self):
        pass

    def search(
        self, 
        query_emb: Any, 
        catalogo_dir: str, 
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Busca embeddings persistidos por similitud coseno y retorna lista top_k de {card_id, score}."""
        if np is None:
            raise RuntimeError("NumPy es requerido para búsqueda de embeddings")

        results: Dict[str, float] = {}
        try:
            qnorm = np.linalg.norm(query_emb)
            if qnorm == 0:
                return []
            q = query_emb / qnorm

            if not os.path.exists(catalogo_dir):
                return []

            for card_folder in os.listdir(catalogo_dir):
                card_dir = os.path.join(catalogo_dir, card_folder)
                embeds_dir = os.path.join(card_dir, "embeds")
                if not os.path.isdir(embeds_dir):
                    continue

                for fname in os.listdir(embeds_dir):
                    if not fname.endswith(".npy"):
                        continue
                    try:
                        emb = np.load(os.path.join(embeds_dir, fname))
                        if np.linalg.norm(emb) == 0:
                            continue
                        emb = emb / np.linalg.norm(emb)
                        sim = float(np.dot(q, emb))
                        if card_folder not in results or sim > results[card_folder]:
                            results[card_folder] = sim
                    except Exception as e:
                        logger.debug(f"Saltando archivo de embedding {fname}: {e}")
                        continue

            ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)[:top_k]
            return [{"card_id": cid, "score": score} for cid, score in ranked]
        except Exception as e:
            logger.error(f"Búsqueda falló: {e}")
            return []

    def evaluate_candidates(
        self, 
        candidates: List[Dict[str, Any]], 
        threshold: float = 0.85
    ) -> Dict[str, Any]:
        """Evalúa candidatos de búsqueda y retorna decisión."""
        if not candidates:
            return {"decision": "UNLIKELY", "top": None}

        top = candidates[0]
        top_score = (top["score"] + 1) / 2  # Convertir de [-1, 1] a [0, 1]
        if top_score >= threshold:
            decision = "MATCH"
        elif top_score >= threshold * 0.75:
            decision = "POSSIBLE"
        else:
            decision = "UNLIKELY"
        return {"decision": decision, "top": top}

    def search_with_archivos_repositorio(
        self,
        query_emb: Any,
        archivos_repositorio,
        catalogo_dir: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Versión alternativa que usa ArchivosRepositorio para leer embeddings."""
        if np is None:
            raise RuntimeError("NumPy es requerido para búsqueda de embeddings")

        results: Dict[str, float] = {}
        try:
            qnorm = np.linalg.norm(query_emb)
            if qnorm == 0:
                return []
            q = query_emb / qnorm

            # Usar ArchivosRepositorio para listar embeddings
            embeddings_info = archivos_repositorio.listar_embeddings(catalogo_dir)
            
            for emb_info in embeddings_info:
                try:
                    emb = archivos_repositorio.leer_embedding(emb_info["ruta"])
                    if np.linalg.norm(emb) == 0:
                        continue
                    emb = emb / np.linalg.norm(emb)
                    sim = float(np.dot(q, emb))
                    card_id = emb_info["card_id"]
                    if card_id not in results or sim > results[card_id]:
                        results[card_id] = sim
                except Exception as e:
                    logger.debug(f"Saltando embedding {emb_info['archivo']}: {e}")
                    continue

            ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)[:top_k]
            return [{"card_id": cid, "score": score} for cid, score in ranked]
        except Exception as e:
            logger.error(f"Búsqueda con ArchivosRepositorio falló: {e}")
            return []