# 3D Directional Drilling Engine 🚀

🌍 Read this in: [English](README.md) | [Español](README.es.md) | [Deutsch](README.de.md)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Developed by:** Emilio Barrera (Mechanical Engineer)

## 🎯 Project Description
Industrial-grade web tool for the 3D calculation and visualization of oil well trajectories. Unlike basic geometric approximations, this engine implements the **Vectorized Minimum Curvature Method**, optimized using NumPy for the efficient processing of large volumes of directional data.

Designed to assist in trajectory analysis, Dogleg Severity (DLS) evaluation, and drilling planning.

### ✨ Main Features
* **Multi-format Support:** Robust parsing and automatic cleaning of raw field reports in `.csv`, `.txt`, and `.las` (Log ASCII Standard) formats.
* **Internationalization (i18n):** Fully functional interface in 3 languages (English 🇬🇧, Spanish 🇪🇸, and German 🇩🇪) with state persistence to avoid losing progress when switching languages.
* **Integrated Golden Dataset:** Automatic detection of test files. Includes real data from the **Volve field (Equinor)** ready to be executed with a single click.
* **Precision Module:** High-precision directional interpolation interface to analyze inclination, azimuth, and coordinates at specific target depths.

## 🧪 Mathematical Validation (Equinor Volve Golden Dataset)
Mathematical integrity is the pillar of this project. The calculation engine has been rigorously validated using the public dataset from the **Volve field (Equinor)**.
* **Core Algorithm:** Minimum Curvature Method (Vectorized Implementation).
* **Precision:** Relative error < 0.001% compared to directional profile results from industry-standard commercial software.
* **Quality Assurance (QA):** 2 automated unit tests using `pytest` that guarantee the reliability of the trajectory and Dogleg Severity (DLS) calculation against the *Golden Dataset* under ISCWSA standards.

## 🛠️ Tech Stack
* **Mathematical Core:** `NumPy`, `SciPy`, `Pandas` (High-speed matrix and vector calculus).
* **Directional Parser:** `lasio` for metadata extraction and memory buffer decoders (`io.BytesIO`).
* **User Interface:** `Streamlit`.
* **Visualization:** `Plotly` (Interactive 3D model rendering and severity profiles).
* **Testing:** `Pytest` for validation and CI/CD.

## 🚀 Local Installation & Usage

1. Clone the repository:
```bash
    git clone https://github.com/ejbo2001/3D-directional-drilling-engine.git
    cd 3D-directional-drilling-engine
```
2. Create a virtual environment and install dependencies:
```bash
    python -m venv venv
    # On Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
```
3. Run the application:
```bash
    streamlit run src/app.py
```
