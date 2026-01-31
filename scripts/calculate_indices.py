"""
Script de Cálculo de Índices Espectrales
Fase 2: Procesamiento de Imágenes
Proyecto: Detección de Cambios Urbanos - Peñaflor

Este script calcula los 4 índices espectrales requeridos:
- NDVI: Índice de Vegetación
- NDBI: Índice de Áreas Construidas
- NDWI: Índice de Agua
- BSI: Índice de Suelo Desnudo
"""

import rasterio
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

INPUT_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# FUNCIONES
# =============================================================================

def calcular_indices(ruta_imagen, ruta_salida):
    """
    Calcula índices espectrales para una imagen Sentinel-2.
    
    Bandas esperadas en el orden de descarga:
    1: B2 (Blue, 490nm)
    2: B3 (Green, 560nm)
    3: B4 (Red, 665nm)
    4: B8 (NIR, 842nm)
    5: B11 (SWIR1, 1610nm)
    6: B12 (SWIR2, 2190nm) - opcional
    
    Args:
        ruta_imagen: Path a la imagen Sentinel-2
        ruta_salida: Path donde guardar los índices
        
    Returns:
        dict: Diccionario con arrays de cada índice y estadísticas
    """
    
    print(f"  📂 Leyendo imagen: {ruta_imagen.name}")
    
    with rasterio.open(ruta_imagen) as src:
        # Leer bandas
        # Las imágenes de GEE ya vienen escaladas (0-1) si usamos .divide(10000)
        # Si vienen como enteros DN, necesitamos escalar
        blue = src.read(1).astype(float)
        green = src.read(2).astype(float)
        red = src.read(3).astype(float)
        nir = src.read(4).astype(float)
        swir = src.read(5).astype(float)
        
        # Verificar si necesitamos escalar (valores > 1 indican DN)
        if np.nanmax(blue) > 1.5:
            print("  ⚙️  Escalando valores de DN a reflectancia (0-1)")
            blue = blue / 10000
            green = green / 10000
            red = red / 10000
            nir = nir / 10000
            swir = swir / 10000
        
        profile = src.profile
        bounds = src.bounds
        transform = src.transform
    
    # Evitar división por cero
    eps = 1e-10
    
    print("  🧮 Calculando índices espectrales...")
    
    # 1. NDVI (Vegetación): (NIR - Red) / (NIR + Red)
    # Rango: -1 a 1 | >0.3 = vegetación saludable
    ndvi = (nir - red) / (nir + red + eps)
    
    # 2. NDBI (Áreas construidas): (SWIR - NIR) / (SWIR + NIR)
    # Rango: -1 a 1 | >0 = áreas urbanas/construidas
    ndbi = (swir - nir) / (swir + nir + eps)
    
    # 3. NDWI (Agua): (Green - NIR) / (Green + NIR)
    # Rango: -1 a 1 | >0 = agua
    ndwi = (green - nir) / (green + nir + eps)
    
    # 4. BSI (Suelo desnudo): ((SWIR + Red) - (NIR + Blue)) / ((SWIR + Red) + (NIR + Blue))
    # Rango: -1 a 1 | valores altos = suelo desnudo
    bsi = ((swir + red) - (nir + blue)) / ((swir + red) + (nir + blue) + eps)
    
    # Aplicar máscaras para valores fuera de rango (-1 a 1)
    indices = {
        'ndvi': np.clip(ndvi, -1, 1),
        'ndbi': np.clip(ndbi, -1, 1),
        'ndwi': np.clip(ndwi, -1, 1),
        'bsi': np.clip(bsi, -1, 1)
    }
    
    # Calcular estadísticas
    stats = {}
    for nombre, array in indices.items():
        valid_data = array[np.isfinite(array)]
        stats[nombre] = {
            'mean': np.mean(valid_data),
            'std': np.std(valid_data),
            'min': np.min(valid_data),
            'max': np.max(valid_data),
            'median': np.median(valid_data)
        }
    
    # Guardar índices en un archivo multi-banda
    print(f"  💾 Guardando índices en: {ruta_salida.name}")
    
    profile.update(
        count=4,
        dtype='float32',
        nodata=-9999
    )
    
    with rasterio.open(ruta_salida, 'w', **profile) as dst:
        dst.write(indices['ndvi'].astype('float32'), 1)
        dst.write(indices['ndbi'].astype('float32'), 2)
        dst.write(indices['ndwi'].astype('float32'), 3)
        dst.write(indices['bsi'].astype('float32'), 4)
        
        # Agregar descripciones a las bandas
        dst.set_band_description(1, 'NDVI')
        dst.set_band_description(2, 'NDBI')
        dst.set_band_description(3, 'NDWI')
        dst.set_band_description(4, 'BSI')
    
    return indices, stats


