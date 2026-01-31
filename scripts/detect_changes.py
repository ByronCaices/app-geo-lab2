#!/usr/bin/env python3
"""
Script de Detección de Cambios - Fase 3
=========================================
Implementa 3 métodos de detección de cambios urbanos:
1. Diferencia Simple (ΔNDVI)
2. Clasificación Multicriterio (múltiples índices)
3. Análisis Z-score (anomalías estadísticas)

Autor: Byron Caices
Fecha: Enero 2025
Universidad de Santiago de Chile
"""

import numpy as np
import rasterio
from pathlib import Path
import pandas as pd
from scipy import stats

# Configuración
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR = BASE_DIR / 'data' / 'processed'

# Años a analizar
YEAR_INICIO = 2018
YEAR_FIN = 2024
YEARS_ALL = [2018, 2020, 2022, 2024]

# Umbrales configurables (ajustados para Peñaflor)
UMBRALES = {
    'ndvi_veg': 0.3,       # NDVI > 0.3 se considera vegetación densa
    'ndbi_urbano': 0.0,    # NDBI > 0 se considera área urbana/construida
    'ndwi_agua': 0.1,      # NDWI > 0.1 se considera agua superficial
    'cambio_min': 0.15,    # Cambio mínimo significativo en índices
    'zscore_umbral': 2.0   # Umbral Z-score para anomalías (±2 desv. est.)
}

# Nombres de clases de cambio
CLASES_CAMBIO = {
    0: 'Sin cambio',
    1: 'Urbanización',
    2: 'Pérdida vegetación',
    3: 'Ganancia vegetación',
    4: 'Nuevo cuerpo agua',
    5: 'Pérdida agua'
}

print("="*70)
print("🔍  DETECCIÓN DE CAMBIOS URBANOS")
print("    Fase 3: Análisis Multi-Temporal")
print("="*70)
print(f"\n📅 Periodo de análisis: {YEAR_INICIO} - {YEAR_FIN}")
print(f"📊 Métodos implementados: 3")
print(f"⚙️  Umbrales configurados:")
for key, val in UMBRALES.items():
    print(f"   - {key}: {val}")
print()


