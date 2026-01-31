# Informe Final - Análisis de Cambios de Uso de Suelo en Peñaflor

## 📄 Descripción

Informe final del proyecto de análisis multitemporal de cambios de uso de suelo en la comuna de Peñaflor (2018-2024) utilizando imágenes Sentinel-2 y técnicas de teledetección.

**Estudiante:** Byron Caices  
**Profesor:** Francisco Parra  
**Curso:** Teledetección y SIG  
**Fecha:** Enero 2026

---

## 🗂️ Estructura del Documento

El informe está dividido en las siguientes secciones:

1. **Introducción** - Contexto, área de estudio, objetivos
2. **Metodología** - Adquisición de datos, procesamiento, análisis
3. **Resultados** - Hallazgos principales con mapas, gráficos y tablas
4. **Discusión** - Interpretación, validación, comparación con estudios previos
5. **Conclusiones** - Síntesis, logros, limitaciones y recomendaciones
6. **Anexos** - Especificaciones técnicas, código, tablas complementarias

---

## 🛠️ Compilación del PDF

### Requisitos Previos

Necesitas tener instalado LaTeX en tu sistema. Las opciones recomendadas son:

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt-get install texlive-full biber
  ```

- **macOS:**
  ```bash
  brew install --cask mactex
  ```

- **Windows:**
  Descargar e instalar [MiKTeX](https://miktex.org/download) o [TeX Live](https://www.tug.org/texlive/)

### Compilación

Desde el directorio `informe_final/`, ejecuta:

```bash
# Compilación completa (con bibliografía)
pdflatex informe.tex
biber informe
pdflatex informe.tex
pdflatex informe.tex
```

O usa el script automatizado:

```bash
chmod +x compilar.sh
./compilar.sh
```

El archivo `informe.pdf` se generará en el mismo directorio.

### Compilación en Overleaf (Alternativa Online)

Si prefieres no instalar LaTeX localmente:

1. Ve a [Overleaf](https://www.overleaf.com/)
2. Crea una cuenta gratuita
3. Sube todos los archivos de la carpeta `informe_final/`
4. Compila directamente en el navegador

---

## 📊 Contenido del Informe

### Sección 1: Introducción (2 páginas)
- Contexto de periurbanización en Peñaflor
- Descripción del área de estudio (202 km²)
- Justificación del proyecto
- Objetivos general y específicos

### Sección 2: Metodología (4 páginas)
- **Fase 1:** Adquisición de imágenes Sentinel-2 (4 años)
- **Fase 2:** Cálculo de índices espectrales (NDVI, NDBI, NDWI, BSI)
- **Fase 3:** Métodos de detección de cambios (Multicriterio, Z-Score, Random Forest)
- **Fase 4:** Análisis zonal con grilla de 100 celdas
- **Fase 5:** Dashboard interactivo Streamlit

### Sección 3: Resultados (3 páginas)
- Estadísticas de índices espectrales por año
- Áreas de cambio detectadas (1,689 ha urbanizadas)
- Ranking de hotspots críticos (Top 10 zonas)
- Evolución temporal de NDVI/NDBI
- Clasificación de zonas por intensidad de cambio

### Sección 4: Discusión (3 páginas)
- Interpretación de patrones de urbanización
- Comparación con Plan Regulador Comunal (226% de desvío)
- Validación con Google Earth (90% de precisión)
- Limitaciones metodológicas y de datos
- Implicancias para gestión territorial

### Sección 5: Conclusiones (2 páginas)
- Síntesis de hallazgos principales
- Cumplimiento de objetivos
- Contribuciones metodológicas y aplicadas
- Recomendaciones para autoridades y futuros estudios
- Reflexión final sobre democratización de teledetección

### Anexos (5 páginas)
- Especificaciones técnicas (hardware, software)
- Estructura del repositorio
- Código ejemplo de cálculo de NDVI
- Fórmulas de índices espectrales
- Matriz de confusión de validación
- Estadísticas descriptivas completas
- Comparación de métodos de detección
- Enlaces y recursos

---

## 📈 Datos Destacados

- **Urbanización detectada:** 1,689 ha (2018-2024)
- **Tasa de crecimiento:** 1.16% anual
- **Pérdida neta de vegetación:** 2,086 ha
- **Zonas críticas:** 18 zonas (18% del territorio)
- **Precisión validada:** 90% (Google Earth)
- **Correlación NDVI-NDBI:** -0.87 (p < 0.001)

---

## 🔗 Referencias Principales

El informe incluye 24 referencias bibliográficas en formato APA, incluyendo:

- Documentación oficial Sentinel-2 (ESA Copernicus)
- Plan Regulador Comunal de Peñaflor (2015)
- Estudios de periurbanización en Chile (Romero et al., Inostroza et al.)
- Papers fundacionales de índices espectrales (Tucker, Zha, Gao)
- Documentación técnica de bibliotecas Python (Rasterio, GeoPandas, Streamlit)

---

## ✅ Checklist de Entrega

- [x] Informe LaTeX completo (5 secciones + anexos)
- [x] Bibliografía en formato APA (24 referencias)
- [x] Portada con datos institucionales
- [x] Tabla de contenidos automática
- [ ] Compilación exitosa a PDF
- [ ] Figuras/mapas incluidos en carpeta images/
- [ ] Revisión ortográfica y gramatical

---

## 📦 Archivos Incluidos

```
informe_final/
├── informe.tex              # Documento principal
├── bibliografia.bib         # Referencias en BibTeX
├── chapters/
│   ├── Seccion1.tex        # Introducción
│   ├── Seccion2.tex        # Metodología
│   ├── Seccion3.tex        # Resultados
│   ├── Seccion4.tex        # Discusión
│   ├── Seccion5.tex        # Conclusiones
│   └── Anexos.tex          # Anexos técnicos
├── images/
│   └── Logo_Usach.pdf      # Logo institucional
├── compilar.sh             # Script de compilación
└── README.md               # Este archivo
```

---

## 🎯 Próximos Pasos

1. **Agregar figuras:** Copiar mapas y gráficos a `images/`
   - Mapa de ubicación de Peñaflor
   - Mapa de cambios clasificado
   - Gráficos de evolución temporal
   - Screenshots del dashboard

2. **Compilar PDF:** Ejecutar `./compilar.sh`

3. **Revisar:** Verificar que todas las referencias, figuras y tablas se muestren correctamente

4. **Entregar:** Subir PDF final junto con código fuente

---

## 📧 Contacto

**Byron Caices**  
GitHub: [@ByronCaices](https://github.com/ByronCaices)  
Repositorio: [geo-lab-2](https://github.com/ByronCaices/geo-lab-2)

---

**Licencia:** Creative Commons BY-SA 4.0  
**Última actualización:** Enero 2026
