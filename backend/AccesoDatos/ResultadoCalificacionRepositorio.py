from typing import Optional
from sqlalchemy.orm import Session
from Modelos.ResultadoCalificacionCarta import ResultadoCalificacionCarta
from Modelos.BaselineCalibracion import BaselineCalibracion


class ResultadoCalificacionRepositorio:

    @staticmethod
    def obtener_por_sesion(
        db: Session, id_sesion: str
    ) -> Optional[ResultadoCalificacionCarta]:
        """Idempotencia: devuelve el resultado existente si ya se procesó esta sesión."""
        return (
            db.query(ResultadoCalificacionCarta)
            .filter(ResultadoCalificacionCarta.id_sesion == id_sesion)
            .first()
        )

    @staticmethod
    def obtener_por_evaluacion_y_sesion(
        db: Session, id_evaluacionCarta: int, id_sesion: str
    ) -> Optional[ResultadoCalificacionCarta]:
        """Devuelve el resultado existente si ya se calificó esta (evaluación, sesión)."""
        return (
            db.query(ResultadoCalificacionCarta)
            .filter(
                ResultadoCalificacionCarta.id_evaluacionCarta == id_evaluacionCarta,
                ResultadoCalificacionCarta.id_sesion == id_sesion,
            )
            .first()
        )

    @staticmethod
    def crear_resultado(
        db: Session,
        id_evaluacionCarta: int,
        id_sesion: str,
        version_algoritmo: str,
        centering_subgrade: Optional[float],
        corners_subgrade: Optional[float],
        edges_subgrade: Optional[float],
        surface_subgrade: Optional[float],
        grado_final: Optional[float],
        uncertainty_band: Optional[float],
        baseline_origen: str,
        baseline_centering: Optional[float],
        baseline_corners: Optional[float],
        baseline_edges: Optional[float],
        baseline_surface: Optional[float],
        tipo_revision: str,
        coherence_flag: str,
    ) -> ResultadoCalificacionCarta:
        """Crea y persiste un nuevo resultado de calificación."""
        resultado = ResultadoCalificacionCarta(
            id_evaluacionCarta=id_evaluacionCarta,
            id_sesion=id_sesion,
            version_algoritmo=version_algoritmo,
            centering_subgrade=centering_subgrade,
            corners_subgrade=corners_subgrade,
            edges_subgrade=edges_subgrade,
            surface_subgrade=surface_subgrade,
            grado_final=grado_final,
            uncertainty_band=uncertainty_band,
            baseline_origen=baseline_origen,
            baseline_centering=baseline_centering,
            baseline_corners=baseline_corners,
            baseline_edges=baseline_edges,
            baseline_surface=baseline_surface,
            tipo_revision=tipo_revision,
            coherence_flag=coherence_flag,
        )
        db.add(resultado)
        db.commit()
        db.refresh(resultado)
        return resultado

    # ── Baseline ─────────────────────────────────────────────────────────────

    @staticmethod
    def obtener_baseline_set_acabado(
        db: Session, set_name: str, acabado: str
    ) -> Optional[BaselineCalibracion]:
        """Busca un baseline calibrado para un (set, acabado) específico."""
        return (
            db.query(BaselineCalibracion)
            .filter(
                BaselineCalibracion.set_name == set_name,
                BaselineCalibracion.acabado == acabado,
            )
            .first()
        )

    @staticmethod
    def obtener_baseline_global(db: Session) -> Optional[BaselineCalibracion]:
        """Busca el baseline global (set_name IS NULL, acabado IS NULL)."""
        return (
            db.query(BaselineCalibracion)
            .filter(
                BaselineCalibracion.set_name.is_(None),
                BaselineCalibracion.acabado.is_(None),
            )
            .first()
        )