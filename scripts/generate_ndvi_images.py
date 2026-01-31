#!/usr/bin/env python3
"""
Script rápido para generar imágenes NDVI para el dashboard
Alternativa a ejecutar el notebook completo

Uso:
    python scripts/generate_ndvi_images.py
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Configuración
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'processed'
FIGURES_DIR = BASE_DIR / 'outputs' / 'figures'
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

YEARS = [2018, 2020, 2022, 2024]

def generate_ndvi_image(year):
    """Generar imagen NDVI para un año específico"""
    
    # Ruta del archivo de índices
    indices_file = DATA_DIR / f'indices_{year}.tif'
    
    if not indices_file.exists():
        print(f"   ⚠️  Archivo no encontrado: {indices_file}")
        return False
    
    try:
        # Leer banda NDVI (banda 1)
        with rasterio.open(indices_file) as src:
            ndvi = src.read(1)
            bounds = src.bounds
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Visualizar NDVI
        im = ax.imshow(ndvi, cmap='RdYlGn', vmin=-0.2, vmax=0.8,
                      extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
        
        # Configurar visualización
        ax.set_title(f'Índice de Vegetación (NDVI) - Peñaflor {year}', 
                    fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Longitud', fontsize=14)
        ax.set_ylabel('Latitud', fontsize=14)
        
        # Barra de color
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('NDVI', fontsize=14, fontweight='bold')
        cbar.ax.tick_params(labelsize=11)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Leyenda interpretativa
        legend_text = (
            'Valores NDVI:\n'
            '< 0.0: Agua/Suelo desnudo\n'
            '0.0-0.3: Vegetación escasa\n'
            '0.3-0.6: Vegetación moderada\n'
            '> 0.6: Vegetación densa'
        )
        ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
               fontsize=11, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.85,
                        edgecolor='black', linewidth=1))
        
        # Información del área
        area_text = f'Comuna de Peñaflor\n~202 km²'
        ax.text(0.98, 0.02, area_text, transform=ax.transAxes,
               fontsize=10, horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        plt.tight_layout()
        
        # Guardar imagen
        output_file = FIGURES_DIR / f'ndvi_{year}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Calcular estadísticas
        ndvi_valid = ndvi[(ndvi >= -1) & (ndvi <= 1)]
        ndvi_mean = np.mean(ndvi_valid)
        ndvi_std = np.std(ndvi_valid)
        veg_area_pct = np.sum(ndvi_valid > 0.3) / len(ndvi_valid) * 100
        
        print(f"   ✓ {year}: {output_file.name}")
        print(f"      NDVI medio: {ndvi_mean:.3f} ± {ndvi_std:.3f}")
        print(f"      Vegetación: {veg_area_pct:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error al procesar {year}: {e}")
        return False

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("   GENERACIÓN DE IMÁGENES NDVI PARA DASHBOARD")
    print("="*70)
    print(f"\n📂 Directorio de entrada: {DATA_DIR}")
    print(f"📂 Directorio de salida: {FIGURES_DIR}")
    print(f"\n🔄 Procesando {len(YEARS)} años...\n")
    
    success_count = 0
    
    for year in YEARS:
        if generate_ndvi_image(year):
            success_count += 1
        print()
    
    print("="*70)
    if success_count == len(YEARS):
        print(f"✅ ÉXITO: {success_count}/{len(YEARS)} imágenes generadas")
    else:
        print(f"⚠️  PARCIAL: {success_count}/{len(YEARS)} imágenes generadas")
    
    print(f"\n📁 Las imágenes están en: {FIGURES_DIR}")
    print("\n💡 Ahora puedes:")
    print("   1. Ejecutar el dashboard: streamlit run app/app.py")
    print("   2. Navegar a '🔍 Comparación Visual Antes/Después'")
    print("   3. Ver las imágenes NDVI generadas")
    print("="*70 + "\n")
    
    return success_count == len(YEARS)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
