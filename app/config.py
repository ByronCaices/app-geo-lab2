"""
Configuración de la aplicación Streamlit
Proyecto: Detección de Cambios Urbanos
"""

import os
from pathlib import Path

# Rutas base del proyecto
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
VECTOR_DIR = DATA_DIR / "vector"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Configuración del área de estudio - Peñaflor
STUDY_AREA = {
    "name": "Peñaflor",
    "center_lat": -33.61,
    "center_lon": -70.89,
    "zoom": 13,
    "bounds": [-70.96, -33.68, -70.82, -33.54],  # [Oeste, Sur, Este, Norte]
}

# Fechas de análisis (ajustar según imágenes descargadas)
ANALYSIS_DATES = [
    "2018",
    "2020",
    "2022",
    "2024",
]

# Índices espectrales a calcular
SPECTRAL_INDICES = {
    "NDVI": "Índice de Vegetación de Diferencia Normalizada",
    "NDBI": "Índice de Construcción de Diferencia Normalizada",
    "NDWI": "Índice de Agua de Diferencia Normalizada",
    "BSI": "Índice de Suelo Desnudo",
}

# Umbrales para clasificación de cambios
CHANGE_THRESHOLDS = {
    "urbanization": 0.15,    # Umbral para detectar urbanización
    "vegetation_loss": -0.2, # Umbral para pérdida de vegetación
    "vegetation_gain": 0.2,  # Umbral para ganancia de vegetación
}

# Configuración del mapa
MAP_CONFIG = {
    "tiles": "CartoDB positron",
    "attr": "Detección de Cambios Urbanos",
}