def detectar_cambio_diferencia(ruta_t1, ruta_t2, umbral=0.15):
    """
    MÉTODO 1: Diferencia Simple de NDVI
    ====================================
    Detecta cambios restando NDVI entre dos fechas.
    
    Parámetros:
    -----------
    ruta_t1 : Path
        Ruta al archivo de índices del año inicial
    ruta_t2 : Path
        Ruta al archivo de índices del año final
    umbral : float
        Magnitud mínima de cambio significativo
        
    Retorna:
    --------
    cambio : array
        Clasificación: -1 (pérdida), 0 (sin cambio), 1 (ganancia)
    diferencia : array
        Valores continuos de diferencia NDVI
    stats_dict : dict
        Estadísticas del análisis
    """
    
    print("="*70)
    print("MÉTODO 1: DIFERENCIA SIMPLE (ΔNDVI)")
    print("="*70)
    
    # Leer índices año inicial
    with rasterio.open(ruta_t1) as src1:
        ndvi_t1 = src1.read(1).astype(np.float32)  # Banda 1 = NDVI
        profile = src1.profile.copy()
        
    # Leer índices año final
    with rasterio.open(ruta_t2) as src2:
        ndvi_t2 = src2.read(1).astype(np.float32)
    
    # Aplicar máscara de nodata
    mask_valido = (ndvi_t1 != -9999) & (ndvi_t2 != -9999)
    
    # Calcular diferencia
    diferencia = np.where(mask_valido, ndvi_t2 - ndvi_t1, -9999)
    
    # Clasificar cambios
    cambio = np.zeros_like(diferencia, dtype=np.int8)
    cambio[diferencia < -umbral] = -1  # Pérdida de vegetación
    cambio[diferencia > umbral] = 1    # Ganancia de vegetación
    cambio[~mask_valido] = -128        # Nodata
    
    # Calcular estadísticas
    pixeles_validos = np.sum(mask_valido)
    pixeles_perdida = np.sum(cambio == -1)
    pixeles_ganancia = np.sum(cambio == 1)
    pixeles_sin_cambio = np.sum(cambio == 0)
    
    # Convertir píxeles a hectáreas (píxel Sentinel-2 = 10m × 10m = 100 m² = 0.01 ha)
    ha_perdida = pixeles_perdida * 0.01
    ha_ganancia = pixeles_ganancia * 0.01
    ha_sin_cambio = pixeles_sin_cambio * 0.01
    
    # Estadísticas de la diferencia (solo píxeles válidos)
    diff_valida = diferencia[mask_valido]
    
    stats_dict = {
        'metodo': 'Diferencia Simple',
        'pixeles_validos': pixeles_validos,
        'pixeles_perdida': pixeles_perdida,
        'pixeles_ganancia': pixeles_ganancia,
        'pixeles_sin_cambio': pixeles_sin_cambio,
        'pct_perdida': 100 * pixeles_perdida / pixeles_validos if pixeles_validos > 0 else 0,
        'pct_ganancia': 100 * pixeles_ganancia / pixeles_validos if pixeles_validos > 0 else 0,
        'pct_sin_cambio': 100 * pixeles_sin_cambio / pixeles_validos if pixeles_validos > 0 else 0,
        'ha_perdida': ha_perdida,
        'ha_ganancia': ha_ganancia,
        'ha_sin_cambio': ha_sin_cambio,
        'diferencia_media': float(np.mean(diff_valida)),
        'diferencia_std': float(np.std(diff_valida)),
        'diferencia_min': float(np.min(diff_valida)),
        'diferencia_max': float(np.max(diff_valida))
    }
    
    print(f"\n📊 Resultados:")
    print(f"   Píxeles analizados: {pixeles_validos:,}")
    print(f"\n   Pérdida vegetación:  {pixeles_perdida:,} px ({stats_dict['pct_perdida']:.2f}%) = {ha_perdida:.2f} ha")
    print(f"   Ganancia vegetación: {pixeles_ganancia:,} px ({stats_dict['pct_ganancia']:.2f}%) = {ha_ganancia:.2f} ha")
    print(f"   Sin cambio:          {pixeles_sin_cambio:,} px ({stats_dict['pct_sin_cambio']:.2f}%) = {ha_sin_cambio:.2f} ha")
    print(f"\n   ΔNDVI medio: {stats_dict['diferencia_media']:+.4f}")
    print(f"   Rango: [{stats_dict['diferencia_min']:+.4f}, {stats_dict['diferencia_max']:+.4f}]")
    
    return cambio, diferencia, stats_dict


