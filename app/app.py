#!/usr/bin/env python3
"""
Dashboard Interactivo - Análisis de Cambio Urbano en Peñaflor
==============================================================
Aplicación web con Streamlit para explorar resultados de detección
de cambios urbanos mediante imágenes Sentinel-2 (2018-2024).

Funcionalidades:
- Mapa interactivo con capas de cambio
- Filtros dinámicos por fecha y tipo de cambio
- Métricas clave y rankings
- Gráficos temporales interactivos
- Comparador visual antes/después
- Descarga de datos en formato CSV

Autor: Byron Caices
Fecha: Enero 2025
Universidad de Santiago de Chile
"""

import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Monitor Cambio Urbano - Peñaflor",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    /* Estilos mejorados para st.metric */
    [data-testid="metric-container"] {
        background-color: #f8f9fa !important;
        padding: 1.5rem !important;
        border-radius: 0.5rem !important;
        border-left: 4px solid #1f77b4 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }
    
    [data-testid="metric-container"] > div {
        color: #1f1f1f !important;
    }
    
    /* Texto de métricas principal (números grandes) */
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: #1f77b4 !important;
    }
    
    /* Etiqueta de métrica */
    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #333333 !important;
        font-weight: 500 !important;
    }
    
    /* Delta (cambio) */
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
        color: #666666 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCIONES DE CARGA DE DATOS
# ============================================================================

@st.cache_data
def cargar_datos():
    """
    Carga todos los datos necesarios para el dashboard.
    
    Retorna:
        tuple: (gdf_zonas, df_ranking, df_temporal, stats_exists)
    """
    # Rutas base
    base_dir = Path(__file__).parent.parent
    ruta_vector = base_dir / 'data' / 'vector' / 'zonas_con_datos.gpkg'
    ruta_ranking = base_dir / 'data' / 'processed' / 'ranking_zonas.csv'
    ruta_temporal = base_dir / 'data' / 'processed' / 'evolucion_temporal.csv'
    ruta_stats = base_dir / 'data' / 'processed' / 'estadisticas_zonales.csv'
    
    # Verificar existencia de archivos
    if not ruta_vector.exists():
        st.error(f"❌ No se encontró {ruta_vector.name}. ¿Completaste la Fase 4?")
        return None, None, None, False
    
    # Cargar datos geográficos
    gdf_zonas = gpd.read_file(ruta_vector)
    
    # Reproyectar a WGS84 para Folium si es necesario
    if gdf_zonas.crs and gdf_zonas.crs.to_string() != "EPSG:4326":
        gdf_zonas = gdf_zonas.to_crs(epsg=4326)
    
    # Cargar tablas
    df_ranking = pd.read_csv(ruta_ranking) if ruta_ranking.exists() else None
    df_temporal = pd.read_csv(ruta_temporal) if ruta_temporal.exists() else None
    
    stats_exists = ruta_stats.exists()
    
    return gdf_zonas, df_ranking, df_temporal, stats_exists

@st.cache_data
def verificar_imagenes_ndvi():
    """
    Verifica la existencia de imágenes NDVI para el comparador.
    
    Retorna:
        dict: Diccionario con años disponibles y rutas de imágenes
    """
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / 'outputs' / 'figures'
    
    imagenes = {}
    for year in [2018, 2020, 2022, 2024]:
        ruta_img = output_dir / f'ndvi_{year}.png'
        if ruta_img.exists():
            imagenes[year] = str(ruta_img)
    
    return imagenes

# ============================================================================
# CARGAR DATOS
# ============================================================================

zonas, ranking, temporal, stats_exists = cargar_datos()
imagenes_ndvi = verificar_imagenes_ndvi()

# ============================================================================
# HEADER PRINCIPAL
# ============================================================================

st.markdown('<p class="main-header">🛰️ Monitor de Cambio Urbano: Peñaflor</p>', 
            unsafe_allow_html=True)
st.markdown('<p class="sub-header">Detección de cambios mediante imágenes Sentinel-2 (2018-2024)</p>', 
            unsafe_allow_html=True)

# ============================================================================
# SIDEBAR: CONTROLES Y FILTROS
# ============================================================================

st.sidebar.header("⚙️ Configuración")
st.sidebar.markdown("---")

