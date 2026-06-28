"""
Script para poblar la tabla ``baseline_calibracion`` con datos iniciales.

Uso:
    cd backend
    .venv\Scripts\python.exe scripts/seed_baseline.py

Los valores aqui son ilustrativos (basados en tendencias tipicas de TCG).
Cuando se disponga de ground truth real de gradings profesionales,
estos valores deben reemplazarse por los calculados con datos reales.
"""

import sys
import os

# Asegura que el directorio raiz del backend este en sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Datos.db import SessionLocal
from Modelos.BaselineCalibracion import BaselineCalibracion


# ── Datos semilla ──────────────────────────────────────────────────────
# Cada tupla: (set_name, acabado, centering, corners, edges, surface,
#              total_muestras, confianza)
#
# set_name=None, acabado=None  → baseline global
SEMILLA = [
    # ── Baseline global ──────────────────────────────────────────────
    (None, None, 8.00, 7.80, 8.20, 8.50, 500, 0.95),

    # ── Sets clasicos (Wizards of the Coast) ─────────────────────────
    ("Base Set", "Holo", 7.20, 7.10, 7.50, 7.80, 45, 0.80),
    ("Base Set", "Non-Holo", 7.50, 7.40, 7.70, 8.00, 30, 0.75),
    ("Jungle", "Holo", 7.30, 7.20, 7.60, 7.90, 38, 0.78),
    ("Jungle", "Non-Holo", 7.60, 7.50, 7.80, 8.10, 32, 0.76),
    ("Fossil", "Holo", 7.40, 7.30, 7.70, 8.00, 35, 0.77),
    ("Fossil", "Non-Holo", 7.70, 7.60, 7.90, 8.20, 30, 0.75),

    # ── Sets modernos (Sun & Moon en adelante) ───────────────────────
    ("Scarlet & Violet", "Reverse Holo", 8.80, 8.50, 8.90, 9.00, 35, 0.78),
    ("Scarlet & Violet", "Holo", 8.50, 8.30, 8.70, 8.80, 40, 0.80),
    ("Scarlet & Violet", "Non-Holo", 8.90, 8.70, 9.10, 9.20, 50, 0.82),
    ("Paldea Evolved", "Reverse Holo", 8.70, 8.40, 8.80, 8.90, 32, 0.76),
    ("Paldea Evolved", "Holo", 8.40, 8.20, 8.60, 8.70, 35, 0.78),
    ("Paldea Evolved", "Non-Holo", 8.80, 8.60, 9.00, 9.10, 38, 0.79),
    ("Obsidian Flames", "Reverse Holo", 8.60, 8.30, 8.70, 8.80, 30, 0.75),
    ("Obsidian Flames", "Non-Holo", 8.70, 8.50, 8.90, 9.00, 33, 0.76),

    # ── Sets de alta gama (especiales / promos) ──────────────────────
    ("Celebrations", "Classic", 9.00, 8.80, 9.20, 9.30, 25, 0.72),
    ("Hidden Fates", "Shiny", 9.10, 8.90, 9.30, 9.40, 28, 0.73),
]


def seed():
    """Inserta los datos semilla en la tabla baseline_calibracion."""
    db = SessionLocal()
    try:
        # Verificar si ya hay datos
        existentes = db.query(BaselineCalibracion).count()
        if existentes > 0:
            print(
                f"La tabla 'baseline_calibracion' ya tiene {existentes} "
                "registros. Se omite la siembra para no duplicar."
            )
            print("Si deseas re-sembrar, borra los registros manualmente "
                  "y ejecuta este script de nuevo.")
            return

        for set_name, acabado, centering, corners, edges, surface, muestras, confianza in SEMILLA:
            registro = BaselineCalibracion(
                set_name=set_name,
                acabado=acabado,
                centering_baseline=centering,
                corners_baseline=corners,
                edges_baseline=edges,
                surface_baseline=surface,
                total_muestras=muestras,
                confianza=confianza,
            )
            db.add(registro)

        db.commit()
        print(f"Seed completado: {len(SEMILLA)} registros insertados en "
              "'baseline_calibracion'.")

    except Exception as e:
        db.rollback()
        print(f"Error durante la siembra: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()