def clasificar_cambio_urbano(ruta_t1, ruta_t2, umbrales=None):
    """
    MÉTODO 2: Clasificación Multicriterio
    ======================================
    Clasifica tipos de cambio usando múltiples índices espectrales.
    
    Clases:
        0: Sin cambio
        1: Urbanización (vegetación → construido)
        2: Pérdida de vegetación (otros tipos)
        3: Ganancia de vegetación
        4: Nuevo cuerpo de agua
        5: Pérdida de agua
        
    Parámetros:
    -----------
    ruta_t1 : Path
        Ruta al archivo de índices del año inicial
    ruta_t2 : Path
        Ruta al archivo de índices del año final
    umbrales : dict
        Diccionario con umbrales de clasificación
        
    Retorna:
    --------
    clase : array
        Clasificación de cambio (0-5)
    stats_dict : dict
        Estadísticas por clase
    """
    
    print("\n" + "="*70)
    print("MÉTODO 2: CLASIFICACIÓN MULTICRITERIO")
    print("="*70)
    
    if umbrales is None:
        umbrales = UMBRALES
    
    # Leer todos los índices año inicial
    with rasterio.open(ruta_t1) as src1:
        ndvi_t1 = src1.read(1).astype(np.float32)
        ndbi_t1 = src1.read(2).astype(np.float32)
        ndwi_t1 = src1.read(3).astype(np.float32)
        profile = src1.profile.copy()
    
    # Leer todos los índices año final
    with rasterio.open(ruta_t2) as src2:
        ndvi_t2 = src2.read(1).astype(np.float32)
        ndbi_t2 = src2.read(2).astype(np.float32)
        ndwi_t2 = src2.read(3).astype(np.float32)
    
    # Máscara de datos válidos
    mask_valido = (ndvi_t1 != -9999) & (ndvi_t2 != -9999)
    
    # Inicializar clasificación
    clase = np.zeros_like(ndvi_t1, dtype=np.uint8)
    
    # REGLA 1: Urbanización (era vegetación, ahora es urbano)
    era_vegetacion = ndvi_t1 > umbrales['ndvi_veg']
    es_urbano = ndbi_t2 > umbrales['ndbi_urbano']
    aumento_ndbi = (ndbi_t2 - ndbi_t1) > umbrales['cambio_min']
    clase[era_vegetacion & es_urbano & aumento_ndbi & mask_valido] = 1
    
    # REGLA 2: Pérdida de vegetación (no necesariamente urbanización)
    perdio_veg = (ndvi_t1 - ndvi_t2) > umbrales['cambio_min']
    clase[(perdio_veg & mask_valido) & (clase == 0)] = 2
    
    # REGLA 3: Ganancia de vegetación
    gano_veg = (ndvi_t2 - ndvi_t1) > umbrales['cambio_min']
    clase[(gano_veg & mask_valido) & (clase == 0)] = 3
    
    # REGLA 4: Nuevo cuerpo de agua
    era_no_agua = ndwi_t1 < 0
    es_agua = ndwi_t2 > umbrales['ndwi_agua']
    clase[(era_no_agua & es_agua & mask_valido) & (clase == 0)] = 4
    
    # REGLA 5: Pérdida de agua
    era_agua = ndwi_t1 > umbrales['ndwi_agua']
    no_es_agua = ndwi_t2 < 0
    clase[(era_agua & no_es_agua & mask_valido) & (clase == 0)] = 5
    
    # Marcar nodata
    clase[~mask_valido] = 255
    
    # Calcular estadísticas por clase
    pixeles_validos = np.sum(mask_valido)
    stats_list = []
    
    print(f"\n📊 Resultados por clase:")
    print(f"   {'Clase':<5} {'Tipo de cambio':<25} {'Píxeles':<12} {'%':<8} {'Hectáreas':<10}")
    print(f"   {'-'*70}")
    
    for clase_id, nombre in CLASES_CAMBIO.items():
        pixeles = np.sum(clase == clase_id)
        pct = 100 * pixeles / pixeles_validos if pixeles_validos > 0 else 0
        ha = pixeles * 0.01
        
        stats_list.append({
            'clase_id': clase_id,
            'nombre': nombre,
            'pixeles': pixeles,
            'porcentaje': pct,
            'hectareas': ha
        })
        
        print(f"   {clase_id:<5} {nombre:<25} {pixeles:<12,} {pct:<7.2f}% {ha:<10.2f}")
    
    stats_dict = {
        'metodo': 'Clasificación Multicriterio',
        'clases': stats_list,
        'pixeles_validos': pixeles_validos
    }
    
    return clase, stats_dict


