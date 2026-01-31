"""
Script para crear animación GIF de la evolución de urbanización en Peñaflor
Fase 7 - Bonus 2: Animación Temporal

Este script:
1. Lee los archivos TIFF de índices espectrales (2018-2024)
2. Extrae la banda NDBI (Índice de Urbanización)
3. Genera cuadros temporales con visualización mejorada
4. Crea un GIF animado que muestra la evolución urbana
5. Opcionalmente genera también una animación comparativa NDVI vs NDBI

Autor: Byron Caices
Fecha: Enero 2026
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import rasterio
from rasterio.plot import show
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR = BASE_DIR / 'outputs' / 'figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Años disponibles
YEARS = ['2018', '2020', '2022', '2024']

def create_custom_colormap():
    """Crear colormap personalizado para NDBI (gris -> rojo)"""
    colors = [
        (0.1, 0.1, 0.1),      # Negro (no urbano)
        (0.3, 0.3, 0.3),      # Gris oscuro
        (0.6, 0.6, 0.6),      # Gris
        (0.9, 0.7, 0.3),      # Naranja
        (1.0, 0.3, 0.0),      # Rojo (urbano)
    ]
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('urban', colors, N=n_bins)
    return cmap

def read_ndbi_band(tif_path):
    """
    Leer banda NDBI de archivo TIFF
    
    Estructura de bandas según Fase 2:
    Banda 1: NDVI
    Banda 2: NDBI
    Banda 3: NDWI
    Banda 4: BSI
    """
    with rasterio.open(tif_path) as src:
        ndbi = src.read(2)  # Banda 2 = NDBI
        profile = src.profile
        bounds = src.bounds
        transform = src.transform
    
    # Enmascarar valores fuera de rango válido para NDBI (-1 a 1)
    ndbi = np.where((ndbi < -1) | (ndbi > 1), np.nan, ndbi)
    
    return ndbi, profile, bounds, transform

def read_ndvi_band(tif_path):
    """Leer banda NDVI"""
    with rasterio.open(tif_path) as src:
        ndvi = src.read(1)  # Banda 1 = NDVI
    
    ndvi = np.where((ndvi < -1) | (ndvi > 1), np.nan, ndvi)
    return ndvi

def create_frame(ndbi, year, bounds, title="Evolución de Urbanización - Peñaflor"):
    """Crear frame individual para el GIF"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Colormap personalizado
    cmap = create_custom_colormap()
    
    # Mostrar NDBI
    im = ax.imshow(ndbi, cmap=cmap, vmin=-0.3, vmax=0.4, 
                   extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    
    # Título grande
    ax.set_title(f'{title}\nAño {year}', 
                 fontsize=22, fontweight='bold', pad=20)
    
    # Barra de color
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('NDBI (Índice de Edificación)', fontsize=14, fontweight='bold')
    cbar.ax.tick_params(labelsize=11)
    
    # Etiquetas
    ax.set_xlabel('Longitud', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitud', fontsize=12, fontweight='bold')
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Leyenda explicativa
    legend_text = (
        'Valores NDBI:\n'
        '< 0.0: Vegetación/Agua\n'
        '0.0-0.2: Suelo mixto\n'
        '> 0.2: Área urbanizada'
    )
    ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Escala visual aproximada (si conoces el área)
    scale_text = f'Comuna de Peñaflor (~202 km²)'
    ax.text(0.98, 0.02, scale_text, transform=ax.transAxes,
            fontsize=9, horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    return fig

def create_comparison_frame(ndvi, ndbi, year, bounds):
    """Crear frame comparativo NDVI vs NDBI"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # NDVI (Vegetación)
    im1 = ax1.imshow(ndvi, cmap='RdYlGn', vmin=-0.2, vmax=0.8,
                     extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    ax1.set_title(f'NDVI (Vegetación) - {year}', fontsize=16, fontweight='bold')
    cbar1 = plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label('NDVI', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # NDBI (Urbanización)
    cmap_urban = create_custom_colormap()
    im2 = ax2.imshow(ndbi, cmap=cmap_urban, vmin=-0.3, vmax=0.4,
                     extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    ax2.set_title(f'NDBI (Urbanización) - {year}', fontsize=16, fontweight='bold')
    cbar2 = plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label('NDBI', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Título general
    fig.suptitle('Comparación: Pérdida de Vegetación vs Ganancia Urbana',
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    return fig

def save_frame(fig, temp_path):
    """Guardar frame como PNG temporal"""
    fig.savefig(temp_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)

def create_gif_with_imageio(frames, output_path, duration=1000):
    """Crear GIF usando imageio"""
    try:
        import imageio.v2 as imageio
    except ImportError:
        import imageio
    
    print(f"📦 Guardando GIF en: {output_path}")
    imageio.mimsave(output_path, frames, duration=duration, loop=0)

def create_gif_with_pillow(frame_paths, output_path, duration=1000):
    """Crear GIF usando PIL (alternativa)"""
    from PIL import Image
    
    frames = [Image.open(fp) for fp in frame_paths]
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=False
    )

def calculate_statistics(ndbi_data):
    """Calcular estadísticas del NDBI"""
    valid_data = ndbi_data[~np.isnan(ndbi_data)]
    urban_pixels = np.sum(valid_data > 0.2)
    total_pixels = len(valid_data)
    urban_percentage = (urban_pixels / total_pixels) * 100 if total_pixels > 0 else 0
    
    return {
        'mean': np.mean(valid_data),
        'std': np.std(valid_data),
        'urban_pixels': urban_pixels,
        'urban_percentage': urban_percentage
    }

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("   GENERACIÓN DE ANIMACIÓN TEMPORAL - URBANIZACIÓN PEÑAFLOR")
    print("="*70)
    
    # Verificar archivos disponibles
    print("\n📂 Verificando archivos de índices...")
    available_years = []
    for year in YEARS:
        tif_path = DATA_DIR / f'indices_{year}.tif'
        if tif_path.exists():
            available_years.append(year)
            print(f"   ✓ {year}: {tif_path.name}")
        else:
            print(f"   ✗ {year}: Archivo no encontrado")
    
    if len(available_years) < 2:
        print("\n❌ Error: Se necesitan al menos 2 años de datos para crear animación")
        return None
    
    print(f"\n✅ {len(available_years)} años disponibles para animación\n")
    
    # Método 1: GIF Principal (NDBI Evolution)
    print("🎬 Generando Animación 1: Evolución NDBI...")
    print("-" * 70)
    
    frames_ndbi = []
    temp_paths_ndbi = []
    stats_by_year = {}
    
    for year in available_years:
        print(f"   Procesando año {year}...")
        
        # Leer datos
        tif_path = DATA_DIR / f'indices_{year}.tif'
        ndbi, profile, bounds, transform = read_ndbi_band(tif_path)
        
        # Calcular estadísticas
        stats = calculate_statistics(ndbi)
        stats_by_year[year] = stats
        print(f"      NDBI medio: {stats['mean']:.3f} | Urbano: {stats['urban_percentage']:.2f}%")
        
        # Crear frame
        fig = create_frame(ndbi, year, bounds)
        
        # Guardar temporalmente
        temp_path = OUTPUT_DIR / f'temp_ndbi_{year}.png'
        save_frame(fig, temp_path)
        temp_paths_ndbi.append(temp_path)
        
        # Leer para GIF
        try:
            import imageio.v2 as imageio
        except ImportError:
            import imageio
        frames_ndbi.append(imageio.imread(temp_path))
    
    # Crear GIF principal
    gif_path_ndbi = OUTPUT_DIR / 'evolucion_urbanizacion_penaflor.gif'
    create_gif_with_imageio(frames_ndbi, gif_path_ndbi, duration=1200)
    print(f"\n   ✅ GIF principal creado: {gif_path_ndbi}")
    
    # Limpiar temporales
    for temp_path in temp_paths_ndbi:
        temp_path.unlink()
    
    # Método 2: GIF Comparativo (NDVI vs NDBI)
    print("\n🎬 Generando Animación 2: NDVI vs NDBI...")
    print("-" * 70)
    
    frames_comparison = []
    temp_paths_comparison = []
    
    for year in available_years:
        print(f"   Procesando comparación {year}...")
        
        tif_path = DATA_DIR / f'indices_{year}.tif'
        ndvi = read_ndvi_band(tif_path)
        ndbi, _, bounds, _ = read_ndbi_band(tif_path)
        
        # Crear frame comparativo
        fig = create_comparison_frame(ndvi, ndbi, year, bounds)
        
        # Guardar temporalmente
        temp_path = OUTPUT_DIR / f'temp_comp_{year}.png'
        save_frame(fig, temp_path)
        temp_paths_comparison.append(temp_path)
        
        # Leer para GIF
        try:
            import imageio.v2 as imageio
        except ImportError:
            import imageio
        frames_comparison.append(imageio.imread(temp_path))
    
    # Crear GIF comparativo
    gif_path_comparison = OUTPUT_DIR / 'comparacion_ndvi_ndbi.gif'
    create_gif_with_imageio(frames_comparison, gif_path_comparison, duration=1500)
    print(f"\n   ✅ GIF comparativo creado: {gif_path_comparison}")
    
    # Limpiar temporales
    for temp_path in temp_paths_comparison:
        temp_path.unlink()
    
    # Resumen de estadísticas
    print("\n" + "="*70)
    print("📊 RESUMEN DE EVOLUCIÓN TEMPORAL")
    print("="*70)
    print(f"\n{'Año':<8} {'NDBI Medio':<15} {'% Urbano':<15} {'Cambio vs anterior':<20}")
    print("-" * 70)
    
    prev_urban = None
    for year in available_years:
        stats = stats_by_year[year]
        change_text = ""
        if prev_urban is not None:
            change = stats['urban_percentage'] - prev_urban
            change_text = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
        
        print(f"{year:<8} {stats['mean']:>6.3f}{'':>9} {stats['urban_percentage']:>6.2f}%{'':>9} {change_text:<20}")
        prev_urban = stats['urban_percentage']
    
    # Calcular cambio total
    if len(available_years) >= 2:
        first_year = available_years[0]
        last_year = available_years[-1]
        total_change = stats_by_year[last_year]['urban_percentage'] - stats_by_year[first_year]['urban_percentage']
        years_span = int(last_year) - int(first_year)
        annual_rate = total_change / years_span if years_span > 0 else 0
        
        print("\n" + "-" * 70)
        print(f"Cambio total ({first_year}-{last_year}): +{total_change:.2f}%")
        print(f"Tasa anual de urbanización: +{annual_rate:.2f}%/año")
    
    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*70)
    print(f"\n📁 Archivos generados:")
    print(f"   1. {gif_path_ndbi.name} ({gif_path_ndbi.stat().st_size / 1024:.1f} KB)")
    print(f"   2. {gif_path_comparison.name} ({gif_path_comparison.stat().st_size / 1024:.1f} KB)")
    print(f"\n💡 Próximos pasos:")
    print(f"   - Incluir GIFs en el dashboard Streamlit (st.image())")
    print(f"   - Agregar al repositorio GitHub")
    print(f"   - Mencionar en sección de Resultados del informe")
    print("="*70 + "\n")
    
    return gif_path_ndbi, gif_path_comparison

if __name__ == "__main__":
    try:
        gif_ndbi, gif_comp = main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
