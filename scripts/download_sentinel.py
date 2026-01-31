"""
Script de Descarga de Imágenes Sentinel-2
Fase 1: Adquisición de Datos
Proyecto: Detección de Cambios Urbanos

Este script descarga imágenes Sentinel-2 desde Google Earth Engine
para los años especificados, aplicando máscaras de nubes y creando
compositos de mediana.

Método: Export.toDrive (exporta a Google Drive para descarga manual)
"""

import ee
import time
from pathlib import Path

# =============================================================================
# CONFIGURACIÓN - MODIFICAR SEGÚN TU ZONA DE ESTUDIO
# =============================================================================

# ID del proyecto de Google Cloud
GEE_PROJECT = 'cambio-urbano-peniaflor'

# Coordenadas del área de estudio: [Oeste, Sur, Este, Norte]
# Comuna de Peñaflor, Región Metropolitana, Chile
# Centro aprox: -33.61, -70.89 | Área: ~70 km²
ROI_COORDS = [-70.96, -33.68, -70.82, -33.54]

# Nombre de la zona (para documentación)
ZONE_NAME = "Peñaflor"

# Años a descargar (mínimo 4 fechas, período >= 5 años)
YEARS = [2018, 2020, 2022, 2024]

# Meses de verano para Chile (menos nubes, vegetación comparable)
START_MONTH = 1   # Enero
END_MONTH = 3     # Marzo
END_DAY = 15      # Hasta el 15 de marzo

# Porcentaje máximo de nubes permitido
MAX_CLOUD_PERCENT = 10

# =============================================================================
# FUNCIONES
# =============================================================================

def initialize_gee():
    """Inicializa Google Earth Engine."""
    try:
        ee.Initialize(project=GEE_PROJECT)
        print(f"✅ GEE inicializado con proyecto: {GEE_PROJECT}")
    except Exception as e:
        print(f"⚠️ Error al inicializar GEE: {e}")
        print("   Intentando autenticación...")
        ee.Authenticate()
        ee.Initialize(project=GEE_PROJECT)
        print(f"✅ GEE inicializado después de autenticación")


def mask_clouds_s2(image):
    """
    Enmascara nubes y cirrus en imágenes Sentinel-2 usando la banda QA60.
    (Método del profesor)
    
    Args:
        image: ee.Image de Sentinel-2
        
    Returns:
        ee.Image con nubes enmascaradas
    """
    qa = image.select('QA60')
    # Bit 10: nubes, Bit 11: cirrus
    cloud_mask = qa.bitwiseAnd(1 << 10).eq(0).And(
                 qa.bitwiseAnd(1 << 11).eq(0))
    return image.updateMask(cloud_mask)


def get_sentinel_collection(roi, year, max_clouds=10):
    """
    Obtiene la colección de Sentinel-2 filtrada para un año específico.
    
    Args:
        roi: ee.Geometry del área de estudio
        year: Año a procesar
        max_clouds: Porcentaje máximo de nubes
        
    Returns:
        Tuple (ee.ImageCollection, int) - colección filtrada y cantidad de imágenes
    """
    start_date = f'{year}-{START_MONTH:02d}-01'
    end_date = f'{year}-{END_MONTH:02d}-28'
    
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                  .filterBounds(roi)
                  .filterDate(start_date, end_date)
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_clouds)))
    
    count = collection.size().getInfo()
    return collection, count


def download_year(roi, year, max_clouds=10):
    """
    Crea y lanza la tarea de exportación para un año específico.
    
    Args:
        roi: ee.Geometry del área de estudio
        year: Año a procesar
        max_clouds: Porcentaje máximo de nubes inicial
        
    Returns:
        ee.batch.Task: Tarea de exportación
    """
    print(f"\n⏳ Procesando año {year}...")
    
    # Fechas de verano (Enero-Febrero)
    start_date = f'{year}-01-01'
    end_date = f'{year}-02-28'
    
    # Crear colección filtrada
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                  .filterBounds(roi)
                  .filterDate(start_date, end_date)
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_clouds))
                  .map(mask_clouds_s2))
    
    # Verificar cantidad de imágenes
    count = collection.size().getInfo()
    print(f"   📷 Imágenes encontradas (<{max_clouds}% nubes): {count}")
    
    if count == 0:
        print(f"   ⚠️ Probando con 20% de nubes...")
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(roi)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                      .map(mask_clouds_s2))
        count = collection.size().getInfo()
        print(f"   📷 Imágenes con 20% nubes: {count}")
    
    if count == 0:
        print(f"   ❌ Sin imágenes disponibles para {year}")
        return None
    
    # Crear composito de mediana y recortar
    composite = collection.median().clip(roi)
    
    # Seleccionar bandas para índices espectrales
    # B2=Blue, B3=Green, B4=Red, B8=NIR, B11=SWIR1, B12=SWIR2
    final_image = composite.select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
    
    # Configurar exportación a Google Drive
    task = ee.batch.Export.image.toDrive(
        image=final_image,
        description=f'sentinel2_{year}',
        folder='cambio_urbano_peniaflor',  # Carpeta en Google Drive
        fileNamePrefix=f'sentinel2_{year}',
        region=roi,
        scale=10,  # Resolución 10m
        maxPixels=1e9,
        fileFormat='GeoTIFF'
    )
    
    # Iniciar la tarea
    task.start()
    print(f"   ✅ Tarea de exportación iniciada: sentinel2_{year}")
    print(f"   📁 Se guardará en Google Drive/cambio_urbano_peniaflor/")
    
    return task