def analisis_zscore(rutas_serie_temporal, indice_analisis=-1):
    """
    MÉTODO 3: Análisis Z-score (Anomalías Estadísticas)
    ====================================================
    Detecta cambios significativos comparando con la media histórica.
    
    Z-score = (actual - media_histórica) / (std_histórica + ε)
    
    Parámetros:
    -----------
    rutas_serie_temporal : list of Path
        Lista de rutas a archivos de índices (ordenados cronológicamente)
    indice_analisis : int
        Índice del año a analizar (default: -1 = último año)
        
    Retorna:
    --------
    z_score : array
        Valores Z-score del NDVI
    cambio_significativo : array
        Máscara booleana de cambios significativos (|Z| > 2)
    direccion : array
        Dirección del cambio: -1 (negativo), 0 (normal), 1 (positivo)
    stats_dict : dict
        Estadísticas del análisis
    """
    
    print("\n" + "="*70)
    print("MÉTODO 3: ANÁLISIS Z-SCORE (ANOMALÍAS ESTADÍSTICAS)")
    print("="*70)
    
    # Leer todos los años
    stack_ndvi = []
    for i, ruta in enumerate(rutas_serie_temporal):
        with rasterio.open(ruta) as src:
            ndvi = src.read(1).astype(np.float32)
            stack_ndvi.append(ndvi)
            if i == indice_analisis or (indice_analisis == -1 and i == len(rutas_serie_temporal) - 1):
                profile = src.profile.copy()
    
    stack_ndvi = np.array(stack_ndvi)
    
    # Calcular estadísticas históricas (excluir año de análisis)
    historico = np.delete(stack_ndvi, indice_analisis, axis=0)
    
    # Máscara de datos válidos
    mask_valido = stack_ndvi[indice_analisis] != -9999
    
    # Calcular media y desviación estándar del histórico
    media_hist = np.nanmean(historico, axis=0)
    std_hist = np.nanstd(historico, axis=0)
    
    # Imagen a analizar
    actual = stack_ndvi[indice_analisis]
    
    # Calcular Z-score
    z_score = np.where(
        mask_valido,
        (actual - media_hist) / (std_hist + 1e-10),
        -9999
    )
    
    # Detectar cambios significativos (|Z| > umbral)
    umbral_z = UMBRALES['zscore_umbral']
    cambio_significativo = np.abs(z_score) > umbral_z
    cambio_significativo[~mask_valido] = False
    
    # Clasificar dirección del cambio
    direccion = np.zeros_like(z_score, dtype=np.int8)
    direccion[z_score < -umbral_z] = -1  # Muy por debajo de lo normal
    direccion[z_score > umbral_z] = 1    # Muy por encima de lo normal
    direccion[~mask_valido] = -128       # Nodata
    
    # Estadísticas
    pixeles_validos = np.sum(mask_valido)
    pixeles_anomalia_negativa = np.sum(direccion == -1)
    pixeles_anomalia_positiva = np.sum(direccion == 1)
    pixeles_normal = pixeles_validos - pixeles_anomalia_negativa - pixeles_anomalia_positiva
    
    # Hectáreas
    ha_anomalia_neg = pixeles_anomalia_negativa * 0.01
    ha_anomalia_pos = pixeles_anomalia_positiva * 0.01
    ha_normal = pixeles_normal * 0.01
    
    # Estadísticas de Z-score
    z_validos = z_score[mask_valido]
    
    stats_dict = {
        'metodo': 'Análisis Z-score',
        'pixeles_validos': pixeles_validos,
        'pixeles_anomalia_negativa': pixeles_anomalia_negativa,
        'pixeles_anomalia_positiva': pixeles_anomalia_positiva,
        'pixeles_normal': pixeles_normal,
        'pct_anomalia_negativa': 100 * pixeles_anomalia_negativa / pixeles_validos if pixeles_validos > 0 else 0,
        'pct_anomalia_positiva': 100 * pixeles_anomalia_positiva / pixeles_validos if pixeles_validos > 0 else 0,
        'pct_normal': 100 * pixeles_normal / pixeles_validos if pixeles_validos > 0 else 0,
        'ha_anomalia_negativa': ha_anomalia_neg,
        'ha_anomalia_positiva': ha_anomalia_pos,
        'ha_normal': ha_normal,
        'zscore_media': float(np.mean(z_validos)),
        'zscore_std': float(np.std(z_validos)),
        'zscore_min': float(np.min(z_validos)),
        'zscore_max': float(np.max(z_validos)),
        'umbral_utilizado': umbral_z
    }
    
    print(f"\n📊 Resultados:")
    print(f"   Píxeles analizados: {pixeles_validos:,}")
    print(f"\n   Anomalía negativa (Z < -{umbral_z}): {pixeles_anomalia_negativa:,} px ({stats_dict['pct_anomalia_negativa']:.2f}%) = {ha_anomalia_neg:.2f} ha")
    print(f"   Normal (|Z| ≤ {umbral_z}):           {pixeles_normal:,} px ({stats_dict['pct_normal']:.2f}%) = {ha_normal:.2f} ha")
    print(f"   Anomalía positiva (Z > +{umbral_z}): {pixeles_anomalia_positiva:,} px ({stats_dict['pct_anomalia_positiva']:.2f}%) = {ha_anomalia_pos:.2f} ha")
    print(f"\n   Z-score medio: {stats_dict['zscore_media']:+.4f}")
    print(f"   Rango Z: [{stats_dict['zscore_min']:+.4f}, {stats_dict['zscore_max']:+.4f}]")
    
    return z_score, cambio_significativo, direccion, stats_dict


