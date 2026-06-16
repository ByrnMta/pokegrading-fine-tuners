#!/usr/bin/env python3
"""Script para verificar que los imports de los módulos refactorizados funcionen."""

import sys
import os

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Probar importación de CatalogoValidacion
    from Servicios.validaciones.CatalogoValidacion import CatalogoValidacion
    print("✓ CatalogoValidacion importado correctamente")
    
    # Probar importación de CatalogoFileManager
    from Servicios.utilidades.CatalogoFileManager import CatalogoFileManager
    print("✓ CatalogoFileManager importado correctamente")
    
    # Probar importación de GestorCatalogo
    from Servicios.utilidades.GestorCatalogo import CatalogoServicio
    print("✓ GestorCatalogo importado correctamente")
    
    # Verificar que las constantes existan
    from Servicios.validaciones.CatalogoValidacion import (
        MAX_FILE_SIZE, 
        ALLOWED_EXTENSIONS, 
        MIN_WIDTH, 
        MIN_HEIGHT,
        CANONICAL_RARITIES,
        VALID_TYPES,
        SUPPORTED_LANGUAGES
    )
    print("✓ Constantes importadas correctamente")
    
    # Verificar métodos principales
    print("\nVerificando métodos principales:")
    print(f"- CatalogoValidacion tiene método 'validar_identidad': {hasattr(CatalogoValidacion, 'validar_identidad')}")
    print(f"- CatalogoValidacion tiene método 'validar_imagen': {hasattr(CatalogoValidacion, 'validar_imagen')}")
    print(f"- CatalogoFileManager tiene método 'guardar_imagenes': {hasattr(CatalogoFileManager, 'guardar_imagenes')}")
    print(f"- CatalogoServicio tiene método 'agregar_carta': {hasattr(CatalogoServicio, 'agregar_carta')}")
    
    print("\n✅ Todos los imports funcionan correctamente!")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1)