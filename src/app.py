import streamlit as st
import pandas as pd
import numpy as np  
import plotly.graph_objects as go
import lasio
import io
import os
from engine import calcular_curvatura_minima_vectorizado

# --- DICCIONARIO DE IDIOMAS (i18n) ---
TEXTS = {
    "es": {
        "title": "Motor Direccional 3D 🎯",
        "subtitle": "Validación de trayectorias mediante Curvatura Mínima Vectorizada.",
        "lang_selector": "🌐 Idioma / Language",
        "opt_a": "📁 Opción A: Sube tu archivo",
        "opt_a_desc": "Formatos: .csv, .las, .txt",
        "opt_b": "🚀 Opción B: Golden Dataset",
        "opt_b_desc": "Prueba con datos de Equinor (Volve):",
        "none": "Selecciona un dataset...",
        "preview_expander": "🔍 Ver tabla de datos originales",
        "download_raw": "📥 Descargar Dataset Crudo (.csv)",
        "mapping_title": "Mapeo de Variables",
        "not_avail": "No disponible",
        "btn_run": "▶ Ejecutar Cálculo Direccional",
        "processing": "Procesando matriz espacial...",
        "success": "¡Cálculo vectorizado exitoso!",
        "plot_calc": "Cálculo Propio (Curvatura Mínima)",
        "plot_orig": "Trayectoria Original",
        "err_title": "Análisis de Error Espacial",
        "err_max": "Diferencia máxima detectada:",
        "dls_title": "Severidad (Dogleg Severity)",
        "dls_max": "DLS Máximo detectado:",
        "dls_limit": "Límite de Fatiga (4°/30m)",
        "interp_title": "🎯 Módulo de Interpolación",
        "depth_target": "Profundidad Objetivo (MD)",
        "export_title": "📥 Exportar Resultados",
        "download_val": "Descargar Trayectoria Validada (.csv)",
        "waiting": "Esperando archivo o selección de datos para iniciar."
    },
    "en": {
        "title": "3D Directional Engine 🎯",
        "subtitle": "Wellbore trajectory validation using Vectorized Minimum Curvature.",
        "lang_selector": "🌐 Language",
        "opt_a": "📁 Option A: Upload File",
        "opt_a_desc": "Supported: .csv, .las, .txt",
        "opt_b": "🚀 Option B: Golden Dataset",
        "opt_b_desc": "Test with Equinor (Volve) data:",
        "none": "Select a dataset...",
        "preview_expander": "🔍 View raw data table",
        "download_raw": "📥 Download Raw Dataset (.csv)",
        "mapping_title": "Curve Mapping",
        "not_avail": "Not available",
        "btn_run": "▶ Run Directional Calculation",
        "processing": "Processing spatial matrix...",
        "success": "Vectorized calculation successful!",
        "plot_calc": "Computed Trajectory (Min. Curvature)",
        "plot_orig": "Original Trajectory",
        "err_title": "Spatial Error Analysis",
        "err_max": "Maximum difference detected:",
        "dls_title": "Dogleg Severity (DLS)",
        "dls_max": "Maximum DLS detected:",
        "dls_limit": "Fatigue Limit (4°/30m)",
        "interp_title": "🎯 Interpolation Module",
        "depth_target": "Target Depth (MD)",
        "export_title": "📥 Export Results",
        "download_val": "Download Validated Trajectory (.csv)",
        "waiting": "Waiting for file upload or data selection to start."
    },
    "de": {
        "title": "3D-Richtbohrmotor 🎯",
        "subtitle": "Bohrlochverlauf-Validierung mittels vektorisierter Minimum-Krümmung.",
        "lang_selector": "🌐 Sprache",
        "opt_a": "📁 Option A: Datei hochladen",
        "opt_a_desc": "Unterstützt: .csv, .las, .txt",
        "opt_b": "🚀 Option B: Golden Dataset",
        "opt_b_desc": "Testen mit Equinor (Volve) Daten:",
        "none": "Datensatz auswählen...",
        "preview_expander": "🔍 Rohdatentabelle anzeigen",
        "download_raw": "📥 Rohdaten herunterladen (.csv)",
        "mapping_title": "Kurvenzuordnung",
        "not_avail": "Nicht verfügbar",
        "btn_run": "▶ Richtbohrberechnung ausführen",
        "processing": "Räumliche Matrix wird verarbeitet...",
        "success": "Vektorisierte Berechnung erfolgreich!",
        "plot_calc": "Berechnete Trajektorie (Min. Krümmung)",
        "plot_orig": "Ursprüngliche Trajektorie",
        "err_title": "Räumliche Fehleranalyse",
        "err_max": "Maximale erkannte Abweichung:",
        "dls_title": "Bohrlochkrümmung (Dogleg Severity)",
        "dls_max": "Maximaler erkannter DLS:",
        "dls_limit": "Ermüdungsgrenze (4°/30m)",
        "interp_title": "🎯 Interpolationsmodul",
        "depth_target": "Zielteufe (MD)",
        "export_title": "📥 Ergebnisse exportieren",
        "download_val": "Validierte Trajektorie herunterladen (.csv)",
        "waiting": "Warten auf Datei-Upload oder Datenauswahl zum Starten."
    }
}


