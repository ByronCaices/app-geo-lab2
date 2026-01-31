"""
Script para exportar hotspots de urbanización a GeoJSON para validación en ArcGIS Online
Fase 7 - Bonus 1: Validación Visual con Imágenes de Alta Resolución

Este script:
1. Carga las zonas con datos del análisis zonal
2. Filtra los Top 20 hotspots por urbanización
3. Exporta a GeoJSON optimizado para visualización web
4. Genera estadísticas básicas para la validación

Autor: Byron Caices
Fecha: Enero 2026
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import json

# Configuración de rutas
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
VECTOR_DIR = DATA_DIR / 'vector'
PROCESSED_DIR = DATA_DIR / 'processed'
OUTPUT_FILE = PROCESSED_DIR / 'validacion_hotspots.geojson'

def load_zones():
    """Cargar zonas con datos del análisis zonal"""
    print("📂 Cargando zonas con datos...")
    zones_file = VECTOR_DIR / 'zonas_con_datos.gpkg'
    
    if not zones_file.exists():
        raise FileNotFoundError(f"No se encuentra el archivo: {zones_file}")
    
    zones = gpd.read_file(zones_file)
    print(f"   ✓ Cargadas {len(zones)} zonas")
    return zones

def filter_top_hotspots(zones, top_n=20, method='urbanizacion_ha'):
    """
    Filtrar los principales hotspots de urbanización
    
    Parameters:
    -----------
    zones : GeoDataFrame
        Zonas con datos
    top_n : int
        Número de hotspots a extraer
    method : str
        Criterio de ordenamiento ('urbanizacion_ha', 'indice_transformacion', 'cambio_ndbi')
    """
    print(f"\n🔍 Filtrando Top {top_n} hotspots por {method}...")
    
    # Verificar columnas disponibles
    available_cols = zones.columns.tolist()
    print(f"   Columnas disponibles: {[c for c in available_cols if 'urban' in c.lower() or 'indice' in c.lower()]}")
    
    # Ordenar por el criterio seleccionado
    if method in zones.columns:
        hotspots = zones.sort_values(method, ascending=False).head(top_n).copy()
    else:
        # Fallback: buscar columna similar
        urban_cols = [c for c in zones.columns if 'urban' in c.lower() or 'cambio' in c.lower()]
        if urban_cols:
            method = urban_cols[0]
            print(f"   ⚠️  Usando columna alternativa: {method}")
            hotspots = zones.sort_values(method, ascending=False).head(top_n).copy()
        else:
            print("   ⚠️  No se encontró columna de ordenamiento, usando todas las zonas")
            hotspots = zones.head(top_n).copy()
    
    print(f"   ✓ Seleccionados {len(hotspots)} hotspots")
    return hotspots, method

def prepare_for_web(hotspots):
    """
    Preparar datos para visualización web en ArcGIS
    - Simplificar geometrías
    - Renombrar columnas a nombres amigables
    - Redondear valores numéricos
    """
    print("\n🌐 Preparando datos para web...")
    
    # Simplificar geometrías (tolerancia de 5 metros)
    hotspots['geometry'] = hotspots.geometry.simplify(tolerance=5)
    
    # Crear columnas limpias para visualización
    hotspots_clean = hotspots.copy()
    
    # Renombrar columnas comunes
    rename_map = {
        'zona_id': 'ID_Zona',
        'urbanizacion_ha': 'Urbanizacion_ha',
        'perdida_veg_ha': 'Perdida_Veg_ha',
        'cambio_ndbi': 'Cambio_NDBI',
        'indice_transformacion': 'Indice_Transf'
    }
    
    for old, new in rename_map.items():
        if old in hotspots_clean.columns:
            hotspots_clean = hotspots_clean.rename(columns={old: new})
    
    # Redondear valores numéricos a 2 decimales
    numeric_cols = hotspots_clean.select_dtypes(include=['float64', 'float32']).columns
    for col in numeric_cols:
        hotspots_clean[col] = hotspots_clean[col].round(2)
    
    print(f"   ✓ Datos preparados con {len(hotspots_clean.columns)} columnas")
    return hotspots_clean

def export_to_geojson(hotspots, output_file):
    """Exportar a GeoJSON con configuración optimizada"""
    print(f"\n💾 Exportando a GeoJSON...")
    
    # Asegurar que el directorio existe
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Exportar con precisión de 6 decimales (suficiente para ~10cm)
    hotspots.to_file(
        output_file, 
        driver='GeoJSON',
        encoding='utf-8'
    )
    
    # Calcular tamaño del archivo
    file_size = output_file.stat().st_size / 1024  # KB
    print(f"   ✓ Archivo exportado: {output_file}")
    print(f"   ✓ Tamaño: {file_size:.1f} KB")
    
    return output_file

def generate_validation_template(hotspots, output_dir):
    """Generar plantilla CSV para validación manual"""
    print("\n📋 Generando plantilla de validación...")
    
    # Extraer columnas clave
    if 'ID_Zona' in hotspots.columns:
        zona_col = 'ID_Zona'
    elif 'zona_id' in hotspots.columns:
        zona_col = 'zona_id'
    else:
        zona_col = hotspots.columns[0]
    
    # Obtener centroide de cada zona para facilitar navegación
    centroids = hotspots.geometry.centroid
    
    validation_data = {
        'ID_Zona': hotspots[zona_col].values,
        'Lat_Centro': centroids.y.round(6).values,
        'Lon_Centro': centroids.x.round(6).values,
        'Clasificacion_Python': ['Urbanización'] * len(hotspots),
        'Observacion_Visual_ArcGIS': [''] * len(hotspots),
        'Coincide': [''] * len(hotspots),
        'Comentarios': [''] * len(hotspots)
    }
    
    # Agregar métricas si están disponibles
    for col in ['Urbanizacion_ha', 'Indice_Transf']:
        if col in hotspots.columns:
            validation_data[col] = hotspots[col].values
    
    validation_df = pd.DataFrame(validation_data)
    
    # Exportar
    output_file = output_dir / 'plantilla_validacion_arcgis.csv'
    validation_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"   ✓ Plantilla generada: {output_file}")
    return validation_df

def generate_statistics(hotspots, method):
    """Generar estadísticas descriptivas de los hotspots"""
    print("\n📊 Estadísticas de hotspots seleccionados:")
    print("=" * 60)
    
    # Estadísticas por columna numérica
    numeric_cols = hotspots.select_dtypes(include=['float64', 'float32', 'int64']).columns
    
    for col in numeric_cols[:5]:  # Primeras 5 columnas numéricas
        if col in hotspots.columns:
            values = hotspots[col]
            print(f"\n{col}:")
            print(f"   Media: {values.mean():.2f}")
            print(f"   Mediana: {values.median():.2f}")
            print(f"   Min: {values.min():.2f}")
            print(f"   Max: {values.max():.2f}")
    
    print("\n" + "=" * 60)

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("   EXPORTACIÓN DE HOTSPOTS PARA VALIDACIÓN EN ArcGIS ONLINE")
    print("="*60)
    
    try:
        # 1. Cargar zonas
        zones = load_zones()
        
        # 2. Filtrar top hotspots
        hotspots, method_used = filter_top_hotspots(zones, top_n=20)
        
        # 3. Preparar para web
        hotspots_web = prepare_for_web(hotspots)
        
        # 4. Exportar a GeoJSON
        output_file = export_to_geojson(hotspots_web, OUTPUT_FILE)
        
        # 5. Generar plantilla de validación
        validation_df = generate_validation_template(hotspots_web, PROCESSED_DIR)
        
        # 6. Mostrar estadísticas
        generate_statistics(hotspots_web, method_used)
        
        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("="*60)
        print(f"\n📁 Archivos generados:")
        print(f"   1. GeoJSON: {output_file}")
        print(f"   2. Plantilla CSV: {PROCESSED_DIR / 'plantilla_validacion_arcgis.csv'}")
        print(f"\n📝 Próximos pasos:")
        print(f"   1. Abre ArcGIS Online: geo-usach.maps.arcgis.com")
        print(f"   2. En Map Viewer, selecciona 'Agregar' > 'Agregar capa desde archivo'")
        print(f"   3. Sube el archivo: {output_file.name}")
        print(f"   4. Agrega capa 'World Imagery Wayback' para comparación temporal")
        print(f"   5. Completa la plantilla CSV durante la validación visual")
        print("="*60 + "\n")
        
        return output_file, validation_df
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    output_file, validation_df = main()