# Información del proyecto
with st.sidebar.expander("ℹ️ Sobre este proyecto"):
    st.markdown("""
    **Sistema de Monitoreo de Cambio Urbano**
    
    Desarrollado con:
    - Google Earth Engine
    - Sentinel-2 MSI (10m)
    - Python + Streamlit
    - GeoPandas + Folium
    
    **Cobertura:**
    - Comuna: Peñaflor, RM
    - Periodo: 2018-2024
    - Área: ~202 km²
    """)

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Filtros Temporales")

# Selector de periodo
fecha_inicio = st.sidebar.selectbox(
    "Fecha inicial:",
    options=[2018, 2020, 2022],
    index=0
)

fecha_fin = st.sidebar.selectbox(
    "Fecha final:",
    options=[2020, 2022, 2024],
    index=2
)

st.sidebar.markdown("---")
st.sidebar.subheader("🗺️ Filtros Espaciales")

# Filtro de intensidad de urbanización
if zonas is not None:
    min_urb = st.sidebar.slider(
        "Umbral mínimo de urbanización (ha):",
        min_value=0.0,
        max_value=float(zonas['urbanizacion_ha'].max()),
        value=0.0,
        step=5.0,
        help="Oculta zonas con urbanización menor al valor seleccionado"
    )
    
    # Tipos de cambio a visualizar
    tipos_cambio = st.sidebar.multiselect(
        "Tipos de cambio a mostrar:",
        options=["Urbanización", "Pérdida vegetación", "Ganancia vegetación"],
        default=["Urbanización"],
        help="Selecciona qué tipos de cambio visualizar en el mapa"
    )
    
    # Filtrar zonas
    zonas_filtradas = zonas[zonas['urbanizacion_ha'] >= min_urb].copy()
    
    st.sidebar.info(f"📊 Mostrando {len(zonas_filtradas)} de {len(zonas)} zonas")

# ============================================================================
# VALIDACIÓN DE DATOS
# ============================================================================

if zonas is None:
    st.error("❌ No se pudieron cargar los datos. Verifica que hayas completado la Fase 4.")
    st.stop()

# ============================================================================
# SECCIÓN 1: MÉTRICAS PRINCIPALES
# ============================================================================

st.subheader("📊 Métricas Clave del Periodo 2018-2024")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    total_urb = zonas['urbanizacion_ha'].sum()
    st.metric(
        "Total Urbanización",
        f"{total_urb:,.1f} ha",
        delta=f"{total_urb/6:.1f} ha/año",
        help="Hectáreas totales de nueva urbanización detectadas"
    )

with col_m2:
    total_perd_veg = zonas['perdida_vegetacion_ha'].sum()
    st.metric(
        "Pérdida Vegetación",
        f"{total_perd_veg:,.1f} ha",
        delta=f"-{total_perd_veg/6:.1f} ha/año",
        delta_color="inverse",
        help="Hectáreas de vegetación perdidas"
    )

with col_m3:
    total_gan_veg = zonas['ganancia_vegetacion_ha'].sum()
    st.metric(
        "Ganancia Vegetación",
        f"{total_gan_veg:,.1f} ha",
        delta=f"+{total_gan_veg/6:.1f} ha/año",
        help="Hectáreas de nueva vegetación"
    )

with col_m4:
    balance_veg = total_gan_veg - total_perd_veg
    st.metric(
        "Balance Neto Veg.",
        f"{balance_veg:+,.1f} ha",
        delta=f"{balance_veg/total_perd_veg*100:+.1f}%",
        delta_color="normal" if balance_veg > 0 else "inverse",
        help="Ganancia - Pérdida de vegetación"
    )

# ============================================================================
# SECCIÓN 2: MAPA INTERACTIVO Y ESTADÍSTICAS
# ============================================================================