# --- CLASE AUXILIAR PARA REUTILIZAR EL PARSER ---
class MockFile(io.BytesIO):
    """Simula un archivo subido por Streamlit para leer archivos locales con la misma función."""
    def __init__(self, filepath):
        with open(filepath, 'rb') as f:
            content = f.read()
        super().__init__(content)
        self.name = os.path.basename(filepath)
        self.size = len(content)

# ESTO DEBE IR AQUÍ ARRIBA, ANTES DE CUALQUIER OTRA COSA DE UI
st.set_page_config(page_title="Directional Engine Pro", layout="wide", initial_sidebar_state="collapsed")


# --- 1. GESTIÓN DE DATOS (FUNCIONES) ---
@st.cache_data
def load_raw_data(_file, file_name):
    try:
        if file_name.lower().endswith('.las'):
            string_data = _file.getvalue().decode("utf-8", errors="replace")
            las = lasio.read(string_data)
            df = las.df().reset_index()
            
        elif file_name.lower().endswith('.txt'):
            content = _file.getvalue().decode("utf-8", errors="replace").splitlines()
            start_idx = 0
            for i, line in enumerate(content):
                if "MD" in line.upper() and "INC" in line.upper():
                    start_idx = i
                    break
            clean_text = "\n".join(content[start_idx:])
            df = pd.read_csv(io.StringIO(clean_text), sep=r'\s+')
            if isinstance(df.iloc[0, 0], str) and any(char in df.iloc[0, 0] for char in ['[', '(']):
                df = df.drop(0).reset_index(drop=True)
                df = df.apply(pd.to_numeric, errors='ignore')

        elif file_name.lower().endswith('.csv'):
            df = pd.read_csv(_file, sep=None, engine='python')
        else:
            raise ValueError("Formato de archivo no soportado.")
            
        return df, None
    except Exception as e:
        return None, f"Error: {str(e)}"

# --- 2. INTERFAZ Y SELECTOR DE IDIOMA INTEGRADO ---
col_title, col_lang = st.columns([5, 1])

with col_lang:
    st.write("") # Espaciador para centrar verticalmente
    lang_choice = st.selectbox(
        "🌐", 
        options=["es", "en", "de"], 
        format_func=lambda x: {"es": "🇪🇸 Español", "en": "🇬🇧 English", "de": "🇩🇪 Deutsch"}[x],
        label_visibility="collapsed",
        key="lang_selector" # La Key evita que Streamlit borre la app
    )

# Variable rápida para acceder a los textos
t = TEXTS[lang_choice]

with col_title:
    st.title(t["title"])
    st.markdown(t["subtitle"])

# Interfaz de entrada mejorada
col_up1, col_up2 = st.columns(2)

with col_up1:
    st.subheader(t["opt_a"])
    uploaded_file = st.file_uploader(t["opt_a_desc"], type=['csv', 'las', 'txt'], key="file_upload_widget")