def guardar_raster(array, ruta_salida, profile, banda_nombre="cambio", dtype='int8', nodata=-128):
    """
    Guarda un array como archivo GeoTIFF.
    """
    profile.update({
        'count': 1,
        'dtype': dtype,
        'nodata': nodata
    })
    
    with rasterio.open(ruta_salida, 'w', **profile) as dst:
        dst.write(array.astype(dtype), 1)
        dst.set_band_description(1, banda_nombre)
    
    print(f"   ✓ Guardado: {ruta_salida.name}")


def main():
    """
    Función principal: ejecuta los 3 métodos de detección de cambios.
    """
    
    # Rutas de archivos
    file_t1 = INPUT_DIR / f'indices_{YEAR_INICIO}.tif'
    file_t2 = INPUT_DIR / f'indices_{YEAR_FIN}.tif'
    
    # Verificar archivos
    if not file_t1.exists() or not file_t2.exists():
        print(f"❌ Error: No se encontraron los archivos de índices.")
        print(f"   Buscado: {file_t1}")
        print(f"   Buscado: {file_t2}")
        return
    
    # Almacenar estadísticas de todos los métodos
    todas_stats = []
    
    # =========================================================================
    # MÉTODO 1: Diferencia Simple
    # =========================================================================
    cambio_dif, diferencia, stats_dif = detectar_cambio_diferencia(
        file_t1, 
        file_t2, 
        umbral=UMBRALES['cambio_min']
    )
    
    # Guardar resultados Método 1
    with rasterio.open(file_t1) as src:
        profile = src.profile.copy()
    
    guardar_raster(
        cambio_dif, 
        OUTPUT_DIR / 'cambio_diferencia.tif', 
        profile, 
        banda_nombre=f'Diferencia_NDVI_{YEAR_INICIO}_{YEAR_FIN}',
        dtype='int8',
        nodata=-128
    )
    
    guardar_raster(
        diferencia, 
        OUTPUT_DIR / 'cambio_diferencia_continua.tif', 
        profile, 
        banda_nombre=f'Delta_NDVI_{YEAR_INICIO}_{YEAR_FIN}',
        dtype='float32',
        nodata=-9999
    )
    
    todas_stats.append(stats_dif)
    
    # =========================================================================
    # MÉTODO 2: Clasificación Multicriterio
    # =========================================================================
    clase, stats_multi = clasificar_cambio_urbano(file_t1, file_t2, UMBRALES)
    
    # Guardar resultados Método 2
    guardar_raster(
        clase, 
        OUTPUT_DIR / 'cambio_clasificado.tif', 
        profile, 
        banda_nombre=f'Clasificacion_Cambio_{YEAR_INICIO}_{YEAR_FIN}',
        dtype='uint8',
        nodata=255
    )
    
    todas_stats.append(stats_multi)
    
    # =========================================================================
    # MÉTODO 3: Análisis Z-score
    # =========================================================================
    rutas_serie = [INPUT_DIR / f'indices_{year}.tif' for year in YEARS_ALL]
    rutas_existentes = [r for r in rutas_serie if r.exists()]
    
    if len(rutas_existentes) >= 3:  # Necesitamos al menos 3 años para histórico
        z_score, cambio_sig, direccion, stats_z = analisis_zscore(rutas_existentes, indice_analisis=-1)
        
        # Guardar resultados Método 3
        guardar_raster(
            direccion, 
            OUTPUT_DIR / 'cambio_zscore.tif', 
            profile, 
            banda_nombre=f'Zscore_Direccion_{YEAR_FIN}',
            dtype='int8',
            nodata=-128
        )
        
        guardar_raster(
            z_score, 
            OUTPUT_DIR / 'cambio_zscore_valores.tif', 
            profile, 
            banda_nombre=f'Zscore_Valores_{YEAR_FIN}',
            dtype='float32',
            nodata=-9999
        )
        
        todas_stats.append(stats_z)
    else:
        print(f"\n⚠️  Advertencia: Se necesitan al menos 3 años para Z-score.")
        print(f"   Años disponibles: {len(rutas_existentes)}")
    
    # =========================================================================
    # RESUMEN FINAL Y EXPORTAR ESTADÍSTICAS
    # =========================================================================
    print("\n" + "="*70)
    print("📋 RESUMEN COMPARATIVO DE MÉTODOS")
    print("="*70)
    
    # Crear tabla comparativa
    comparacion = []
    for stats in todas_stats:
        if stats['metodo'] == 'Clasificación Multicriterio':
            # Extraer datos de urbanización (clase 1)
            for clase_info in stats['clases']:
                if clase_info['clase_id'] == 1:
                    comparacion.append({
                        'Método': stats['metodo'],
                        'Urbanización (ha)': clase_info['hectareas'],
                        'Pérdida Vegetación (ha)': next((c['hectareas'] for c in stats['clases'] if c['clase_id'] == 2), 0),
                        'Píxeles Analizados': stats['pixeles_validos']
                    })
                    break
        elif stats['metodo'] == 'Diferencia Simple':
            comparacion.append({
                'Método': stats['metodo'],
                'Urbanización (ha)': '-',
                'Pérdida Vegetación (ha)': stats['ha_perdida'],
                'Píxeles Analizados': stats['pixeles_validos']
            })
        elif stats['metodo'] == 'Análisis Z-score':
            comparacion.append({
                'Método': stats['metodo'],
                'Urbanización (ha)': '-',
                'Pérdida Vegetación (ha)': stats['ha_anomalia_negativa'],
                'Píxeles Analizados': stats['pixeles_validos']
            })
    
    df_comparacion = pd.DataFrame(comparacion)
    print("\n" + df_comparacion.to_string(index=False))
    
    # Exportar estadísticas detalladas a CSV
    csv_path = OUTPUT_DIR / 'estadisticas_cambios.csv'
    
    rows_export = []
    for stats in todas_stats:
        if stats['metodo'] == 'Clasificación Multicriterio':
            for clase_info in stats['clases']:
                rows_export.append({
                    'Método': stats['metodo'],
                    'Categoría': clase_info['nombre'],
                    'Píxeles': clase_info['pixeles'],
                    'Porcentaje': clase_info['porcentaje'],
                    'Hectáreas': clase_info['hectareas']
                })
        else:
            # Para otros métodos, resumir datos principales
            row = {'Método': stats['metodo']}
            for key, val in stats.items():
                if key != 'metodo' and key != 'clases':
                    row[key] = val
            rows_export.append(row)
    
    df_export = pd.DataFrame(rows_export)
    df_export.to_csv(csv_path, index=False)
    print(f"\n✓ Estadísticas exportadas: {csv_path.name}")
    
    # Resumen final
    print("\n" + "="*70)
    print("✅ FASE 3 COMPLETADA")
    print("="*70)
    print("\n📂 Archivos generados:")
    archivos_generados = [
        'cambio_diferencia.tif',
        'cambio_diferencia_continua.tif',
        'cambio_clasificado.tif',
        'cambio_zscore.tif',
        'cambio_zscore_valores.tif',
        'estadisticas_cambios.csv'
    ]
    
    for archivo in archivos_generados:
        ruta = OUTPUT_DIR / archivo
        if ruta.exists():
            size_mb = ruta.stat().st_size / (1024 * 1024)
            print(f"   ✓ {archivo} ({size_mb:.2f} MB)")
    
    print("\n🎯 Próximo paso: Fase 4 - Análisis Zonal por Unidades Administrativas")


if __name__ == '__main__':
    main()
