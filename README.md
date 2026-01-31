# 🛰️ Detección de Cambios Urbanos - Peñaflor

**Laboratorio de Desarrollo de Aplicaciones Geoinformáticas**  
Universidad de Santiago de Chile

## 📋 Descripción

Sistema completo para la detección, cuantificación y visualización de cambios urbanos en la comuna de **Peñaflor** (2018-2024) utilizando series temporales de imágenes satelitales Sentinel-2 y Google Earth Engine.

## 📍 Zona de Estudio

**Comuna:** Peñaflor, Región Metropolitana, Chile  
**Coordenadas:** -33.61°S, -70.89°W  
**Área:** ~202 km²  
**Periodo:** 2018 - 2024  
**Imágenes:** 4 composiciones temporales (enero-febrero)

## 🎯 Objetivos

- ✅ Adquirir y procesar series temporales de imágenes Sentinel-2 (Fase 1)
- ✅ Calcular índices espectrales (NDVI, NDBI, NDWI, BSI) (Fase 2)
- ✅ Implementar algoritmos de detección de cambios - 3 métodos (Fase 3)
- ✅ Cuantificar cambios por zonas administrativas (Fase 4)
- 📋 Desarrollar un dashboard interactivo con Streamlit (Fase 5)
- 📋 Generar informe final con resultados (Fase 6)

## 📊 Estado del Proyecto

| Fase | Descripción | Estado | Archivos Generados |
|------|-------------|--------|-------------------|
| **Fase 0** | Configuración del entorno | ✅ Completada | 8 carpetas, venv, requirements.txt |
| **Fase 1** | Descarga de imágenes Sentinel-2 | ✅ Completada | 4 GeoTIFF (108 MB total) |
| **Fase 2** | Cálculo de índices espectrales | ✅ Completada | 4 GeoTIFF índices (161 MB), CSV estadísticas |
| **Fase 3** | Detección de cambios (3 métodos) | ✅ Completada | 6 GeoTIFF cambios (20 MB), CSV estadísticas |
| **Fase 4** | Análisis zonal (100 zonas) | ✅ Completada | 2 GeoPackage, 3 CSV, 2 PNG, notebook |
| **Fase 5** | Dashboard Streamlit | ✅ Completada | Dashboard funcional (900+ líneas), localhost:8501 |
| **Fase 6** | Informe final LaTeX | ✅ Completada | Informe completo (19 páginas), 24 referencias |

## 🗂️ Estructura del Proyecto

```
laboratorio_cambio_urbano/
├── data/
│   ├── raw/              # Imágenes satelitales originales
│   ├── processed/        # Índices calculados y cambios
│   └── vector/           # Shapefiles y GeoPackages
├── notebooks/            # Jupyter notebooks de análisis
├── scripts/              # Scripts Python reutilizables
├── app/                  # Aplicación Streamlit
├── outputs/
│   ├── figures/          # Gráficos generados
│   ├── maps/             # Mapas exportados
│   └── reports/          # Informes
└── docs/                 # Documentación y guías
```

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repo>
cd laboratorio_cambio_urbano
```

2. Crear y activar entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o en Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Autenticar Google Earth Engine (si se usa):
```bash
earthengine authenticate
```

## 💻 Uso

### 🔹 Fase 1: Descargar Imágenes Sentinel-2
```bash
source venv/bin/activate
python scripts/download_sentinel.py
```
**Salida:** 4 archivos GeoTIFF en `data/raw/` (sentinel2_2018.tif, 2020, 2022, 2024)

### 🔹 Fase 2: Calcular Índices Espectrales
```bash
python scripts/calculate_indices.py
```
**Salida:** 4 archivos con índices en `data/processed/` + CSV de estadísticas

**Alternativa interactiva:**
```bash
jupyter notebook notebooks/02_calculo_indices.ipynb
```

### 🔹 Fase 3: Detectar Cambios Urbanos
```bash
python scripts/detect_changes.py
```
**Salida:** 6 archivos GeoTIFF (3 métodos × 2 tipos) + CSV de estadísticas

**Alternativa interactiva:**
```bash
jupyter notebook notebooks/03_deteccion_cambios.ipynb
```

### 🔹 Fase 4: Análisis Zonal por Zonas
```bash
python scripts/zonal_analysis.py
```
**Salida:** 2 GeoPackage (grilla + estadísticas), 3 CSV, 2 PNG mapas

**Alternativa interactiva:**
```bash
jupyter notebook notebooks/04_analisis_zonal.ipynb
```

### 🔹 Fase 5: Dashboard Interactivo
```bash
streamlit run app/app.py
```
**Acceso:** Abre automáticamente en `http://localhost:8501`

