from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from AccesoDatos.CartasRepositorio import CartasRepositorio
from Modelos import Cartas as models
from Servicios.utilidades.BuscadorImagenes import EmbeddingService


@dataclass
class SubmitterSearchResult:
	"""Resultado estructurado para búsquedas del submitter."""

	candidatos: list[Dict[str, Any]]
	evaluacion: Dict[str, Any]


class Submitter:
	"""Centraliza la lógica y utilidades que el flujo de submitter necesita.

	Esta clase será el punto único de entrada desde el controlador y podrá crecer
	con nuevas utilidades de submitter en el futuro.
	"""

	def __init__(self, embeddings_dir: str = "embeddings") -> None:
		self.embeddings_dir = embeddings_dir
		self.embedding_service = EmbeddingService(embeddings_dir=embeddings_dir)
		self.cartas_repo = CartasRepositorio()

	def buscar_imagenes(
		self,
		db: Session,
		imagen_frontal: UploadFile,
		imagen_reverso: Optional[UploadFile] = None,
		top_k: int = 3,
	) -> SubmitterSearchResult:
		"""Busca las cartas más similares a una imagen dada.

		Usa la utilidad `EmbeddingService` de la carpeta de utilidades.
		"""
		if not imagen_frontal or not getattr(imagen_frontal, "filename", None):
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Se requiere imagen_frontal",
			)

		front_bytes = self._read_upload_bytes(imagen_frontal)
		_ = self._read_upload_bytes(imagen_reverso) if imagen_reverso and getattr(imagen_reverso, "filename", None) else None

		query_emb = self.embedding_service.embed_image_bytes(front_bytes)
		cartas = self.cartas_repo.get_all_cartas(db)
		if not cartas:
			return SubmitterSearchResult(candidatos=[], evaluacion={"decision": "UNLIKELY", "top": None})

		resultados = self.embedding_service.search(
			query_emb=query_emb,
			embeddings_dir=self.embeddings_dir,
			top_k=top_k,
		)
		evaluacion = self.embedding_service.evaluate_candidates(resultados)

		candidatos = self._enrich_candidates(db, resultados)
		return SubmitterSearchResult(candidatos=candidatos, evaluacion=evaluacion)

	def _read_upload_bytes(self, upload: UploadFile) -> bytes:
		upload.file.seek(0)
		return upload.file.read()

	def _enrich_candidates(self, db: Session, resultados: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
		enriquecidos: list[Dict[str, Any]] = []
		for resultado in resultados:
			card_id = resultado.get("card_id")
			carta = db.query(models.Carta).filter(models.Carta.card_id == card_id).first()
			if carta is None:
				continue
			enriquecidos.append(
				{
					"card_id": card_id,
					"score": resultado.get("score"),
					"set_name": carta.set_name,
					"numero": carta.numero,
					"nombre": carta.nombre,
                    "edicion": carta.edicion,
                    "idioma": carta.idioma,
                    "acabado": carta.acabado,
					"autor": carta.autor,
					"rareza": carta.rareza,
                    "tipo": carta.tipo,
                    "hp": carta.hp,
                    "ilustrador": carta.ilustrador,
                    "anio_impresion": carta.anio_impresion,
				}
			)
		return enriquecidos
