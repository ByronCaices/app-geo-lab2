#!/bin/bash

# Script de compilación del informe LaTeX con bibliografía

echo "🚀 Compilando informe LaTeX..."
echo ""

# Primera compilación (genera archivos auxiliares)
echo "📝 Paso 1/4: Primera compilación de LaTeX..."
pdflatex -interaction=nonstopmode informe.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Paso 1 completado"
else
    echo "   ❌ Error en paso 1. Verifica errores con: pdflatex informe.tex"
    exit 1
fi

# Compilar bibliografía con biber
echo "📚 Paso 2/4: Compilando bibliografía con biber..."
biber informe > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Paso 2 completado"
else
    echo "   ⚠️  Warning en bibliografía (puede ser normal si no hay citas)"
fi

# Segunda compilación (incorpora referencias)
echo "📝 Paso 3/4: Segunda compilación de LaTeX..."
pdflatex -interaction=nonstopmode informe.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Paso 3 completado"
else
    echo "   ❌ Error en paso 3"
    exit 1
fi

# Tercera compilación (finaliza referencias cruzadas)
echo "📝 Paso 4/4: Tercera compilación de LaTeX (final)..."
pdflatex -interaction=nonstopmode informe.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Paso 4 completado"
else
    echo "   ❌ Error en paso 4"
    exit 1
fi

# Limpiar archivos auxiliares
echo ""
echo "🧹 Limpiando archivos auxiliares..."
rm -f *.aux *.log *.out *.toc *.bbl *.blg *.bcf *.run.xml

echo ""
echo "✅ ¡Compilación exitosa!"
echo "📄 Archivo generado: informe.pdf"
echo ""
echo "📊 Información del PDF:"
ls -lh informe.pdf
echo ""
echo "Para ver el PDF ejecuta: xdg-open informe.pdf"
