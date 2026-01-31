"""
Archivo principal para despliegue en Streamlit Community Cloud
"""
import sys
from pathlib import Path

# Agregar el directorio app al path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Importar y ejecutar la app
from app import *
