import sys
import os
import pytest
import numpy as np
from numpy.testing import assert_allclose

# --- SOLUCIÓN DE RUTAS (PATH INJECTION) ---
# Le decimos a Python que añada la carpeta 'src' a su radar de búsqueda de módulos.
# Así podrá encontrar 'engine.py' sin importar desde dónde ejecutemos pytest.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Ahora sí, importamos sin problemas
from engine import calcular_curvatura_minima_vectorizado 

def test_volumen_curvatura_minima_volve_15_9_F_1():
    # 1. DATOS DE ENTRADA (Sección Vertical Inicial del Pozo)
    md_vals = np.array([145.90, 150.15, 160.45, 170.04, 179.79])
    inc_vals = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    azi_vals = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    
    # 2. RESULTADOS OFICIALES ESPERADOS 
    tvd_oficial = np.array([145.90, 150.15, 160.45, 170.04, 179.79]) 
    ns_oficial = np.array([3.17, 3.17, 3.17, 3.17, 3.17])
    ew_oficial = np.array([-3.53, -3.53, -3.53, -3.53, -3.53])

    # 3. EJECUTAR TU MOTOR MATEMÁTICO
    tvd_calc, ns_calc, ew_calc, dls_calc = calcular_curvatura_minima_vectorizado(
        md=md_vals,
        inc_deg=inc_vals,
        azi_deg=azi_vals,
        tvd_tie=145.90, 
        ns_tie=3.17,    # Coordenada Norte inicial 
        ew_tie=-3.53    # Coordenada Este inicial 
    )

    # 4. VALIDACIÓN
    assert_allclose(tvd_calc, tvd_oficial, atol=0.1, err_msg="Error en TVD")
    assert_allclose(ns_calc, ns_oficial, atol=0.1, err_msg="Error en N/S")
    assert_allclose(ew_calc, ew_oficial, atol=0.1, err_msg="Error en E/W")

    print("✅ Prueba de Curvatura Mínima superada con éxito (Sección Vertical).")


def test_curvatura_minima_seccion_curva_3D():
    """
    Prueba de Estrés: Sección de Construcción y Giro (Build & Turn).
    Evalúa la robustez del cálculo del Dogleg (Alpha) y proyecciones trigonométricas.
    """
    # 1. DATOS DE ENTRADA (Kick-Off agresivo)
    md_vals = np.array([1000.0, 1100.0, 1200.0])
    inc_vals = np.array([0.0, 10.0, 20.0])
    azi_vals = np.array([0.0, 45.0, 90.0])
    
    # 2. RESULTADOS ESPERADOS (Calculados con rigor ISCWSA)
    tvd_oficial = np.array([1000.0, 1099.49, 1196.29]) 
    ns_oficial = np.array([0.0, 6.15, 12.32])
    ew_oficial = np.array([0.0, 6.15, 29.53])

    # 3. EJECUTAR MOTOR (Amarre en 1000m vertical)
    tvd_calc, ns_calc, ew_calc, dls_calc = calcular_curvatura_minima_vectorizado(
        md=md_vals,
        inc_deg=inc_vals,
        azi_deg=azi_vals,
        tvd_tie=1000.0, 
        ns_tie=0.0,    
        ew_tie=0.0    
    )

    # 4. VALIDACIÓN ESTRICTA (Tolerancia de 10 centímetros)
    assert_allclose(tvd_calc, tvd_oficial, atol=0.1, err_msg="¡Fallo masivo en TVD durante la curva!")
    assert_allclose(ns_calc, ns_oficial, atol=0.1, err_msg="¡Fallo masivo en N/S durante la curva!")
    assert_allclose(ew_calc, ew_oficial, atol=0.1, err_msg="¡Fallo masivo en E/W durante la curva!")
    
    print("✅ Prueba de Estrés superada: El motor domina las curvas 3D.")