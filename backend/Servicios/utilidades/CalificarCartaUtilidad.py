"""
Utilidad para la calificacion automatica de cartas (Grading).

Transforma los scores 0-100 del preprocesamiento en subgrades 1.0-10.0,
selecciona baseline calibrado por (set, acabado), aplica regla de
coherencia, calcula banda de incertidumbre y persiste el resultado
con version inmutable del algoritmo.

Las validaciones de dominio (insumos, coherencia interna, sesion
duplicada) delegan en CalificarCartaValidacion.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from AccesoDatos.ResultadoCalificacionRepositorio import (
    ResultadoCalificacionRepositorio,
)
from Modelos.EvaluacionCarta import EvaluacionCarta
from Servicios.validaciones.CalificarCartaValidacion import (
    CalificarCartaValidacion,
)


class CalificarCartaUtilidad:
    """Algoritmo de calificacion de carta.

    Metodo principal:
        calificar()
            -> dict con tipo_revision, calificacion, mensaje, etc.

    Constantes de clase versionadas (inmutables por registro).
    """

    ALGORITHM_VERSION = "1.0.0"
    SUBGRADE_MAX = 10.0
    COHERENCE_BUMP_LIMIT = 0.5
    MIN_SAMPLES_CALIBRATED = 30
    UNCERTAINTY_MIN = 0.3
    UNCERTAINTY_FACTOR = 1.5

    @staticmethod
    def calificar(
        db: Session,
        id_evaluacionCarta: int,
        id_sesion: str,
        scores_frontal: Dict[str, Optional[float]],
        scores_reversa: Dict[str, Optional[float]],
        evaluacion: EvaluacionCarta,
        set_name: Optional[str] = None,
        acabado: Optional[str] = None,
        huella_imagenes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Ejecuta el pipeline de calificacion completo."""
        errores = {}

        # Combinacion de scores de ambas caras
        centering = CalificarCartaUtilidad._combinar_dimension(
            scores_frontal.get("centering"), scores_reversa.get("centering")
        )
        corners = CalificarCartaUtilidad._combinar_dimension(
            scores_frontal.get("corners"), scores_reversa.get("corners")
        )
        edges = CalificarCartaUtilidad._combinar_dimension(
            scores_frontal.get("edges"), scores_reversa.get("edges")
        )
        surface = CalificarCartaUtilidad._combinar_dimension(
            scores_frontal.get("surface"), scores_reversa.get("surface")
        )

        # Validaciones de dominio
        CalificarCartaValidacion.validar_insumos_suficientes(
            scores_frontal, scores_reversa, errores
        )
        if centering is None or corners is None or edges is None or surface is None:
            return CalificarCartaUtilidad._manejar_caso_manual(
                db, id_evaluacionCarta, id_sesion,
                centering, corners, edges, surface, evaluacion,
                huella_imagenes=huella_imagenes,
            )

        # Escalamiento de scores a subgrades 1.0-10.0
        centering_sg = CalificarCartaUtilidad._escalar(centering)
        corners_sg   = CalificarCartaUtilidad._escalar(corners)
        edges_sg     = CalificarCartaUtilidad._escalar(edges)
        surface_sg   = CalificarCartaUtilidad._escalar(surface)

        # Seleccion de baseline calibrado (set, acabado) o global
        baseline, global_ref, baseline_origen = CalificarCartaUtilidad._seleccionar_baseline(
            db, set_name, acabado
        )

        # Aplicacion de sesgo segun baseline y calculo de grado final
        centering_aj = CalificarCartaUtilidad._aplicar_sesgo(
            centering_sg, baseline.get("centering"), global_ref.get("centering")
        )
        corners_aj = CalificarCartaUtilidad._aplicar_sesgo(
            corners_sg, baseline.get("corners"), global_ref.get("corners")
        )
        edges_aj = CalificarCartaUtilidad._aplicar_sesgo(
            edges_sg, baseline.get("edges"), global_ref.get("edges")
        )
        surface_aj = CalificarCartaUtilidad._aplicar_sesgo(
            surface_sg, baseline.get("surface"), global_ref.get("surface")
        )

        # Calculo de grado final y banda de incertidumbre
        min_subgrade = min(centering_aj, corners_aj, edges_aj, surface_aj)
        grado_final = round(
            min(min_subgrade + CalificarCartaUtilidad.COHERENCE_BUMP_LIMIT,
                CalificarCartaUtilidad.SUBGRADE_MAX), 1)

        uncertainty_band = CalificarCartaUtilidad._calcular_incertidumbre(
            baseline.get("confianza", 0.0)
        )

        errores.clear()

        # Validacion de coherencia interna
        CalificarCartaValidacion.validar_coherencia_interna(
            centering_aj, corners_aj, edges_aj, surface_aj, errores
        )
        coherence_flag = "REVIEW" if "coherencia_interna" in errores else "OK"
        tipo_revision = "REVIEW" if coherence_flag == "REVIEW" else "AUTO"

        # Persistencia del resultado de calificacion
        repositorio = ResultadoCalificacionRepositorio()
        resultado = repositorio.crear_resultado(
            db=db, id_evaluacionCarta=id_evaluacionCarta,
            id_sesion=id_sesion,
            version_algoritmo=CalificarCartaUtilidad.ALGORITHM_VERSION,
            huella_imagenes=huella_imagenes,
            centering_subgrade=centering_aj, corners_subgrade=corners_aj,
            edges_subgrade=edges_aj, surface_subgrade=surface_aj,
            grado_final=grado_final, uncertainty_band=uncertainty_band,
            baseline_origen=baseline_origen,
            baseline_centering=baseline.get("centering"),
            baseline_corners=baseline.get("corners"),
            baseline_edges=baseline.get("edges"),
            baseline_surface=baseline.get("surface"),
            tipo_revision=tipo_revision, coherence_flag=coherence_flag,
        )

        evaluacion.estado = tipo_revision
        db.commit()

        # Armado de respuesta final
        return CalificarCartaUtilidad._armar_respuesta_exitosa(
            resultado, tipo_revision, coherence_flag,
            centering_aj, corners_aj, edges_aj, surface_aj,
            grado_final, uncertainty_band, baseline_origen,
        )
    

    @staticmethod
    def _combinar_dimension(frontal, reversa):
        if frontal is None and reversa is None:
            return None
        if frontal is None:
            return reversa
        if reversa is None:
            return frontal
        return (frontal + reversa) / 2.0

    @staticmethod
    def _escalar(valor):
        return round(max(1.0, min(CalificarCartaUtilidad.SUBGRADE_MAX, valor / 10.0)), 1)

    @staticmethod
    def _seleccionar_baseline(db, set_name, acabado):
        repositorio = ResultadoCalificacionRepositorio()
        # Primero obtener siempre el global como referencia
        gb = repositorio.obtener_baseline_global(db)
        gl = {
            "centering": gb.centering_baseline if gb else CalificarCartaUtilidad.SUBGRADE_MAX / 2.0,
            "corners": gb.corners_baseline if gb else CalificarCartaUtilidad.SUBGRADE_MAX / 2.0,
            "edges": gb.edges_baseline if gb else CalificarCartaUtilidad.SUBGRADE_MAX / 2.0,
            "surface": gb.surface_baseline if gb else CalificarCartaUtilidad.SUBGRADE_MAX / 2.0,
        }
        # Buscar baseline especifico
        if set_name and acabado:
            esp = repositorio.obtener_baseline_set_acabado(db, set_name, acabado)
            if esp is not None and esp.total_muestras >= CalificarCartaUtilidad.MIN_SAMPLES_CALIBRATED:
                return ({
                    "centering": esp.centering_baseline, "corners": esp.corners_baseline,
                    "edges": esp.edges_baseline, "surface": esp.surface_baseline,
                    "confianza": esp.confianza,
                }, gl, "SET_ACABADO")
        # Fallback a global
        return ({
            "centering": gl["centering"], "corners": gl["corners"],
            "edges": gl["edges"], "surface": gl["surface"],
            "confianza": gb.confianza if gb else 0.5,
        }, gl, "GLOBAL")

    @staticmethod
    def _aplicar_sesgo(subgrade_bruto, baseline_val, global_val=None):
        """Aplica sesgo correctivo respecto al baseline global.

        Formula:
            sesgo = baseline_global - baseline_especifico

        Si el baseline especifico es mas BAJO que el global, la carta
        recibe un BOOST (esa categoria suele salir peor, asi que un
        score normal es mejor de lo que parece).

        Si el baseline especifico es mas ALTO que el global, la carta
        recibe un PENALTY (esa categoria suele salir mejor, asi que
        un score normal es peor de lo que parece).

        Args:
            subgrade_bruto: subgrade en escala 1.0-10.0
            baseline_val: valor del baseline (especifico o global)
            global_val: valor del baseline global (referencia)
        """
        if baseline_val is None:
            return subgrade_bruto
        if global_val is None or global_val == baseline_val:
            # Si no hay referencia global o el baseline ya es el global,
            # no hay sesgo que aplicar
            return subgrade_bruto
        sesgo = global_val - baseline_val
        return round(max(1.0, min(CalificarCartaUtilidad.SUBGRADE_MAX,
                                  subgrade_bruto + sesgo)), 1)

    @staticmethod
    def _calcular_incertidumbre(confianza):
        return round(max(CalificarCartaUtilidad.UNCERTAINTY_MIN, CalificarCartaUtilidad.UNCERTAINTY_FACTOR * (1.0 - confianza)), 2)

    @staticmethod
    def _manejar_caso_manual(db, id_evaluacionCarta, id_sesion, centering, corners, edges, surface, evaluacion, huella_imagenes=None):
        repositorio = ResultadoCalificacionRepositorio()
        repositorio.crear_resultado(
            db=db, id_evaluacionCarta=id_evaluacionCarta, id_sesion=id_sesion,
            version_algoritmo=CalificarCartaUtilidad.ALGORITHM_VERSION,
            huella_imagenes=huella_imagenes,
            centering_subgrade=CalificarCartaUtilidad._escalar(centering) if centering is not None else None,
            corners_subgrade=CalificarCartaUtilidad._escalar(corners) if corners is not None else None,
            edges_subgrade=CalificarCartaUtilidad._escalar(edges) if edges is not None else None,
            surface_subgrade=CalificarCartaUtilidad._escalar(surface) if surface is not None else None,
            grado_final=None, uncertainty_band=None, baseline_origen="GLOBAL",
            baseline_centering=None, baseline_corners=None, baseline_edges=None, baseline_surface=None,
            tipo_revision="MANUAL", coherence_flag="OK",
        )
        evaluacion.estado = "MANUAL"
        db.commit()
        return {
            "tipo_revision": "MANUAL", "estado": "MANUAL", "requiere_accion": True,
            "mensaje": "No fue posible calcular algunos subgrades de forma automatica. La carta ha sido derivada a calificacion manual. Te notificaremos cuando este lista.",
            "calificacion": None,
        }

    @staticmethod
    def _mapear_resultado_existente(resultado):
        if resultado.tipo_revision == "MANUAL":
            return {
                "tipo_revision": "MANUAL", "estado": "MANUAL", "requiere_accion": True,
                "mensaje": "Esta evaluacion ya fue procesada y requiere calificacion manual.",
                "calificacion": None,
            }
        return CalificarCartaUtilidad._armar_respuesta_exitosa(
            resultado, resultado.tipo_revision, resultado.coherence_flag,
            resultado.centering_subgrade, resultado.corners_subgrade,
            resultado.edges_subgrade, resultado.surface_subgrade,
            resultado.grado_final, resultado.uncertainty_band, resultado.baseline_origen,
        )

    @staticmethod
    def _armar_respuesta_exitosa(resultado, tipo_revision, coherence_flag, centering, corners, edges, surface, grado_final, uncertainty_band, baseline_origen):
        requiere_accion = tipo_revision in ("MANUAL", "REVIEW")
        return {
            "tipo_revision": tipo_revision, "estado": tipo_revision,
            "requiere_accion": requiere_accion,
            "mensaje": CalificarCartaUtilidad._mensaje_segun_tipo(tipo_revision, coherence_flag),
            "calificacion": {
                "version_algoritmo": CalificarCartaUtilidad.ALGORITHM_VERSION,
                "centering_subgrade": centering, "corners_subgrade": corners,
                "edges_subgrade": edges, "surface_subgrade": surface,
                "grado_final": grado_final, "uncertainty_band": uncertainty_band,
                "baseline_origen": baseline_origen, "tipo_revision": tipo_revision,
                "coherence_flag": coherence_flag,
            },
        }

    @staticmethod
    def _mensaje_segun_tipo(tipo_revision, coherence_flag):
        if tipo_revision == "MANUAL":
            return "No fue posible calcular algunos subgrades de forma automatica. La carta ha sido derivada a calificacion manual. Te notificaremos cuando este lista."
        if tipo_revision == "REVIEW":
            return "La calificacion se completo, pero los resultados presentan incoherencias internas y han sido derivados a revision humana. Te notificaremos la resolucion."
        return "Evaluacion de carta registrada exitosamente."