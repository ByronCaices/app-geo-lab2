"""
Archivo principal para despliegue en Streamlit Community Cloud
"""
import sys
import os
from pathlib import Path

# Asegurar que el directorio de trabajo sea la raíz del proyecto
os.chdir(Path(__file__).parent)

# Agregar el directorio app al path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Importar y ejecutar la app
import app.app
