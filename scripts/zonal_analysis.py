#!/usr/bin/env python3
"""
Script de Análisis Zonal - Fase 4
==================================
Cuantifica cambios urbanos por zonas geográficas mediante:
1. Creación de grilla de análisis espacial
2. Estadísticas zonales de cambios por zona
3. Análisis temporal de evolución de índices
4. Identificación de hotspots de urbanización
5. Generación de mapas y tablas para dashboard

Autor: Byron Caices
Fecha: Enero 2025
Universidad de Santiago de Chile
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from pathlib import Path
from shapely.geometry import box
from rasterstats import zonal_stats
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial import distance
from scipy.ndimage import label
import glob

# Configuración
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR_PROC = BASE_DIR / 'data' / 'processed'
INPUT_DIR_RAW = BASE_DIR / 'data' / 'raw'
OUTPUT_DIR_VEC = BASE_DIR / 'data' / 'vector'
OUTPUT_DIR_FIG = BASE_DIR / 'outputs' / 'figures'

# Crear carpetas si no existen
OUTPUT_DIR_VEC.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR_FIG.mkdir(parents=True, exist_ok=True)

# Configuración de visualización
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['figure.dpi'] = 100
sns.set_palette("husl")

# Mapeo de clases de cambio
CLASES_CAMBIO = {
    0: 'Sin cambio',
    1: 'Urbanización',
    2: 'Pérdida vegetación',
    3: 'Ganancia vegetación',
    4: 'Nuevo cuerpo agua',
    5: 'Pérdida agua'
}

# Conversión de píxel a hectáreas (Sentinel-2: 10m × 10m = 100 m² = 0.01 ha)
PIXEL_AREA_HA = 0.01

print("="*70)
print("📊  ANÁLISIS ZONAL DE CAMBIOS URBANOS")
print("    Fase 4: Cuantificación por Zonas")
print("="*70)
print()


def crear_grilla_analisis(ruta_raster, salida_vector, n_cells_x=10, n_cells_y=10):
    """
    Crea una grilla de análisis sobre el área de estudio.
    
    Esta grilla simula unidades administrativas (barrios/distritos) cuando no se
    dispone de shapefiles censales oficiales. Cada celda representa una zona de análisis.
    
    Parámetros:
    -----------
    ruta_raster : Path
        Ruta a un archivo raster de referencia (para obtener extensión y CRS)
    salida_vector : Path
        Ruta donde guardar la grilla (formato GeoPackage)
    n_cells_x : int
        Número de celdas en dirección X (este-oeste)
    n_cells_y : int
        Número de celdas en dirección Y (norte-sur)
        
    Retorna:
    --------
    gdf : GeoDataFrame
        Grilla de análisis con geometrías y zona_id
    """
    
    print("="*70)
    print("PASO 1: CREACIÓN DE GRILLA DE ANÁLISIS")
    print("="*70)
    
    with rasterio.open(ruta_raster) as src:
        bounds = src.bounds  # (xmin, ymin, xmax, ymax)
        crs = src.crs
        
    xmin, ymin, xmax, ymax = bounds
    
    # Calcular tamaño de celda
    cell_width = (xmax - xmin) / n_cells_x
    cell_height = (ymax - ymin) / n_cells_y
    
    print(f"\n📐 Parámetros de grilla:")
    print(f"   Extensión: [{xmin:.2f}, {ymin:.2f}, {xmax:.2f}, {ymax:.2f}]")
    print(f"   CRS: {crs}")
    print(f"   Celdas: {n_cells_x} × {n_cells_y} = {n_cells_x * n_cells_y} zonas")
    print(f"   Tamaño celda: {cell_width:.2f}m × {cell_height:.2f}m")
    print(f"   Área celda: {(cell_width * cell_height) / 10000:.2f} ha")
    
    # Crear geometrías de celda
    grid_cells = []
    zona_ids = []
    zona_x = []
    zona_y = []
    
    for i in range(n_cells_x):
        for j in range(n_cells_y):
            x1 = xmin + i * cell_width
            y1 = ymin + j * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            
            grid_cells.append(box(x1, y1, x2, y2))
            zona_ids.append(f"Z_{i:02d}_{j:02d}")
            zona_x.append(i)
            zona_y.append(j)
    
    # Crear GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'zona_id': zona_ids,
        'zona_x': zona_x,
        'zona_y': zona_y,
        'geometry': grid_cells
    }, crs=crs)
    
    # Calcular área de cada zona (en hectáreas)
    gdf['area_ha'] = gdf.geometry.area / 10000
    
    # Guardar
    gdf.to_file(salida_vector, driver='GPKG')
    
    print(f"\n✓ Grilla creada: {len(gdf)} zonas")
    print(f"✓ Guardada en: {salida_vector.name}")
    
    return gdf


def analisis_zonal_cambios(ruta_cambios, gdf_zonas, columna_zona='zona_id'):
    """
    Calcula estadísticas de cambio por zona usando análisis zonal.
    
    Parámetros:
    -----------
    ruta_cambios : Path
        Ruta al raster de cambios clasificados (cambio_clasificado.tif)
    gdf_zonas : GeoDataFrame
        Polígonos de zonas de análisis
    columna_zona : str
        Nombre de la columna con identificador de zona
        
    Retorna:
    --------
    gdf_zonas : GeoDataFrame
        Zonas actualizadas con estadísticas de cambio
    """
    
    print("\n" + "="*70)
    print("PASO 2: ANÁLISIS ZONAL DE CAMBIOS")
    print("="*70)
    
    print(f"\n📊 Calculando estadísticas para {len(gdf_zonas)} zonas...")
    
    # Realizar estadísticas zonales categóricas
    stats = zonal_stats(
        gdf_zonas,
        str(ruta_cambios),
        stats=['count', 'sum', 'mean'],
        categorical=True,
        all_touched=True,
        nodata=255
    )
    
    # Convertir a DataFrame
    df_stats = pd.DataFrame(stats)
    
    # Asegurar que todas las clases existan (rellenar con 0 si no hay datos)
    for clase_id in CLASES_CAMBIO.keys():
        if clase_id not in df_stats.columns:
            df_stats[clase_id] = 0
    
    # Calcular píxeles totales válidos por zona
    df_stats['pixeles_validos'] = df_stats['count']
    
    # Calcular hectáreas por clase
    for clase_id, clase_nombre in CLASES_CAMBIO.items():
        # Normalizar nombre (sin tildes para columnas)
        col_name = (clase_nombre
                    .lower()
                    .replace('á', 'a')
                    .replace('é', 'e')
                    .replace('í', 'i')
                    .replace('ó', 'o')
                    .replace('ú', 'u')
                    .replace(' ', '_'))
        
        # DEBUG: Verificar si columna ya existe y eliminarla
        for suffix in ['_px', '_ha', '_pct']:
            col_full = f'{col_name}{suffix}'
            if col_full in gdf_zonas.columns:
                gdf_zonas = gdf_zonas.drop(columns=col_full)
        
        # Píxeles
        gdf_zonas[f'{col_name}_px'] = df_stats[clase_id].fillna(0).astype(int)
        
        # Hectáreas
        gdf_zonas[f'{col_name}_ha'] = gdf_zonas[f'{col_name}_px'] * PIXEL_AREA_HA
        
        # Porcentaje
        gdf_zonas[f'{col_name}_pct'] = (
            100 * gdf_zonas[f'{col_name}_px'] / df_stats['pixeles_validos']
        ).fillna(0)
    
    # Calcular métricas agregadas
    gdf_zonas['pixeles_validos'] = df_stats['pixeles_validos'].fillna(0).astype(int)
    gdf_zonas['cambio_total_ha'] = (
        gdf_zonas['urbanizacion_ha'] + 
        gdf_zonas['perdida_vegetacion_ha'] +
        gdf_zonas['ganancia_vegetacion_ha']
    )
    gdf_zonas['cambio_total_pct'] = (
        100 * gdf_zonas['cambio_total_ha'] / gdf_zonas['area_ha']
    ).fillna(0)
    
    # Calcular índice de transformación (urbanización + pérdida veg - ganancia veg)
    gdf_zonas['indice_transformacion'] = (
        gdf_zonas['urbanizacion_ha'] + 
        gdf_zonas['perdida_vegetacion_ha'] -
        gdf_zonas['ganancia_vegetacion_ha']
    )
    
    print(f"\n📈 Resumen Global:")
    print(f"   Total urbanización:        {gdf_zonas['urbanizacion_ha'].sum():8.2f} ha")
    print(f"   Total pérdida vegetación:  {gdf_zonas['perdida_vegetacion_ha'].sum():8.2f} ha")
    print(f"   Total ganancia vegetación: {gdf_zonas['ganancia_vegetacion_ha'].sum():8.2f} ha")
    print(f"   Cambio neto vegetación:    {(gdf_zonas['ganancia_vegetacion_ha'].sum() - gdf_zonas['perdida_vegetacion_ha'].sum()):8.2f} ha")
    
    return gdf_zonas


def identificar_hotspots(gdf_zonas, columna_metrica, top_n=10):
    """
    Identifica zonas con mayor intensidad de cambio (hotspots).
    
    Parámetros:
    -----------
    gdf_zonas : GeoDataFrame
        Zonas con estadísticas de cambio
    columna_metrica : str
        Columna a usar para ranking
    top_n : int
        Número de zonas top a retornar
        
    Retorna:
    --------
    df_ranking : DataFrame
        Ranking de zonas con mayor cambio
    """
    
    print("\n" + "="*70)
    print("PASO 3: IDENTIFICACIÓN DE HOTSPOTS")
    print("="*70)
    
    # Crear ranking usando loc para evitar duplicación
    columnas_seleccionar = [
        'zona_id', 
        columna_metrica,
        'urbanizacion_ha',
        'perdida_vegetacion_ha',
        'ganancia_vegetacion_ha',
        'cambio_total_ha',
        'indice_transformacion'
    ]
    
    # Asegurar que no haya duplicados en la lista
    columnas_seleccionar = list(dict.fromkeys(columnas_seleccionar))
    
    df_ranking = gdf_zonas[columnas_seleccionar].copy().sort_values(
        columna_metrica, ascending=False
    ).head(top_n)
    
    print(f"\n🔥 Top {top_n} zonas con mayor {columna_metrica.replace('_', ' ')}:")
    print("="*70)
    
    for idx, row in df_ranking.iterrows():
        print(f"   {row['zona_id']}: {row[columna_metrica]:.2f} ha")
    
    return df_ranking


def analisis_temporal(patron_archivos, fechas=None):
    """
    Analiza la evolución temporal de índices espectrales.
    
    Parámetros:
    -----------
    patron_archivos : str
        Patrón glob para buscar archivos de índices (ej: 'indices_*.tif')
    fechas : list
        Lista de fechas correspondientes (opcional, se extraen del nombre)
        
    Retorna:
    --------
    df_temporal : DataFrame
        Serie temporal con estadísticas de índices
    """
    
    print("\n" + "="*70)
    print("PASO 4: ANÁLISIS TEMPORAL")
    print("="*70)
    
    # Buscar archivos
    archivos = sorted(glob.glob(str(INPUT_DIR_PROC / patron_archivos)))
    
    if len(archivos) == 0:
        print(f"⚠️  No se encontraron archivos con patrón: {patron_archivos}")
        return None
    
    print(f"\n📅 Procesando {len(archivos)} años...")
    
    resultados = []
    
    for archivo in archivos:
        # Extraer año del nombre (ej: indices_2018.tif)
        nombre = Path(archivo).stem
        year = nombre.split('_')[-1]
        
        with rasterio.open(archivo) as src:
            # Leer índices
            ndvi = src.read(1).astype(np.float32)
            ndbi = src.read(2).astype(np.float32)
            ndwi = src.read(3).astype(np.float32)
            bsi = src.read(4).astype(np.float32)
            
            # Aplicar máscara de nodata
            mask_valido = ndvi != -9999
            
            # Calcular estadísticas
            stats = {
                'fecha': int(year),
                'ndvi_mean': float(np.nanmean(ndvi[mask_valido])),
                'ndvi_std': float(np.nanstd(ndvi[mask_valido])),
                'ndbi_mean': float(np.nanmean(ndbi[mask_valido])),
                'ndbi_std': float(np.nanstd(ndbi[mask_valido])),
                'ndwi_mean': float(np.nanmean(ndwi[mask_valido])),
                'bsi_mean': float(np.nanmean(bsi[mask_valido])),
                # Porcentajes
                'pct_vegetacion': float(100 * np.sum((ndvi > 0.3) & mask_valido) / np.sum(mask_valido)),
                'pct_urbano': float(100 * np.sum((ndbi > 0) & mask_valido) / np.sum(mask_valido)),
                'pct_agua': float(100 * np.sum((ndwi > 0.1) & mask_valido) / np.sum(mask_valido)),
            }
            
            resultados.append(stats)
            
            print(f"   {year}: NDVI={stats['ndvi_mean']:.3f}, "
                  f"NDBI={stats['ndbi_mean']:.3f}, "
                  f"Urbano={stats['pct_urbano']:.1f}%")
    
    df_temporal = pd.DataFrame(resultados)
    
    return df_temporal


def generar_mapas_coropleticos(gdf_zonas, columnas_mapear, output_dir):
    """
    Genera mapas coropléticos de intensidad de cambio.
    
    Parámetros:
    -----------
    gdf_zonas : GeoDataFrame
        Zonas con estadísticas de cambio
    columnas_mapear : list
        Lista de columnas a mapear
    output_dir : Path
        Directorio donde guardar mapas
    """
    
    print("\n" + "="*70)
    print("PASO 5: GENERACIÓN DE MAPAS COROPLÉTICOS")
    print("="*70)
    
    n_mapas = len(columnas_mapear)
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    axes = axes.flatten()
    
    for idx, columna in enumerate(columnas_mapear):
        ax = axes[idx]
        
        # Mapa coroplético
        gdf_zonas.plot(
            column=columna,
            cmap='YlOrRd',
            legend=True,
            ax=ax,
            edgecolor='black',
            linewidth=0.5,
            legend_kwds={'label': columna.replace('_', ' ').title(), 'shrink': 0.8}
        )
        
        ax.set_title(f"{columna.replace('_', ' ').title()}", fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitud')
        ax.set_ylabel('Latitud')
        ax.grid(True, alpha=0.3)
    
    # Ocultar ejes sobrantes
    for idx in range(n_mapas, len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle('Mapas de Intensidad de Cambio por Zona - Peñaflor 2018-2024', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = output_dir / 'mapas_coropleticos.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Mapas guardados en: {output_path.name}")
    
    plt.close()


def generar_graficos_temporales(df_temporal, output_dir):
    """
    Genera gráficos de evolución temporal de índices.
    
    Parámetros:
    -----------
    df_temporal : DataFrame
        Serie temporal con estadísticas
    output_dir : Path
        Directorio donde guardar gráficos
    """
    
    if df_temporal is None:
        print("\n⚠️  No hay datos temporales para graficar")
        return
    
    print("\n" + "="*70)
    print("PASO 6: GENERACIÓN DE GRÁFICOS TEMPORALES")
    print("="*70)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # NDVI temporal
    axes[0, 0].errorbar(
        df_temporal['fecha'], 
        df_temporal['ndvi_mean'], 
        yerr=df_temporal['ndvi_std'],
        marker='o', 
        capsize=5, 
        linewidth=2,
        color='green'
    )
    axes[0, 0].set_ylabel('NDVI medio ± σ', fontweight='bold')
    axes[0, 0].set_title('Evolución del NDVI', fontsize=14, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_xlabel('Año')
    
    # NDBI temporal
    axes[0, 1].errorbar(
        df_temporal['fecha'], 
        df_temporal['ndbi_mean'], 
        yerr=df_temporal['ndbi_std'],
        marker='s', 
        capsize=5, 
        linewidth=2,
        color='brown'
    )
    axes[0, 1].set_ylabel('NDBI medio ± σ', fontweight='bold')
    axes[0, 1].set_title('Evolución del NDBI', fontsize=14, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_xlabel('Año')
    
    # Porcentaje vegetación
    axes[1, 0].bar(
        df_temporal['fecha'], 
        df_temporal['pct_vegetacion'], 
        color='green', 
        alpha=0.7,
        edgecolor='black'
    )
    axes[1, 0].set_ylabel('% Área con vegetación', fontweight='bold')
    axes[1, 0].set_title('Cobertura de Vegetación', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Año')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Porcentaje urbano
    axes[1, 1].bar(
        df_temporal['fecha'], 
        df_temporal['pct_urbano'], 
        color='gray', 
        alpha=0.7,
        edgecolor='black'
    )
    axes[1, 1].set_ylabel('% Área urbana', fontweight='bold')
    axes[1, 1].set_title('Cobertura Urbana', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Año')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Evolución Temporal de Índices - Peñaflor 2018-2024', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = output_dir / 'evolucion_temporal.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Gráficos guardados en: {output_path.name}")
    
    plt.close()


def main():
    """
    Función principal: ejecuta análisis zonal completo.
    """
    
    # Rutas de archivos
    ruta_cambios = INPUT_DIR_PROC / 'cambio_clasificado.tif'
    ruta_grilla = OUTPUT_DIR_VEC / 'grilla_zonas.gpkg'
    
    # Verificar archivo de cambios
    if not ruta_cambios.exists():
        print(f"❌ Error: No se encontró {ruta_cambios}")
        print("   Ejecuta primero: python scripts/detect_changes.py")
        return
    
    # PASO 1: Crear o cargar grilla
    if not ruta_grilla.exists():
        gdf_zonas = crear_grilla_analisis(
            ruta_cambios, 
            ruta_grilla, 
            n_cells_x=10, 
            n_cells_y=10
        )
    else:
        print("="*70)
        print("PASO 1: CARGANDO GRILLA EXISTENTE")
        print("="*70)
        gdf_zonas = gpd.read_file(ruta_grilla)
        print(f"\n✓ Grilla cargada: {len(gdf_zonas)} zonas desde {ruta_grilla.name}")
    
    # PASO 2: Análisis zonal de cambios
    gdf_zonas = analisis_zonal_cambios(ruta_cambios, gdf_zonas)
    
    # PASO 3: Identificar hotspots
    df_ranking_urb = identificar_hotspots(gdf_zonas, 'urbanizacion_ha', top_n=10)
    df_ranking_trans = identificar_hotspots(gdf_zonas, 'indice_transformacion', top_n=10)
    
    # PASO 4: Análisis temporal
    df_temporal = analisis_temporal('indices_*.tif')
    
    # PASO 5: Mapas coropléticos
    columnas_mapear = [
        'urbanizacion_ha',
        'perdida_vegetacion_ha',
        'ganancia_vegetacion_ha',
        'cambio_total_pct'
    ]
    generar_mapas_coropleticos(gdf_zonas, columnas_mapear, OUTPUT_DIR_FIG)
    
    # PASO 6: Gráficos temporales
    if df_temporal is not None:
        generar_graficos_temporales(df_temporal, OUTPUT_DIR_FIG)
    
    # EXPORTAR DATOS
    print("\n" + "="*70)
    print("EXPORTACIÓN DE RESULTADOS")
    print("="*70)
    
    # 1. Zonas con datos (GeoPackage)
    ruta_zonas_datos = OUTPUT_DIR_VEC / 'zonas_con_datos.gpkg'
    gdf_zonas.to_file(ruta_zonas_datos, driver='GPKG')
    print(f"\n✓ Zonas con datos: {ruta_zonas_datos.name}")
    
    # 2. Estadísticas zonales (CSV)
    ruta_stats_csv = INPUT_DIR_PROC / 'estadisticas_zonales.csv'
    df_export = gdf_zonas.drop(columns='geometry')
    df_export.to_csv(ruta_stats_csv, index=False)
    print(f"✓ Estadísticas zonales: {ruta_stats_csv.name}")
    
    # 3. Ranking de zonas (CSV)
    ruta_ranking = INPUT_DIR_PROC / 'ranking_zonas.csv'
    df_ranking_urb.to_csv(ruta_ranking, index=False)
    print(f"✓ Ranking zonas: {ruta_ranking.name}")
    
    # 4. Evolución temporal (CSV)
    if df_temporal is not None:
        ruta_temporal_csv = INPUT_DIR_PROC / 'evolucion_temporal.csv'
        df_temporal.to_csv(ruta_temporal_csv, index=False)
        print(f"✓ Evolución temporal: {ruta_temporal_csv.name}")
    
    # RESUMEN FINAL
    print("\n" + "="*70)
    print("✅ FASE 4 COMPLETADA")
    print("="*70)
    
    print(f"\n📊 Resumen de Resultados:")
    print(f"   Zonas analizadas: {len(gdf_zonas)}")
    print(f"   Urbanización total: {gdf_zonas['urbanizacion_ha'].sum():.2f} ha")
    print(f"   Pérdida vegetación: {gdf_zonas['perdida_vegetacion_ha'].sum():.2f} ha")
    print(f"   Ganancia vegetación: {gdf_zonas['ganancia_vegetacion_ha'].sum():.2f} ha")
    
    print(f"\n📁 Archivos generados:")
    archivos = [
        ruta_grilla,
        ruta_zonas_datos,
        ruta_stats_csv,
        ruta_ranking,
        OUTPUT_DIR_FIG / 'mapas_coropleticos.png',
        OUTPUT_DIR_FIG / 'evolucion_temporal.png'
    ]
    
    for archivo in archivos:
        if archivo.exists():
            size_mb = archivo.stat().st_size / (1024 * 1024)
            print(f"   ✓ {archivo.name} ({size_mb:.2f} MB)")
    
    print(f"\n🎯 Próximo paso: Fase 5 - Dashboard Streamlit")


if __name__ == '__main__':
    main()
