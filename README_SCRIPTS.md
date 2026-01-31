# 📋 Compilador y Editor de Informe - Geo-Lab-2

Scripts bash para facilitar la compilación y edición del informe final del proyecto de análisis multitemporal de cambios de uso de suelo en Peñaflor.

## 📦 Instalación Rápida

```bash
# Hacer los scripts ejecutables (ya está hecho)
chmod +x compilar_informe.sh
chmod +x editar_informe.sh
```

## 🚀 Uso

### Script 1: `compilar_informe.sh`

Script principal para compilar el informe LaTeX.

#### Opciones disponibles:

```bash
# Compilación completa (default)
./compilar_informe.sh compile
# o simplemente:
./compilar_informe.sh

# Recompilación desde cero (limpia + compila)
./compilar_informe.sh rebuild

# Compilación rápida (solo pdflatex, sin biber)
./compilar_informe.sh quick

# Limpiar archivos temporales
./compilar_informe.sh clean

# Verificar dependencias (pdflatex, biber)
./compilar_informe.sh check

# Mostrar estadísticas del PDF
./compilar_informe.sh stats

# Abrir PDF generado
./compilar_informe.sh view

# Ayuda
./compilar_informe.sh help
```

#### Flujo de compilación automático:

1. ✅ Verifica dependencias (pdflatex, biber)
2. 🧹 Limpia archivos temporales
3. 📄 Primera compilación pdflatex (genera .bcf)
4. 📚 Procesa referencias con biber
5. 📄 Segunda y tercera compilación pdflatex
6. ✓ Verifica errores en el log
7. 📊 Muestra estadísticas (páginas, palabras)
8. 🎯 Abre el PDF (opcional)

#### Ejemplo de uso típico:

```bash
# Al terminar de editar el informe
./compilar_informe.sh

# Para recompilar rápidamente después de ediciones menores
./compilar_informe.sh quick

# Si hay dudas sobre dependencias
./compilar_informe.sh check
```

---

### Script 2: `editar_informe.sh`

Menú interactivo para editar archivos del informe.

#### Uso:

```bash
./editar_informe.sh
```

#### Opciones del menú:

```
1. Portada y Tabla de Contenidos (informe.tex)
2. Sección 1 - Introducción
3. Sección 2 - Metodología
4. Sección 3 - Resultados
5. Sección 4 - Discusión
6. Sección 5 - Conclusiones
7. Anexos
8. Bibliografía (referencias.bib)
9. Compilar informe
10. Crear respaldo (.bak)
11. Ver cambios (git diff)
0. Salir
```

#### Características:

- 📝 Interfaz de menú intuitiva
- 💾 Crea backup automático antes de editar
- ⚙️ Usa el editor del sistema ($EDITOR, nano, vim, vi)
- 🔄 Compilación integrada
- 💿 Gestión de respaldos
- 📊 Comparación con git

#### Ejemplo de uso:

```bash
./editar_informe.sh
# → Selecciona 4 (Sección 3 - Resultados)
# → Se abre en tu editor predeterminado
# → Al guardar, pregunta si deseas compilar
```

---

## 📋 Estructura de Archivos

```
geo-lab-2/
├── compilar_informe.sh          # Script de compilación
├── editar_informe.sh            # Script de edición
├── README_SCRIPTS.md            # Este archivo
│
└── informe_final/
    ├── informe.tex              # Archivo principal
    ├── bibliografia.bib         # Referencias BibTeX
    ├── informe.pdf              # PDF generado ⭐
    │
    ├── chapters/
    │   ├── Seccion1.tex         # Introducción
    │   ├── Seccion2.tex         # Metodología
    │   ├── Seccion3.tex         # Resultados
    │   ├── Seccion4.tex         # Discusión
    │   ├── Seccion5.tex         # Conclusiones
    │   └── Anexos.tex           # Anexos
    │
    ├── images/                  # Figuras y gráficos
    │   ├── ndvi_2018.png
    │   ├── ndvi_2020.png
    │   ├── ndvi_2022.png
    │   ├── ndvi_2024.png
    │   ├── evolucion_temporal.png
    │   └── ...
    │
    └── backups/                 # Respaldos automáticos
        └── backup_20260131_*/
```

---

## 🔧 Dependencias

Los scripts requieren:

- **pdflatex**: Compilador LaTeX
- **biber**: Procesador de referencias BibTeX
- **pdfinfo** (opcional): Para mostrar info del PDF
- **pdftotext** (opcional): Para estadísticas del documento

### Instalación en Linux (Ubuntu/Debian):

```bash
# Instalación completa de LaTeX
sudo apt-get update
sudo apt-get install texlive-full

# Esto incluye:
# - pdflatex
# - biber
# - pdfinfo
# - pdftotext
```

### Instalación en macOS:

```bash
# Con Homebrew
brew install basictex
sudo tlmgr update --self
sudo tlmgr install biber

# O completa (MacTeX - ~4GB)
brew install mactex
```

---

## 🎯 Flujo de Trabajo Recomendado

### Cuando necesitas editar el informe:

