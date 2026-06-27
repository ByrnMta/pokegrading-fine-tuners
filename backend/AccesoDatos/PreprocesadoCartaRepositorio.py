from sqlalchemy.orm import Session
from Modelos.PreprocesadoCarta import PreprocesadoCarta

class PreprocesadoCartaRepositorio:

    @staticmethod
    def crear_preprocesado_carta(
        db: Session, 
        id_evaluacionCarta: int, 
        tipo_revision: str, 
        centering_score: float, 
        corner_score: float, 
        edges_score: float, 
        surface_score: float,
        tipo_imagen: str
    ):
        """Crea un registro de preprocesado de carta en la base de datos."""

        preprocesado = PreprocesadoCarta(
            id_evaluacionCarta=id_evaluacionCarta,
            tipo_revision=tipo_revision,
            centering_score=centering_score,
            corner_score=corner_score,
            edges_score=edges_score,
            surface_score=surface_score,
            tipo_imagen=tipo_imagen
        )
        db.add(preprocesado)
        db.commit()
        db.refresh(preprocesado)
        return preprocesado