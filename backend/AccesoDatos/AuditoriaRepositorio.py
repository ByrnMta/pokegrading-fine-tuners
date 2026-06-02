import json
from sqlalchemy.orm import Session
from Modelos import AuditoriaCarta as models

"""Acceso a datos para la auditoría de altas de cartas."""


class AuditoriaRepositorio:
    """Persistencia de eventos de auditoría relacionados con cartas."""

    def create_auditoria(self, db: Session, carta_id: int, card_id: str, autor: str, datos: dict):
        """Registra el evento de alta con el payload completo recibido."""
        db_auditoria = models.AuditoriaCarta(
            carta_id=carta_id,
            card_id=card_id,
            autor=autor,
            accion="ALTA",
            datos_json=json.dumps(datos, ensure_ascii=True),
        )
        db.add(db_auditoria)
        return db_auditoria
