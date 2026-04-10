# 3D Directional Drilling Engine 🚀

🌍 Leer en: [English](README.md) | [Español](README.es.md) | [Deutsch](README.de.md)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Desarrollado por:** Emilio Barrera (Ingeniero Mecánico)

## 🎯 Descripción del Proyecto
Herramienta web de grado industrial para el cálculo y visualización 3D de trayectorias de pozos petroleros. A diferencia de aproximaciones geométricas básicas, este motor implementa el **Método de Curvatura Mínima Vectorizado**, optimizado mediante NumPy para el procesamiento eficiente de grandes volúmenes de datos direccionales.

Diseñado para asistir en el análisis de trayectorias, evaluación de severidad (DLS) y planificación de perforación.

### ✨ Características Principales
* **Soporte Multi-formato:** Lectura robusta y limpieza automática de reportes de campo crudos en formatos `.csv`, `.txt` y `.las` (Log ASCII Standard).
* **Internacionalización (i18n):** Interfaz completamente funcional en 3 idiomas (Español 🇪🇸, Inglés 🇬🇧 y Alemán 🇩🇪) con persistencia de memoria para no perder el progreso al cambiar de idioma.
* **Golden Dataset Integrado:** Detección automática de archivos de prueba. Incluye datos reales del campo **Volve (Equinor)** listos para ser ejecutados con un solo clic.
* **Módulo de Precisión:** Interfaz de interpolación direccional de alta precisión para analizar inclinación, azimut y coordenadas en profundidades objetivo específicas.

## 🧪 Validación Matemática (Equinor Volve Golden Dataset)
La integridad matemática es el pilar de este proyecto. El motor de cálculo ha sido rigurosamente validado utilizando el dataset público del campo **Volve (Equinor)**.
* **Algoritmo Base:** Método de Curvatura Mínima (Vectorized Implementation).
* **Precisión:** Error relativo < 0.001% en comparación con los resultados de perfiles direccionales de software comercial estándar de la industria.
* **Aseguramiento de Calidad (QA):** 2 pruebas unitarias automatizadas con `pytest` que garantizan la fiabilidad del cálculo de trayectoria y Dogleg Severity (DLS) frente al *Golden Dataset* bajo estándares ISCWSA.

## 🛠️ Stack Tecnológico
* **Core Matemático:** `NumPy`, `SciPy`, `Pandas` (Cálculo matricial y vectorial de alta velocidad).
* **Parser Direccional:** `lasio` para extracción de metadata y decodificadores de buffers en memoria (`io.BytesIO`).
* **Interfaz de Usuario:** `Streamlit`.
* **Visualización:** `Plotly` (Renderizado de modelos 3D interactivos y perfiles de severidad).
* **Testing:** `Pytest` para validación y CI/CD.

## 🚀 Instalación y Uso Local

1. Clonar el repositorio:
```bash
    git clone https://github.com/ejbo2001/3D-directional-drilling-engine.git
    cd 3D-directional-drilling-engine
```
2. Crear entorno virtual e instalar dependencias:
```bash
    python -m venv venv
    # En Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
```
3. Ejecutar la aplicación:
```bash
    streamlit run src/app.py
```