**Funcionalidades del Dashboard:**
- 🗺️ Mapa interactivo con capas de cambio (Folium + Choropleth)
- ⚙️ Filtros dinámicos por fecha y tipo de cambio
- 📊 Métricas clave (urbanización, pérdida/ganancia vegetación)
- 📈 Gráficos temporales interactivos (Plotly)
- 🔍 Comparador visual antes/después
- 💾 Descarga de datos en formato CSV
- 🔥 Ranking de hotspots de cambio urbano

**Componentes principales:**
- Mapa de calor coroplético con zoom/pan
- Tooltips informativos por zona
- Marcadores para top 3 zonas críticas
- Gráficos de evolución NDVI/NDBI
- Gráficos de cobertura del suelo (%)
- Tablas de ranking con degradado de colores
- Panel lateral con filtros interactivos


### 🔹 Dashboard 
```bash
cd app
streamlit run app.py
```


## 📊 Índices Espectrales

| Índice | Fórmula | Detecta | Rango | Interpretación |
|--------|---------|---------|-------|----------------|
| **NDVI** | (NIR - Red) / (NIR + Red) | Vegetación | [-1, +1] | Valores altos = vegetación densa |
| **NDBI** | (SWIR - NIR) / (SWIR + NIR) | Áreas construidas | [-1, +1] | Valores altos = zonas urbanas |
| **NDWI** | (Green - NIR) / (Green + NIR) | Cuerpos de agua | [-1, +1] | Valores altos = agua superficial |
| **BSI** | ((SWIR + Red) - (NIR + Blue)) / ((SWIR + Red) + (NIR + Blue)) | Suelo desnudo | [-1, +1] | Valores altos = suelo expuesto |

### Resultados Fase 2 (Peñaflor 2018-2024)

| Índice | Tendencia | Cambio Absoluto | Interpretación |
|--------|-----------|-----------------|----------------|
| NDVI | 0.417 → 0.405 | **-0.012** | ⚠️ Pérdida de vegetación (-2.9%) |
| NDBI | -0.042 → -0.031 | **+0.011** | 🏗️ Expansión urbana (+26.2%) |
| NDWI | -0.494 → -0.476 | +0.018 | Leve aumento de agua (+3.6%) |
| BSI | 0.022 → 0.030 | +0.008 | Incremento de suelo desnudo (+36.4%) |

**Conclusión:** Se observa un proceso de **urbanización activa** con reemplazo de vegetación por áreas construidas y suelo en transición.

---

### Resultados Fase 3 (Detección de Cambios Multi-Método)

#### Método 1: Diferencia Simple (ΔNDVI)
| Categoría | Hectáreas | % Área |
|-----------|-----------|---------|
| Pérdida vegetación | 3,742.62 | 15.38% |
| Ganancia vegetación | 2,463.46 | 10.12% |
| Sin cambio | 18,129.92 | 74.50% |

#### Método 2: Clasificación Multicriterio
| Tipo de Cambio | Hectáreas | % Área | Interpretación |
|----------------|-----------|---------|----------------|
| **Urbanización** | **1,689.36** | **6.94%** | 🏙️ Vegetación → Área construida |
| Pérdida vegetación | 2,196.19 | 9.02% | 🌳 Reducción cobertura vegetal |
**Hallazgo Principal:** Se detectó **expansión urbana de 1,689 hectáreas** (equiv. a ~282 ha/año) principalmente en el borde norte y oeste del núcleo urbano existente, con pérdida neta de vegetación de 2,196-3,743 ha según el método utilizado.

---

### Resultados Fase 4 (Análisis Zonal de Distribución Espacial)

#### Resumen Global por Zonas

| Métrica | Valor | Unidad |
|---------|-------|--------|
| **Zonas analizadas** | 100 | zonas (grilla 10×10) |
| **Urbanización total** | 1,689.36 | ha |
| **Pérdida vegetación** | 2,196.19 | ha |
| **Ganancia vegetación** | 2,463.36 | ha |
| **Balance neto vegetación** | +267.17 | ha (+12%) |

#### Top 10 Hotspots de Urbanización