def print_statistics(year, stats):
    """Imprime estadísticas de forma legible."""
    print(f"\n  📊 Estadísticas {year}:")
    print(f"     {'Índice':<8} {'Media':<8} {'Std':<8} {'Min':<8} {'Max':<8}")
    print(f"     {'-'*45}")
    for nombre, valores in stats.items():
        print(f"     {nombre.upper():<8} {valores['mean']:>7.3f} {valores['std']:>7.3f} "
              f"{valores['min']:>7.3f} {valores['max']:>7.3f}")


def create_summary_table(all_stats):
    """Crea una tabla resumen de todos los años."""
    rows = []
    for year, stats in all_stats.items():
        for indice, valores in stats.items():
            rows.append({
                'Año': year,
                'Índice': indice.upper(),
                'Media': valores['mean'],
                'Desviación': valores['std'],
                'Mínimo': valores['min'],
                'Máximo': valores['max'],
                'Mediana': valores['median']
            })
    
    df = pd.DataFrame(rows)
    return df


# =============================================================================
# PROCESO PRINCIPAL
# =============================================================================

def main():
    """Función principal de procesamiento."""
    
    print("=" * 60)
    print("🧮  CÁLCULO DE ÍNDICES ESPECTRALES")
    print("    Fase 2: Procesamiento de Imágenes")
    print("=" * 60)
    
    # Buscar todas las imágenes
    imagenes = sorted(INPUT_DIR.glob('sentinel2_*.tif'))
    
    if len(imagenes) == 0:
        print("\n❌ No se encontraron imágenes en data/raw/")
        print("   Asegúrate de haber completado la Fase 1 primero.")
        return
    
    print(f"\n📁 Encontradas {len(imagenes)} imágenes para procesar:")
    for img in imagenes:
        print(f"   - {img.name}")
    
    # Procesar cada imagen
    all_stats = {}
    
    for img_path in imagenes:
        # Extraer año del nombre del archivo
        year = img_path.stem.split('_')[1]
        output_path = OUTPUT_DIR / f'indices_{year}.tif'
        
        print(f"\n{'='*60}")
        print(f"⏳ Procesando año {year}...")
        print(f"{'='*60}")
        
        # Calcular índices
        indices, stats = calcular_indices(img_path, output_path)
        all_stats[year] = stats
        
        # Mostrar estadísticas
        print_statistics(year, stats)
    
    # Crear tabla resumen
    print(f"\n{'='*60}")
    print("📈 RESUMEN COMPLETO")
    print(f"{'='*60}\n")
    
    df_resumen = create_summary_table(all_stats)
    print(df_resumen.to_string(index=False))
    
    # Guardar tabla resumen
    csv_path = OUTPUT_DIR / 'estadisticas_indices.csv'
    df_resumen.to_csv(csv_path, index=False)
    print(f"\n💾 Tabla resumen guardada en: {csv_path}")
    
    # Análisis de tendencias
    print(f"\n{'='*60}")
    print("📊 ANÁLISIS DE TENDENCIAS")
    print(f"{'='*60}\n")
    
    # Calcular tendencias de NDVI y NDBI (indicadores clave)
    ndvi_means = [all_stats[y]['ndvi']['mean'] for y in sorted(all_stats.keys())]
    ndbi_means = [all_stats[y]['ndbi']['mean'] for y in sorted(all_stats.keys())]
    years = sorted(all_stats.keys())
    
    ndvi_change = ndvi_means[-1] - ndvi_means[0]
    ndbi_change = ndbi_means[-1] - ndbi_means[0]
    
    print(f"NDVI (Vegetación):")
    print(f"  {years[0]}: {ndvi_means[0]:.3f} → {years[-1]}: {ndvi_means[-1]:.3f}")
    print(f"  Cambio: {ndvi_change:+.3f} {'(pérdida de vegetación)' if ndvi_change < 0 else '(ganancia de vegetación)'}")
    
    print(f"\nNDBI (Urbanización):")
    print(f"  {years[0]}: {ndbi_means[0]:.3f} → {years[-1]}: {ndbi_means[-1]:.3f}")
    print(f"  Cambio: {ndbi_change:+.3f} {'(aumento de urbanización)' if ndbi_change > 0 else '(disminución de urbanización)'}")
    
    print(f"\n{'='*60}")
    print("✅ FASE 2 COMPLETADA")
    print(f"{'='*60}")
    print(f"\n📂 Archivos generados en {OUTPUT_DIR}:")
    for f in sorted(OUTPUT_DIR.glob('indices_*.tif')):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"   - {f.name} ({size_mb:.1f} MB)")
    
    print(f"\n🎯 Próximo paso: Fase 3 - Detección de Cambios")


if __name__ == "__main__":
    main()
