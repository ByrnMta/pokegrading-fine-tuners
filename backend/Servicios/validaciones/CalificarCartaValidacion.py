from __future__ import annotations

from typing import Dict, Optional

from sqlalchemy.orm import Session

from AccesoDatos.ResultadoCalificacionRepositorio import (
    ResultadoCalificacionRepositorio,
)

# Umbral maximo de dispersion entre subgrades para considerar la
# calificacion coherente. Si max - min supera este valor -> REVIEW.
COHERENCE_MAX_SPREAD = 3.0


class CalificarCartaValidacion:

    @staticmethod
    def validar_insumos_suficientes(
        scores_frontal: Dict[str, Optional[float]],
        scores_reversa: Dict[str, Optional[float]],
        errores: dict,
    ) -> None:
        """Valida que ninguna dimension combinada quede como None.

        Si ambas caras tienen None en la misma dimension, o una cara
        tiene None y la otra tambien, la dimension combinada queda
        como None -> insumos insuficientes.
        """
        for dim in ("centering", "corners", "edges", "surface"):
            frontal = scores_frontal.get(dim)
            reversa = scores_reversa.get(dim)
            if frontal is None and reversa is None:
                errores[f"{dim}_insumos"] = (
                    f"No se pudo calcular '{dim}' en ninguna de las caras."
                )

    @staticmethod
    def validar_coherencia_interna(
        centering: float,
        corners: float,
        edges: float,
        surface: float,
        errores: dict,
    ) -> None:
        """Valida que la dispersion entre subgrades no exceda el umbral.

        Si la diferencia entre el subgrade mas alto y el mas bajo
        supera COHERENCE_MAX_SPREAD, se marca para revision humana.
        """
        max_subgrade = max(centering, corners, edges, surface)
        min_subgrade = min(centering, corners, edges, surface)

        if (max_subgrade - min_subgrade) > COHERENCE_MAX_SPREAD:
            errores["coherencia_interna"] = (
                f"Dispersion de {round(max_subgrade - min_subgrade, 1)} "
                f"puntos entre subgrades supera el umbral de "
                f"{COHERENCE_MAX_SPREAD}. Requiere revision humana."
            )

    @staticmethod
    def validar_sesion_no_duplicada(
        db: Session,
        id_sesion: str,
        errores: dict,
    ) -> None:
        """Valida que no exista ya un resultado para esta sesion.

        La idempotencia se basa unicamente en el id_sesion (no en
        id_evaluacionCarta), porque cada reintento crearia un nuevo
        id_evaluacionCarta.
        """
        repositorio = ResultadoCalificacionRepositorio()
        existente = repositorio.obtener_por_sesion(db, id_sesion)
        if existente is not None:
            errores["sesion_duplicada"] = {
                "mensaje": "Esta sesion ya fue procesada.",
                "resultado_existente": existente,
            }