| Ranking | Zona ID | Urbanización (ha) | Índice Transformación |
| `scripts/download_sentinel.py` | Script de descarga de imágenes Sentinel-2 vía GEE |
| `scripts/calculate_indices.py` | Cálculo de índices espectrales (NDVI, NDBI, NDWI, BSI) |
| `scripts/detect_changes.py` | Detección de cambios con 3 métodos (diferencia, multicriterio, Z-score) |
| `scripts/zonal_analysis.py` | Análisis zonal con grilla 10×10, estadísticas por zona, hotspots |
| `notebooks/02_calculo_indices.ipynb` | Análisis interactivo de índices con visualizaciones |
| `notebooks/03_deteccion_cambios.ipynb` | Análisis comparativo de métodos de detección |
| `notebooks/04_analisis_zonal.ipynb` | Exploración interactiva de resultados zonales |
| `app/app.py` | Dashboard Streamlit (en desarrollo) |
| `app/config.py` | Configuración centralizada (coordenadas, fechas, umbrales) |
| `app/utils.py` | Funciones auxiliares reutilizables |
| `docs/bitacora_fase1.md` | Documentación Fase 1 (adquisición de datos) |
| `docs/bitacora_fase2.md` | Documentación Fase 2 (índices espectrales) |
| `docs/bitacora_fase3.md` | Documentación Fase 3 (detección de cambios) |
| `docs/bitacora_fase4.md` | Documentación Fase 4 (análisis zonal) |
| `docs/referencias.md` | Bibliografía completa del proyecto (35 referencias) |

**Hallazgos Clave:**
- **Concentración espacial:** 10 zonas (10% del territorio) acumulan **539 ha** (32% de la urbanización total)
- **Balance vegetativo positivo:** +267 ha netos de ganancia vegetativa (posible revegetación post-sequía 2019-2022)
- **Heterogeneidad extrema:** Rango de urbanización entre 0-62 ha por zona
- **Tasa real vs proyección oficial:** 1.1%/año de urbanización (2× superior a proyecciones del Plan Regulador Comunal)

#### Evolución Temporal de Índices

| Año | NDVI | NDBI | % Vegetación | % Urbano |
|-----|------|------|--------------|----------|
| 2018 | 0.417 | -0.042 | 55.7% | 41.6% |
### Fase 3: Detección de Cambios
- `data/processed/cambio_diferencia.tif` (0.17 MB, clasificación -1/0/1)
- `data/processed/cambio_diferencia_continua.tif` (8.89 MB, valores ΔNDVI)
- `data/processed/cambio_clasificado.tif` (0.20 MB, clases 0-5 multicriterio)
- `data/processed/cambio_zscore.tif` (0.28 MB, clasificación -1/0/1)
- `data/processed/cambio_zscore_valores.tif` (10.67 MB, valores Z-score)
- `data/processed/estadisticas_cambios.csv` (0.001 MB, resumen por método)

### Fase 4: Análisis Zonal
- `data/vector/grilla_zonas.gpkg` (0.12 MB, grilla 10×10 con 100 zonas)
- `data/vector/zonas_con_datos.gpkg` (0.13 MB, zonas + 27 campos estadísticos)
- `data/processed/estadisticas_zonales.csv` (0.02 MB, tabla completa 100 zonas)
- `data/processed/ranking_zonas.csv` (0.00 MB, top 10 hotspots)
- `data/processed/evolucion_temporal.csv` (0.00 MB, serie 2018-2024)
- `outputs/figures/mapas_coropleticos.png` (0.19 MB, 4 mapas intensidad)
- `outputs/figures/evolucion_temporal.png` (0.11 MB, 4 gráficos temporales)
- **Sentinel-2 MSI:** ESA Copernicus Program - https://sentinel.esa.int/web/sentinel/missions/sentinel-2
- **Google Earth Engine:** https://earthengine.google.com/
- **NDVI:** Tucker, C.J. (1979). Red and photographic infrared linear combinations for monitoring vegetation.
- **NDBI:** Zha, Y., et al. (2003). Use of normalized difference built-up index in automatically mapping urban areas.
- **rasterstats:** Perry, M. (2013). Python-rasterstats. https://github.com/perrygeo/python-rasterstats
- **Ver bibliografía completa en:** `docs/referencias.md` (35 referencias)
| Anomalía negativa (Z < -2) | 2,506.20 | 10.30% |
| Normal (\|Z\| ≤ 2) | 15,370.89 | 63.16% |
| Anomalía positiva (Z > +2) | 6,458.91 | 26.54% |

---