with col_up2:
    st.subheader(t["opt_b"])
    # ESCANEAMOS LA CARPETA DATA/ AUTOMÁTICAMENTE
    archivos_disponibles = [] 
    if os.path.exists("data"):
        archivos_disponibles = [f for f in os.listdir("data") if f.endswith(('.csv', '.las', '.txt'))]
    
    # Agregamos "index=None" para que use el placeholder y detaching de las traducciones
    archivo_seleccionado = st.selectbox(
        t["opt_b_desc"], 
        options=archivos_disponibles, 
        index=None, 
        placeholder=t["none"],
        key="dataset_select_widget"
    )

# --- 3. ENRUTADOR DE DATOS Y MANEJO DE ESTADO ---
df_raw = None
origen_datos = None 
modo_prueba_activo = False

# Jerarquía: El archivo subido tiene prioridad. Si no hay, verificamos el dropdown.
if uploaded_file is not None:
    df_raw, error_lectura = load_raw_data(uploaded_file, uploaded_file.name)
    if error_lectura:
        st.error(error_lectura)
    else:
        origen_datos = f"{uploaded_file.name}_{uploaded_file.size}"

elif archivo_seleccionado is not None:
    ruta_prueba = os.path.join("data", archivo_seleccionado)
    if os.path.exists(ruta_prueba):
        archivo_simulado = MockFile(ruta_prueba)
        df_raw, error_lectura = load_raw_data(archivo_simulado, archivo_simulado.name)
        
        if error_lectura:
            st.error(error_lectura)
        else:
            origen_datos = f"prueba_{archivo_seleccionado}"
            modo_prueba_activo = True
    else:
        st.error("File not found.")