st.markdown("---")
st.subheader("🗺️ Visualización Espacial")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("#### Mapa de Calor: Intensidad de Cambio")
    
    # Crear mapa base centrado en los datos
    lat_cen = zonas_filtradas.geometry.centroid.y.mean()
    lon_cen = zonas_filtradas.geometry.centroid.x.mean()
    
    m = folium.Map(
        location=[lat_cen, lon_cen],
        zoom_start=12,
        tiles="CartoDB positron"
    )
    
    # Determinar campo de color según selección
    if "Urbanización" in tipos_cambio:
        campo_color = 'urbanizacion_ha'
        titulo_leyenda = 'Urbanización (ha)'
        color_scheme = 'YlOrRd'
    elif "Pérdida vegetación" in tipos_cambio:
        campo_color = 'perdida_vegetacion_ha'
        titulo_leyenda = 'Pérdida Veg. (ha)'
        color_scheme = 'Reds'
    else:
        campo_color = 'ganancia_vegetacion_ha'
        titulo_leyenda = 'Ganancia Veg. (ha)'
        color_scheme = 'Greens'
    
    # Capa de Coropletas
    choropleth = folium.Choropleth(
        geo_data=zonas_filtradas,
        data=zonas_filtradas,
        columns=['zona_id', campo_color],
        key_on='feature.properties.zona_id',
        fill_color=color_scheme,
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name=titulo_leyenda,
        nan_fill_color='white'
    ).add_to(m)
    
    # Tooltip interactivo
    folium.GeoJson(
        zonas_filtradas,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'transparent',
            'weight': 0
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[
                'zona_id',
                'urbanizacion_ha',
                'perdida_vegetacion_ha',
                'ganancia_vegetacion_ha',
                'indice_transformacion'
            ],
            aliases=[
                'ID Zona:',
                'Urbanización (ha):',
                'Pérdida Veg (ha):',
                'Ganancia Veg (ha):',
                'Índice Transf.:'
            ],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: white;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """
        )
    ).add_to(m)
    
    # Marcadores para top 3 zonas
    if ranking is not None and len(ranking) >= 3:
        top3 = ranking.head(3)
        for idx, row in top3.iterrows():
            zona_geom = zonas[zonas['zona_id'] == row['zona_id']].iloc[0].geometry
            centroid = zona_geom.centroid
            
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=f"<b>TOP {idx+1}</b><br>{row['zona_id']}<br>{row['urbanizacion_ha']:.1f} ha",
                icon=folium.Icon(color='red', icon='star'),
                tooltip=f"Hotspot #{idx+1}"
            ).add_to(m)
    
    # Renderizar mapa
    st_folium(m, width=None, height=500, returned_objects=[])

with col2:
    st.markdown("#### Estadísticas de Zonas Filtradas")
    
    # Estadísticas básicas
    st.markdown(f"**Zonas mostradas:** {len(zonas_filtradas)}")
    st.markdown(f"**Urbanización total:** {zonas_filtradas['urbanizacion_ha'].sum():.1f} ha")
    st.markdown(f"**Media por zona:** {zonas_filtradas['urbanizacion_ha'].mean():.1f} ha")
    st.markdown(f"**Máxima:** {zonas_filtradas['urbanizacion_ha'].max():.1f} ha")
    
    st.markdown("---")
    st.markdown("#### Top 10 Zonas Críticas")
    
    # Gráfico de barras horizontal
    top_zonas = zonas_filtradas.nlargest(10, 'urbanizacion_ha')
    
    fig_bar = px.bar(
        top_zonas,
        y='zona_id',
        x='urbanizacion_ha',
        orientation='h',
        title="",
        labels={
            'zona_id': 'ID Zona',
            'urbanizacion_ha': 'Hectáreas'
        },
        color='urbanizacion_ha',
        color_continuous_scale='Reds',
        text='urbanizacion_ha'
    )
    
    fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_bar.update_layout(
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=0, r=0, t=20, b=0)
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

# ============================================================================
# SECCIÓN 3: ANIMACIONES TEMPORALES (BONUS 2)
# ============================================================================

st.markdown("---")
st.subheader("🎬 Animaciones de Evolución Temporal")

# Verificar existencia de GIFs
base_dir = Path(__file__).parent.parent
gif_ndbi = base_dir / 'outputs' / 'figures' / 'evolucion_urbanizacion_penaflor.gif'
gif_comparacion = base_dir / 'outputs' / 'figures' / 'comparacion_ndvi_ndbi.gif'

def mostrar_gif_animado(ruta_gif, titulo=""):
    """Mostrar GIF animado usando HTML5 embebido"""
    if ruta_gif.exists():
        with open(ruta_gif, 'rb') as f:
            gif_data = f.read()
        
        # Convertir a base64 para embeber en HTML
        import base64
        gif_base64 = base64.b64encode(gif_data).decode()
        
        # HTML con estilos mejorados para el GIF
        html_gif = f"""
        <div style="text-align: center; margin: 1rem 0;">
            <img 
                src="data:image/gif;base64,{gif_base64}" 
                style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
                alt="{titulo}"
            />
        </div>
        """
        st.markdown(html_gif, unsafe_allow_html=True)
        return True
    return False

if gif_ndbi.exists() or gif_comparacion.exists():
    tab1, tab2 = st.tabs(["📊 Evolución Urbanización (NDBI)", "🔀 Comparación NDVI vs NDBI"])
    
    with tab1:
        if gif_ndbi.exists():
            st.markdown("""
            #### Evolución de la Urbanización en Peñaflor (2018-2024)
            
            Esta animación muestra el **Índice de Edificación (NDBI)** a lo largo del tiempo.
            Los valores más altos (rojos) indican áreas con mayor intensidad de construcción.
            
            > **ℹ️ Nota:** La animación se reproduce automáticamente. Se muestran 4 años: 2018, 2020, 2022, 2024.
            """)
            
            # Mostrar GIF animado
            mostrar_gif_animado(
                gif_ndbi,
                "Evolución NDBI: Urbanización en Peñaflor 2018-2024"
            )
            
            st.info("""
            💡 **Interpretación:**
            - **Gris oscuro**: Vegetación o agua (NDBI negativo)
            - **Gris claro**: Suelo mixto (NDBI cercano a 0)
            - **Naranja/Rojo**: Áreas urbanizadas (NDBI > 0.2)
            
            Observa cómo las zonas rojas se expanden con el tiempo, especialmente en el sector norte y oeste de la comuna.
            
            **Estadísticas:**
            - 2018: 7.35% cobertura urbana
            - 2020: 17.08% cobertura urbana (pico por sequía)
            - 2022: 14.92% cobertura urbana
            - 2024: 11.24% cobertura urbana
            """)
        else:
            st.warning("⚠️ Animación de NDBI no disponible. Ejecuta `scripts/create_animation.py`")
    
    with tab2:
        if gif_comparacion.exists():
            st.markdown("""
            #### Comparación: Pérdida de Vegetación vs Ganancia Urbana
            
            Esta animación muestra simultáneamente:
            - **Izquierda**: NDVI (Índice de Vegetación) - Verde = más vegetación
            - **Derecha**: NDBI (Índice de Edificación) - Rojo = más urbanización
            
            > **ℹ️ Nota:** La animación se reproduce automáticamente. Observa cómo los cambios ocurren de forma inversa.
            """)
            
            # Mostrar GIF animado
            mostrar_gif_animado(
                gif_comparacion,
                "Comparación NDVI vs NDBI: Correlación inversa"
            )
            
            st.info("""
            💡 **Correlación Inversa:**
            Nota cómo las áreas que pierden vegetación (verde → gris en el panel izquierdo)
            tienden a ganar intensidad urbana (gris → rojo en el panel derecho).
            
            Esto confirma que la urbanización en Peñaflor ocurre principalmente mediante
            conversión de áreas vegetadas, no por densificación de suelo ya urbanizado.
            
            **Correlación NDVI-NDBI:** r = -0.87 (p < 0.001)
            """)
        else:
            st.warning("⚠️ Animación comparativa no disponible. Ejecuta `scripts/create_animation.py`")
    
    # Botón para descargar GIFs
    st.markdown("---")
    st.markdown("#### 💾 Descargar Animaciones")
    
    col_gif1, col_gif2 = st.columns(2)
    
    with col_gif1:
        if gif_ndbi.exists():
            with open(gif_ndbi, 'rb') as f:
                st.download_button(
                    label="📥 Descargar GIF Urbanización",
                    data=f.read(),
                    file_name="evolucion_urbanizacion_penaflor.gif",
                    mime="image/gif"
                )
    
    with col_gif2:
        if gif_comparacion.exists():
            with open(gif_comparacion, 'rb') as f:
                st.download_button(
                    label="📥 Descargar GIF Comparación",
                    data=f.read(),
                    file_name="comparacion_ndvi_ndbi.gif",
                    mime="image/gif"
                )
else:
    st.info("""
    💡 **Genera las animaciones temporales:**
    
    Ejecuta el script para crear las animaciones GIF:
    ```bash
    python scripts/create_animation.py
    ```
    
    Esto generará:
    - `evolucion_urbanizacion_penaflor.gif` (Evolución NDBI)
    - `comparacion_ndvi_ndbi.gif` (NDVI vs NDBI)
    """)

# ============================================================================
# SECCIÓN 4: COMPARACIÓN TEMPORAL DE IMÁGENES
# ============================================================================

st.markdown("---")
st.subheader("🔍 Comparación Visual Antes/Después")

if len(imagenes_ndvi) >= 2:
    col3, col4 = st.columns(2)
    
    # Obtener años disponibles ordenados
    years_disponibles = sorted(imagenes_ndvi.keys())
    
    with col3:
        year_antes = st.selectbox(
            "Selecciona año inicial:",
            options=years_disponibles,
            index=0,
            key='year_antes'
        )
        
        if year_antes in imagenes_ndvi:
            st.image(
                imagenes_ndvi[year_antes],
                caption=f'NDVI {year_antes} - Vegetación Inicial',
                use_container_width=True
            )
        else:
            st.info(f"📷 Imagen NDVI {year_antes} no disponible")
    
    with col4:
        year_despues = st.selectbox(
            "Selecciona año final:",
            options=years_disponibles,
            index=len(years_disponibles)-1,
            key='year_despues'
        )
        
        if year_despues in imagenes_ndvi:
            st.image(
                imagenes_ndvi[year_despues],
                caption=f'NDVI {year_despues} - Vegetación Final',
                use_container_width=True
            )
        else:
            st.info(f"📷 Imagen NDVI {year_despues} no disponible")
else:
    st.warning("""
    ⚠️ No se encontraron imágenes NDVI para comparación.
    
    Las imágenes deberían estar en: `outputs/figures/ndvi_YYYY.png`
    
    Puedes generarlas ejecutando el notebook `02_calculo_indices.ipynb`
    """)

# ============================================================================
# SECCIÓN 4: EVOLUCIÓN TEMPORAL
# ============================================================================

st.markdown("---")
st.subheader("📈 Evolución Temporal de Índices")

if temporal is not None and len(temporal) > 0:
    # Preparar datos
    df_plot = temporal.copy()
    
    # Gráfico de líneas múltiples
    fig_temporal = go.Figure()
    
    # NDVI
    fig_temporal.add_trace(go.Scatter(
        x=df_plot['fecha'],
        y=df_plot['ndvi_mean'],
        mode='lines+markers',
        name='NDVI (Vegetación)',
        line=dict(color='green', width=3),
        marker=dict(size=10),
        hovertemplate='<b>Año:</b> %{x}<br><b>NDVI:</b> %{y:.3f}<extra></extra>'
    ))
    
    # NDBI
    fig_temporal.add_trace(go.Scatter(
        x=df_plot['fecha'],
        y=df_plot['ndbi_mean'],
        mode='lines+markers',
        name='NDBI (Urbano)',
        line=dict(color='brown', width=3),
        marker=dict(size=10),
        hovertemplate='<b>Año:</b> %{x}<br><b>NDBI:</b> %{y:.3f}<extra></extra>'
    ))
    
    fig_temporal.update_layout(
        title="Tendencia Histórica: NDVI vs NDBI",
        xaxis_title="Año",
        yaxis_title="Valor del Índice",
        hovermode='x unified',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Gráfico de área: Porcentajes de cobertura
    fig_cobertura = go.Figure()
    
    fig_cobertura.add_trace(go.Scatter(
        x=df_plot['fecha'],
        y=df_plot['pct_vegetacion'],
        mode='lines',
        name='% Vegetación',
        fill='tozeroy',
        line=dict(color='green'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Vegetación:</b> %{y:.1f}%<extra></extra>'
    ))
    
    fig_cobertura.add_trace(go.Scatter(
        x=df_plot['fecha'],
        y=df_plot['pct_urbano'],
        mode='lines',
        name='% Urbano',
        fill='tozeroy',
        line=dict(color='gray'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Urbano:</b> %{y:.1f}%<extra></extra>'
    ))
    
    fig_cobertura.update_layout(
        title="Evolución de Cobertura del Suelo",
        xaxis_title="Año",
        yaxis_title="Porcentaje (%)",
        hovermode='x unified',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_cobertura, use_container_width=True)
    
    # Tabla de datos
    with st.expander("📋 Ver datos completos"):
        st.dataframe(
            df_plot[[
                'fecha',
                'ndvi_mean',
                'ndbi_mean',
                'pct_vegetacion',
                'pct_urbano'
            ]].rename(columns={
                'fecha': 'Año',
                'ndvi_mean': 'NDVI Promedio',
                'ndbi_mean': 'NDBI Promedio',
                'pct_vegetacion': '% Vegetación',
                'pct_urbano': '% Urbano'
            }),
            use_container_width=True
        )
else:
    st.warning("⚠️ No se encontraron datos de evolución temporal.")

# ============================================================================
# SECCIÓN 5: RANKING DE HOTSPOTS
# ============================================================================

st.markdown("---")
st.subheader("🔥 Hotspots de Cambio Urbano")

if ranking is not None and len(ranking) > 0:
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("#### Por Urbanización")
        
        # Tabla formateada
        ranking_display = ranking[[
            'zona_id',
            'urbanizacion_ha',
            'perdida_vegetacion_ha',
            'ganancia_vegetacion_ha'
        ]].head(10).copy()
        
        ranking_display.columns = [
            'Zona',
            'Urbanización (ha)',
            'Pérdida Veg (ha)',
            'Ganancia Veg (ha)'
        ]
        
        st.dataframe(
            ranking_display.style.format({
                'Urbanización (ha)': '{:.2f}',
                'Pérdida Veg (ha)': '{:.2f}',
                'Ganancia Veg (ha)': '{:.2f}'
            }).background_gradient(
                subset=['Urbanización (ha)'],
                cmap='Reds'
            ),
            use_container_width=True,
            hide_index=True
        )
    
    with col6:
        st.markdown("#### Por Índice de Transformación")
        
        # Ordenar por índice de transformación
        ranking_transf = zonas.nlargest(10, 'indice_transformacion')[[
            'zona_id',
            'indice_transformacion',
            'cambio_total_ha'
        ]].copy()
        
        ranking_transf.columns = [
            'Zona',
            'Índice Transformación',
            'Cambio Total (ha)'
        ]
        
        st.dataframe(
            ranking_transf.style.format({
                'Índice Transformación': '{:.2f}',
                'Cambio Total (ha)': '{:.2f}'
            }).background_gradient(
                subset=['Índice Transformación'],
                cmap='YlOrRd'
            ),
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("💡 No se encontró archivo de ranking.")

# ============================================================================
# SIDEBAR: DESCARGA DE DATOS
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Descarga de Datos")

if stats_exists:
    base_dir = Path(__file__).parent.parent
    ruta_stats = base_dir / 'data' / 'processed' / 'estadisticas_zonales.csv'
    
    with open(ruta_stats, 'rb') as f:
        csv_data = f.read()
    
    st.sidebar.download_button(
        label="📥 Descargar Estadísticas (CSV)",
        data=csv_data,
        file_name="estadisticas_cambio_penaflor.csv",
        mime="text/csv",
        help="Descarga tabla completa con estadísticas de las 100 zonas"
    )
else:
    st.sidebar.info("Estadísticas no disponibles")

# Descarga de ranking
if ranking is not None:
    csv_ranking = ranking.to_csv(index=False).encode('utf-8')
    
    st.sidebar.download_button(
        label="📥 Descargar Ranking (CSV)",
        data=csv_ranking,
        file_name="ranking_hotspots_penaflor.csv",
        mime="text/csv",
        help="Descarga ranking de zonas críticas"
    )

# Descarga de evolución temporal
if temporal is not None:
    csv_temporal = temporal.to_csv(index=False).encode('utf-8')
    
    st.sidebar.download_button(
        label="📥 Descargar Serie Temporal (CSV)",
        data=csv_temporal,
        file_name="evolucion_temporal_penaflor.csv",
        mime="text/csv",
        help="Descarga serie temporal de índices 2018-2024"
    )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><b>Monitor de Cambio Urbano - Peñaflor</b></p>
    <p>Desarrollado con Python, Streamlit, Google Earth Engine y Sentinel-2</p>
    <p>Universidad de Santiago de Chile | 2025</p>
    <p style='font-size: 0.8rem; margin-top: 1rem;'>
        Byron Caices - Laboratorio de Desarrollo de Aplicaciones Geoinformáticas
    </p>
</div>
""", unsafe_allow_html=True)