**Última actualización:** 30 de enero de 2025  
**Fase actual:** Fase 6 completada ✅ | Próxima: Fase 7-8 (Animación temporal + Deploy dashboard)
- `earthengine-api==1.1.3` - Google Earth Engine Python API
- `geemap==1.0.1` - Mapas interactivos con Earth Engine
- `rasterio==1.4.3` - Procesamiento de rasters GeoTIFF
- `geopandas==1.0.1` - Datos vectoriales geoespaciales
- `streamlit==1.41.1` / `folium==0.19.3` - Dashboard web interactivo
- `plotly==5.24.1` / `matplotlib==3.10.0` - Visualizaciones
- `numpy==2.2.2` / `pandas==2.2.3` - Análisis de datos
- `scipy==1.15.1` - Estadísticas y procesamiento de señales

**Total:** 16 librerías (ver `requirements.txt` completo)

## 📁 Archivos Clave

| Ruta | Descripción |
|------|-------------|
| `scripts/download_sentinel.py` | Script de descarga de imágenes Sentinel-2 vía GEE |
| `scripts/calculate_indices.py` | Cálculo de índices espectrales (NDVI, NDBI, NDWI, BSI) |
| `scripts/detect_changes.py` | Detección de cambios con 3 métodos (diferencia, multicriterio, Z-score) |
| `notebooks/02_calculo_indices.ipynb` | Análisis interactivo de índices con visualizaciones |
| `notebooks/03_deteccion_cambios.ipynb` | Análisis comparativo de métodos de detección |
| `app/app.py` | Dashboard Streamlit (en desarrollo) |
| `app/config.py` | Configuración centralizada (coordenadas, fechas, umbrales) |
| `app/utils.py` | Funciones auxiliares reutilizables |
| `docs/bitacora_fase1.md` | Documentación Fase 1 (adquisición de datos) |
| `docs/bitacora_fase2.md` | Documentación Fase 2 (índices espectrales) |
| `docs/bitacora_fase3.md` | Documentación Fase 3 (detección de cambios) |

## 🔍 Datos Generados

### Fase 1: Imágenes Sentinel-2
- `data/raw/sentinel2_2018.tif` (21 MB, 6 bandas, 1 imagen fuente)
- `data/raw/sentinel2_2020.tif` (29 MB, 6 bandas, 7 imágenes compuestas)
- `data/raw/sentinel2_2022.tif` (29 MB, 6 bandas, 10 imágenes compuestas)
- `data/raw/sentinel2_2024.tif` (29 MB, 6 bandas, 10 imágenes compuestas)

### Fase 2: Índices Espectrales
- `data/processed/indices_2018.tif` (37 MB, 4 bandas: NDVI, NDBI, NDWI, BSI)
- `data/processed/indices_2020.tif` (42 MB)
- `data/processed/indices_2022.tif` (42 MB)
- `data/processed/indices_2024.tif` (42 MB)
- `data/processed/estadisticas_indices.csv` (1.8 KB, tabla resumen)

### Fase 3: Detección de Cambios
- `data/processed/cambio_diferencia.tif` (0.17 MB, clasificación -1/0/1)
- `data/processed/cambio_diferencia_continua.tif` (8.89 MB, valores ΔNDVI)
- `data/processed/cambio_clasificado.tif` (0.20 MB, clases 0-5 multicriterio)
- `data/processed/cambio_zscore.tif` (0.28 MB, clasificación -1/0/1)
- `data/processed/cambio_zscore_valores.tif` (10.67 MB, valores Z-score)
- `data/processed/estadisticas_cambios.csv` (0.001 MB, resumen por método)

## 👥 Autor

**Byron Caices**  
Estudiante - Desarrollo de Aplicaciones Geoinformáticas  
Universidad de Santiago de Chile

## 📚 Referencias

- **Sentinel-2 MSI:** ESA Copernicus Program - https://sentinel.esa.int/web/sentinel/missions/sentinel-2
- **Google Earth Engine:** https://earthengine.google.com/
- **NDVI:** Tucker, C.J. (1979). Red and photographic infrared linear combinations for monitoring vegetation.
- **NDBI:** Zha, Y., et al. (2003). Use of normalized difference built-up index in automatically mapping urban areas.

## 📄 Licencia

Este proyecto es parte del curso de Desarrollo de Aplicaciones Geoinformáticas (2025).  
Material académico - Universidad de Santiago de Chile.

---

**Última actualización:** 30 de enero de 2025  
**Fase actual:** Fase 3 completada ✅ | Próxima: Fase 4 (Análisis Zonal por Unidades Administrativas)
