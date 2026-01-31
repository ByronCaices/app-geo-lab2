"""
Utilidades para la aplicación Streamlit
Proyecto: Detección de Cambios Urbanos
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from pathlib import Path
from typing import Tuple, Optional


def load_raster(filepath: str) -> Tuple[np.ndarray, dict]:
    """
    Carga un archivo raster y retorna los datos y metadatos.
    
    Args:
        filepath: Ruta al archivo raster
        
    Returns:
        Tuple con (array de datos, diccionario de metadatos)
    """
    with rasterio.open(filepath) as src:
        data = src.read()
        meta = src.meta.copy()
        bounds = src.bounds
        meta['bounds'] = bounds
    return data, meta


def load_vector(filepath: str) -> gpd.GeoDataFrame:
    """
    Carga un archivo vectorial (shapefile, geopackage, etc.)
    
    Args:
        filepath: Ruta al archivo vectorial
        
    Returns:
        GeoDataFrame con los datos
    """
    return gpd.read_file(filepath)


def calculate_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """
    Calcula el Índice de Vegetación de Diferencia Normalizada (NDVI).
    
    Args:
        nir: Banda del infrarrojo cercano
        red: Banda del rojo
        
    Returns:
        Array con valores NDVI [-1, 1]
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)
        ndvi = np.where(np.isfinite(ndvi), ndvi, 0)
    return ndvi


def calculate_ndbi(swir: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """
    Calcula el Índice de Construcción de Diferencia Normalizada (NDBI).
    
    Args:
        swir: Banda del infrarrojo de onda corta
        nir: Banda del infrarrojo cercano
        
    Returns:
        Array con valores NDBI [-1, 1]
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        ndbi = (swir.astype(float) - nir.astype(float)) / (swir + nir)
        ndbi = np.where(np.isfinite(ndbi), ndbi, 0)
    return ndbi


def calculate_ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """
    Calcula el Índice de Agua de Diferencia Normalizada (NDWI).
    
    Args:
        green: Banda del verde
        nir: Banda del infrarrojo cercano
        
    Returns:
        Array con valores NDWI [-1, 1]
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        ndwi = (green.astype(float) - nir.astype(float)) / (green + nir)
        ndwi = np.where(np.isfinite(ndwi), ndwi, 0)
    return ndwi


def calculate_bsi(blue: np.ndarray, red: np.ndarray, 
                  nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
    """
    Calcula el Índice de Suelo Desnudo (BSI).
    
    Args:
        blue: Banda del azul
        red: Banda del rojo
        nir: Banda del infrarrojo cercano
        swir: Banda del infrarrojo de onda corta
        
    Returns:
        Array con valores BSI
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        numerator = (swir.astype(float) + red) - (nir + blue)
        denominator = (swir + red) + (nir + blue)
        bsi = numerator / denominator
        bsi = np.where(np.isfinite(bsi), bsi, 0)
    return bsi


def get_statistics(data: np.ndarray, nodata: Optional[float] = None) -> dict:
    """
    Calcula estadísticas descriptivas de un array.
    
    Args:
        data: Array de datos
        nodata: Valor a ignorar (nodata)
        
    Returns:
        Diccionario con estadísticas
    """
    if nodata is not None:
        data = data[data != nodata]
    
    valid_data = data[np.isfinite(data)]
    
    return {
        "min": float(np.min(valid_data)),
        "max": float(np.max(valid_data)),
        "mean": float(np.mean(valid_data)),
        "std": float(np.std(valid_data)),
        "median": float(np.median(valid_data)),
    }


def format_hectares(pixels: int, pixel_size: float = 10.0) -> float:
    """
    Convierte número de píxeles a hectáreas.
    
    Args:
        pixels: Número de píxeles
        pixel_size: Tamaño del píxel en metros (default 10m para Sentinel-2)
        
    Returns:
        Área en hectáreas
    """
    area_m2 = pixels * (pixel_size ** 2)
    return area_m2 / 10000  # 1 hectárea = 10,000 m²