```bash
# 1. Abre el editor interactivo
./editar_informe.sh

# 2. Selecciona la sección a editar (ej: opción 3)

# 3. El script abre tu editor predeterminado
# 4. Editas el archivo
# 5. Guardas los cambios

# 6. Cuando termina la edición, pregunta si compilar
# → Responde "s" para compilar automáticamente

# 7. El script verifica errores y abre el PDF
```

### Compilación rápida después de editar:

```bash
# Para cambios menores (evita procesar referencias)
./compilar_informe.sh quick

# Para compilación completa (recomendado)
./compilar_informe.sh compile
```

### Crear respaldo antes de cambios grandes:

```bash
./editar_informe.sh
# Selecciona opción 10 (Crear respaldo)
# Se guardará en informe_final/backups/backup_YYYYMMDD_HHMMSS/
```

---

## 📊 Ejemplos de Uso Práctico

### Escenario 1: Editar Resultados y Compilar

```bash
$ ./editar_informe.sh
# → Selecciona 4 (Sección 3 - Resultados)
# → Edita el archivo en nano/vim
# → Presiona Enter para terminar
# → Se pregunta si compilar → "s"
# → Se compila automáticamente y abre el PDF
```

### Escenario 2: Actualizar Bibliografía

```bash
$ ./editar_informe.sh
# → Selecciona 8 (Bibliografía)
# → Edita referencias.bib en tu editor
# → Guarda cambios
# → Compila
$ ./compilar_informe.sh
```

### Escenario 3: Recompilación Rápida

```bash
# Después de múltiples ediciones menores
$ ./compilar_informe.sh quick

# Si hay problemas, compilación completa:
$ ./compilar_informe.sh rebuild
```

### Escenario 4: Ver Qué Cambió

```bash
$ ./editar_informe.sh
# → Selecciona 11 (Ver cambios con git diff)
# → Muestra estadísticas de cambios
# → Opción de ver detalles línea por línea
```

---

## 🐛 Solución de Problemas

### Problema: "pdflatex: command not found"

```bash
# Solución: Instalar TeX Live
sudo apt-get install texlive-full

# O verificar instalación
./compilar_informe.sh check
```

### Problema: "biber not found"

```bash
# Solución: Instalar biber por separado
sudo apt-get install biber

# O con tlmgr (si tienes LaTeX)
sudo tlmgr install biber
```

### Problema: Citas aparecen como "[?]"

```bash
# Solución: Compilación completa (no rápida)
./compilar_informe.sh rebuild

# Esto ejecuta: clean → pdflatex → biber → pdflatex → pdflatex
```

### Problema: El script no es ejecutable

```bash
# Solución: Hacer ejecutable
chmod +x compilar_informe.sh
chmod +x editar_informe.sh
```

### Problema: Editor no se abre

```bash
# Solución: Establecer editor predeterminado
export EDITOR=nano
./editar_informe.sh

# O permanentemente, agrega a ~/.bashrc:
echo 'export EDITOR=nano' >> ~/.bashrc
source ~/.bashrc
```

---

## 📈 Estadísticas útiles

### Ver información del PDF:

```bash
./compilar_informe.sh stats
# Muestra: palabras, caracteres, páginas
```

### Ver últimos cambios:

```bash
$ cd /home/byron-caices/Escritorio/geo-lab-2
$ git log --oneline informe_final/ | head -10
```

### Contar palabras de una sección:

```bash
pdftotext informe_final/informe.pdf - | wc -w
```

---

## 💡 Tips y Trucos

### Atajo rápido: crear función en .bashrc

```bash
# Agrega esto a ~/.bashrc
alias compile="cd /path/to/geo-lab-2 && ./compilar_informe.sh"
alias edit="cd /path/to/geo-lab-2 && ./editar_informe.sh"

# Luego puedes usar:
$ compile      # en lugar de ./compilar_informe.sh
$ edit         # en lugar de ./editar_informe.sh
```

### Ver errores de compilación en tiempo real:

```bash
# En lugar de compilación silenciosa
cd informe_final
pdflatex -interaction=nonstopmode informe.tex | grep -A 5 "^!"
```

### Buscar texto en el informe:

```bash
$ grep -n "urbanización" informe_final/chapters/*.tex
# Muestra dónde aparece "urbanización" con número de línea
```

---

## 📝 Notas Importantes

- ⚠️ Los scripts crear respaldos automáticos con timestamp
- ⚠️ Los archivos `.bak_*` NO se incluyen en git
- ✅ Siempre es seguro ejecutar `./compilar_informe.sh clean` y `rebuild`
- ✅ Las citas funcionan solo después de compilación completa (con biber)
- ✅ Usa `git diff` para revisar cambios antes de hacer commit

---

## 👨‍💻 Autor

Byron Caices | Proyecto Geo-Lab-2 | Enero 2026

```
📍 Ubicación: /home/byron-caices/Escritorio/geo-lab-2/
📧 Para preguntas o mejoras, contacta al autor del proyecto
```

---

## 📄 Licencia

Estos scripts se distribuyen bajo la misma licencia que el proyecto Geo-Lab-2 (Creative Commons BY-SA 4.0)