# --- 4. INICIO DEL MOTOR DE LA APLICACIÓN ---
if df_raw is not None:
    if st.session_state.get('last_file_id') != origen_datos:
        st.session_state['calculo_listo'] = False
        st.session_state['last_file_id'] = origen_datos
        
    # Mejor UX: Usamos un expander para esconder la tabla gigante por defecto
    with st.expander(t["preview_expander"]):
        st.dataframe(df_raw.head(100), use_container_width=True)
        if modo_prueba_activo:
            csv_crudo = df_raw.to_csv(index=False).encode('utf-8')
            st.download_button(t["download_raw"], data=csv_crudo, file_name=f"crudo_{archivo_seleccionado}.csv", mime='text/csv')
        
    st.divider()
    
    st.subheader(t["mapping_title"])
    columnas_disponibles = df_raw.columns.tolist()
        
    def adivinar_columna(palabras_clave):
        for clave in palabras_clave:
            for i, col in enumerate(columnas_disponibles):
                if clave.upper() in col.upper():
                    return i
        return 0
            
    col1, col2, col3 = st.columns(3)
    md_sel = col1.selectbox("MD", columnas_disponibles, index=adivinar_columna(['MD', 'DEPT']), key="md_map")
    inc_sel = col2.selectbox("INC", columnas_disponibles, index=adivinar_columna(['INC']), key="inc_map")
    azi_sel = col3.selectbox("AZI", columnas_disponibles, index=adivinar_columna(['AZI', 'HAZ']), key="azi_map")

    opciones_optativas = [t["not_avail"]] + columnas_disponibles
    
    col4, col5, col6 = st.columns(3)
    tvd_sel = col4.selectbox("TVD", opciones_optativas, key="tvd_map")
    ns_sel = col5.selectbox("N/S", opciones_optativas, key="ns_map")
    ew_sel = col6.selectbox("E/W", opciones_optativas, key="ew_map")

    st.divider()

    # EL BOTÓN DE CONTROL
    if st.button(t["btn_run"], type="primary"):
        md_vals = df_raw[md_sel].values
        inc_vals = df_raw[inc_sel].values
        azi_vals = df_raw[azi_sel].values
        
        tvd_tie = df_raw[tvd_sel].iloc[0] if tvd_sel != t["not_avail"] else 0.0
        ns_tie = df_raw[ns_sel].iloc[0] if ns_sel != t["not_avail"] else 0.0
        ew_tie = df_raw[ew_sel].iloc[0] if ew_sel != t["not_avail"] else 0.0
        
        with st.spinner(t["processing"]):
            tvd_calc, ns_calc, ew_calc, dls_calc = calcular_curvatura_minima_vectorizado(
                md_vals, inc_vals, azi_vals, tvd_tie, ns_tie, ew_tie
            )
        
        # GUARDAMOS EN ESTADO
        st.session_state['calculo_listo'] = True
        st.session_state['md'] = md_vals
        st.session_state['inc_rad'] = np.radians(inc_vals)
        st.session_state['azi_rad'] = np.radians(azi_vals)
        st.session_state['tvd'] = tvd_calc
        st.session_state['ns'] = ns_calc
        st.session_state['ew'] = ew_calc
        st.session_state['dls'] = dls_calc

    # --- 5. RENDERIZADO REACTIVO ---
    if st.session_state.get('calculo_listo', False):
        st.success(t["success"])
        
        md = st.session_state['md']
        inc_rad = st.session_state['inc_rad']
        azi_rad = st.session_state['azi_rad']
        tvd_calc = st.session_state['tvd']
        ns_calc = st.session_state['ns']
        ew_calc = st.session_state['ew']
        dls_calc = st.session_state['dls']
        
        tiene_originales = tvd_sel != t["not_avail"] and ns_sel != t["not_avail"] and ew_sel != t["not_avail"]
        
        col_izq, col_der = st.columns(2)
        
        with col_der if tiene_originales else st.container():
            st.subheader(t["plot_calc"])
            fig_user = go.Figure(data=[go.Scatter3d(x=ew_calc, y=ns_calc, z=tvd_calc * -1, mode='lines', line=dict(color=tvd_calc, colorscale='Inferno', width=4))])
            fig_user.update_layout(scene=dict(aspectratio=dict(x=1, y=1, z=2)), margin=dict(l=0, r=0, b=0, t=0), height=500)
            st.plotly_chart(fig_user, use_container_width=True)

        if tiene_originales:
            with col_izq:
                st.subheader(t["plot_orig"])
                fig_orig = go.Figure(data=[go.Scatter3d(x=df_raw[ew_sel], y=df_raw[ns_sel], z=df_raw[tvd_sel] * -1, mode='lines', line=dict(color=df_raw[tvd_sel], colorscale='Inferno', width=4))])
                fig_orig.update_layout(scene=dict(aspectratio=dict(x=1, y=1, z=2)), margin=dict(l=0, r=0, b=0, t=0), height=500)
                st.plotly_chart(fig_orig, use_container_width=True)
            
            error_euclidiano = np.sqrt((df_raw[ew_sel].values - ew_calc)**2 + (df_raw[ns_sel].values - ns_calc)**2 + (df_raw[tvd_sel].values - tvd_calc)**2)
            st.subheader(t["err_title"])
            st.markdown(f"**{t['err_max']}** {error_euclidiano.max():.5f} m")
            fig_error = go.Figure(data=[go.Scatter(x=md, y=error_euclidiano, mode='lines', line=dict(color='darkred', width=2))])
            fig_error.update_layout(xaxis_title="MD [m]", yaxis_title="Error [m]", margin=dict(l=0, r=0, b=0, t=0), height=300)
            st.plotly_chart(fig_error, use_container_width=True)
            
            st.subheader(t["dls_title"])
            st.markdown(f"**{t['dls_max']}** {dls_calc.max():.2f}° / 30m")
            
            fig_dls = go.Figure(data=[go.Scatter(
                x=md, y=dls_calc, mode='lines', fill='tozeroy', 
                line=dict(color='darkorange', width=2)
            )])
            
            fig_dls.add_hline(y=4.0, line_dash="dot", line_color="red", annotation_text=t["dls_limit"])
            
            fig_dls.update_layout(
                xaxis_title="MD [m]", 
                yaxis_title="DLS [° / 30m]", 
                margin=dict(l=0, r=0, b=0, t=0), height=300
            )
            st.plotly_chart(fig_dls, use_container_width=True)

        st.divider()
        st.subheader(t["interp_title"])

        min_md, max_md = float(md.min()), float(md.max())
        md_step = float(np.diff(md).min()) if len(md) > 1 else 1.0
        md_target = st.number_input(
            t["depth_target"],
            min_value=min_md,
            max_value=max_md,
            value=min_md + ((max_md - min_md) / 2),
            step=md_step
        )

        if md_target is not None:
            idx_lower = np.searchsorted(md, md_target, side='right') - 1
            idx_lower = max(0, min(idx_lower, len(md) - 2))
            idx_upper = min(idx_lower + 1, len(md) - 1)

            if md_target == md[idx_lower]:
                inc_tgt, azi_tgt = np.degrees(inc_rad[idx_lower]), np.degrees(azi_rad[idx_lower])
                tvd_tgt, ns_tgt, ew_tgt = tvd_calc[idx_lower], ns_calc[idx_lower], ew_calc[idx_lower]
            else:
                md1, inc1, azi1 = md[idx_lower], inc_rad[idx_lower], azi_rad[idx_lower]
                md2, inc2, azi2 = md[idx_upper], inc_rad[idx_upper], azi_rad[idx_upper]

                ratio = (md_target - md1) / (md2 - md1)
                inc_tgt_rad = inc1 + ratio * (inc2 - inc1)

                diff_azi = azi2 - azi1
                if diff_azi > np.pi: diff_azi -= 2 * np.pi
                elif diff_azi < -np.pi: diff_azi += 2 * np.pi
                
                azi_tgt_rad = (azi1 + ratio * diff_azi) % (2 * np.pi)

                d_md_tgt = md_target - md1
                cos_a = np.sin(inc1) * np.sin(inc_tgt_rad) * np.cos(azi_tgt_rad - azi1) + np.cos(inc1) * np.cos(inc_tgt_rad)
                cos_a = np.clip(cos_a, -1.0, 1.0)
                a = np.arccos(cos_a)
                
                rf_tgt = 1.0 if a < 1e-9 else (2.0 / a) * np.tan(a / 2.0)

                tvd_tgt = tvd_calc[idx_lower] + (d_md_tgt / 2.0) * (np.cos(inc1) + np.cos(inc_tgt_rad)) * rf_tgt
                ns_tgt  = ns_calc[idx_lower] + (d_md_tgt / 2.0) * (np.sin(inc1) * np.cos(azi1) + np.sin(inc_tgt_rad) * np.cos(azi_tgt_rad)) * rf_tgt
                ew_tgt  = ew_calc[idx_lower] + (d_md_tgt / 2.0) * (np.sin(inc1) * np.sin(azi1) + np.sin(inc_tgt_rad) * np.sin(azi_tgt_rad)) * rf_tgt
                
                inc_tgt, azi_tgt = np.degrees(inc_tgt_rad), np.degrees(azi_tgt_rad)

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("INC", f"{inc_tgt:.2f}°")
            m2.metric("AZI", f"{azi_tgt:.2f}°")
            m3.metric("TVD", f"{tvd_tgt:.2f} m")
            m4.metric("N/S (Local)", f"{ns_tgt - ns_calc[0]:.2f} m")
            m5.metric("E/W (Local)", f"{ew_tgt - ew_calc[0]:.2f} m")

        st.divider()
        st.subheader(t["export_title"])
        
        df_export = df_raw.copy()
        df_export['TVD_Calc'] = tvd_calc
        df_export['NS_Offset_Local_Calc'] = ns_calc - ns_calc[0]
        df_export['EW_Offset_Local_Calc'] = ew_calc - ew_calc[0]
        df_export['DLS_Calc_Deg_30m'] = dls_calc
        if tiene_originales:
            df_export['Error_Euclidiano'] = error_euclidiano
                    
        def convert_df(df):
            return df.to_csv(index=False, sep=';').encode('utf-8')

        csv_export = convert_df(df_export)
        st.download_button(t["download_val"], data=csv_export, file_name='trayectoria_validada.csv', mime='text/csv', type="primary")

else:
    st.info(t["waiting"])