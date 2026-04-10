# 3D Directional Drilling Engine 🚀

🌍 Lesen auf: [English](README.md) | [Español](README.es.md) | [Deutsch](README.de.md)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Entwickelt von:** Emilio Barrera (Maschinenbauingenieur)

## 🎯 Projektbeschreibung
Industrietaugliches Web-Tool zur 3D-Berechnung und Visualisierung von Bohrlochverläufen in der Erdölindustrie. Im Gegensatz zu einfachen geometrischen Näherungen implementiert dieser Motor die **vektorisierte Minimum-Krümmungs-Methode**, die durch NumPy für die effiziente Verarbeitung großer Mengen an Richtbohrdaten optimiert ist.

Entwickelt zur Unterstützung bei der Trajektorienanalyse, der Bewertung der Dogleg-Severity (DLS) und der Bohrplanung.

### ✨ Hauptmerkmale
* **Multiformat-Unterstützung:** Robustes Einlesen und automatische Bereinigung von rohen Feldberichten in den Formaten `.csv`, `.txt` und `.las` (Log ASCII Standard).
* **Internationalisierung (i18n):** Voll funktionsfähige Schnittstelle in 3 Sprachen (Englisch 🇬🇧, Spanisch 🇪🇸 und Deutsch 🇩🇪) mit Speicherpersistenz, um beim Sprachwechsel keinen Fortschritt zu verlieren.
* **Integriertes Golden Dataset:** Automatische Erkennung von Testdateien. Enthält reale Daten aus dem **Volve-Feld (Equinor)**, die mit einem Klick ausgeführt werden können.
* **Präzisionsmodul:** Hochpräzise direktionsbezogene Interpolationsschnittstelle zur Analyse von Neigung, Azimut und Koordinaten in bestimmten Zielteufen.

## 🧪 Mathematische Validierung (Equinor Volve Golden Dataset)
Die mathematische Integrität ist die Säule dieses Projekts. Der Berechnungsalgorithmus wurde rigoros mit dem öffentlichen Datensatz des **Volve-Feldes (Equinor)** validiert.
* **Basisalgorithmus:** Minimum-Krümmungs-Methode (Vektorisierte Implementierung).
* **Präzision:** Relativer Fehler < 0.001% im Vergleich zu den Ergebnissen von Standard-Industriesoftware.
* **Qualitätssicherung (QA):** 2 automatisierte Unit-Tests mit `pytest`, die die Zuverlässigkeit der Trajektorien- und Dogleg-Severity (DLS)-Berechnung im Vergleich zum *Golden Dataset* nach ISCWSA-Standards garantieren.

## 🛠️ Technologie-Stack
* **Mathematischer Kern:** `NumPy`, `SciPy`, `Pandas` (Hochgeschwindigkeits-Matrix- und Vektorberechnung).
* **Direktional-Parser:** `lasio` zur Metadatenextraktion und Speicherpuffer-Decoder (`io.BytesIO`).
* **Benutzeroberfläche:** `Streamlit`.
* **Visualisierung:** `Plotly` (Rendern von interaktiven 3D-Modellen und Belastungsprofilen).
* **Testing:** `Pytest` für Validierung und CI/CD.

## 🚀 Lokale Installation und Nutzung

1. Repository klonen:
```bash
    git clone https://github.com/ejbo2001/3D-directional-drilling-engine.git
    cd 3D-directional-drilling-engine
```
2. Virtuelle Umgebung erstellen und Abhängigkeiten installieren:
```bash
    python -m venv venv
    # Unter Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
```
3. Anwendung starten:
```bash
    streamlit run src/app.py
```