def main():
    """Función principal de descarga."""
    print("=" * 60)
    print("🛰️  DESCARGA DE IMÁGENES SENTINEL-2")
    print("    Fase 1: Adquisición de Datos")
    print("    Método: Export a Google Drive")
    print("=" * 60)
    
    # Inicializar GEE
    initialize_gee()
    
    # Crear geometría del área de estudio
    roi = ee.Geometry.Rectangle(ROI_COORDS)
    
    # Calcular área aproximada
    area_km2 = roi.area().divide(1e6).getInfo()
    print(f"\n📍 Zona de estudio: {ZONE_NAME}")
    print(f"   Coordenadas: {ROI_COORDS}")
    print(f"   Área aproximada: {area_km2:.1f} km²")
    print(f"📅 Años a procesar: {YEARS}")
    
    # Verificar que el área está en el rango recomendado
    if area_km2 < 100:
        print(f"\n⚠️ NOTA: El área ({area_km2:.1f} km²) es menor a 100 km²")
        print(f"   (La guía recomienda 100-500 km², pero Peñaflor es un caso específico)")
    
    # Lanzar tareas de exportación
    tasks = []
    for year in YEARS:
        task = download_year(roi, year, MAX_CLOUD_PERCENT)
        if task:
            tasks.append((year, task))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TAREAS")
    print("=" * 60)
    print(f"   Total de tareas iniciadas: {len(tasks)}/{len(YEARS)}")
    
    if len(tasks) > 0:
        print("\n🔄 Monitoreando estado de las tareas...")
        print("   (Esto puede tomar varios minutos)")
        
        # Esperar y mostrar progreso
        all_completed = False
        while not all_completed:
            time.sleep(10)  # Esperar 10 segundos entre verificaciones
            
            statuses = []
            for year, task in tasks:
                status = task.status()
                state = status['state']
                statuses.append((year, state))
                
                if state == 'COMPLETED':
                    icon = "✅"
                elif state == 'RUNNING':
                    icon = "⏳"
                elif state == 'READY':
                    icon = "🕐"
                elif state == 'FAILED':
                    icon = "❌"
                else:
                    icon = "❓"
                
                print(f"   {year}: {icon} {state}")
            
            # Verificar si todas terminaron
            all_completed = all([state in ['COMPLETED', 'FAILED', 'CANCELLED'] 
                               for _, state in statuses])
            
            if not all_completed:
                print("   Actualizando en 10 segundos...\n")
        
        # Resumen final
        completed = sum(1 for _, state in statuses if state == 'COMPLETED')
        failed = sum(1 for _, state in statuses if state == 'FAILED')
        
        print("\n" + "=" * 60)
        print("📊 RESULTADO FINAL")
        print("=" * 60)
        print(f"   ✅ Completadas: {completed}")
        print(f"   ❌ Fallidas: {failed}")
        
        if completed == len(YEARS):
            print("\n🎉 ¡Todas las exportaciones completadas!")
            print("\n📥 PRÓXIMOS PASOS:")
            print("   1. Ve a Google Drive/cambio_urbano_peniaflor/")
            print("   2. Descarga los archivos .tif")
            print("   3. Muévelos a la carpeta data/raw/ del proyecto")
            print("   4. Continúa con la Fase 2: Cálculo de Índices")
        else:
            print("\n⚠️ Algunas exportaciones fallaron.")
            print("   Revisa los errores en la consola de Google Earth Engine:")
            print("   https://code.earthengine.google.com/tasks")
    else:
        print("\n❌ No se pudieron iniciar las tareas de exportación")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
