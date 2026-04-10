import streamlit as st
import pandas as pd
import numpy as np  
import plotly.graph_objects as go
import lasio
import io
from engine import calcular_curvatura_minima_vectorizado
# ESTO DEBE IR AQUÍ ARRIBA, ANTES DE CUALQUIER OTRA COSA DE UI
st.set_page_config(page_title="Validación Direccional Pro", layout="wide")


# --- 2. GESTIÓN DE DATOS ---
@st.cache_data
def load_raw_data(file, file_name):
    try:
        if file_name.lower().endswith('.las'):
            # Ignora al linter. LAS es Log ASCII Standard, es 100% texto.
            # Decodificamos los bytes a texto y se lo pasamos directo a lasio
            string_data = file.getvalue().decode("utf-8", errors="replace")
            las = lasio.read(string_data)
            df = las.df().reset_index()
            
        elif file_name.lower().endswith('.txt'):
            content = file.getvalue().decode("utf-8", errors="replace").splitlines()
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
            df = pd.read_csv(file, sep=None, engine='python')
        else:
            df = pd.read_excel(file)
            
        return df, None
    except Exception as e:
        return None, f"Error en la lectura del archivo: {str(e)}"

# --- 3. INTERFAZ Y CONTROL DE ESTADO ---
st.title("Ingeniería de Perforación: Validación de Curvatura Mínima")
st.markdown("Soporte multi-formato con mapeo inteligente de curvas.")

uploaded_file = st.file_uploader("Sube tu archivo (.csv, .xlsx, .las, .txt)", type=["csv", "xlsx", "las", "txt"])

# --- EL PARCHE ANTI-ZOMBIES ---
if uploaded_file:
    # Creamos una huella única del archivo (nombre + peso en bytes)
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # Si detectamos que el archivo subido es diferente al anterior, VACIAMOS LA MEMORIA
    if st.session_state.get('last_file_id') != file_id:
        st.session_state['calculo_listo'] = False
        st.session_state['last_file_id'] = file_id
        
    df_raw, error_lectura = load_raw_data(uploaded_file, uploaded_file.name)
    
    if error_lectura:
        st.error(f"Error al leer el archivo: {error_lectura}")
    else:
        st.subheader("1. Mapeo de Curvas (Mnemonics)")
        columnas_disponibles = df_raw.columns.tolist()
        
        def adivinar_columna(palabras_clave):
            for clave in palabras_clave:
                for i, col in enumerate(columnas_disponibles):
                    if clave.upper() in col.upper():
                        return i
            return 0
            
        col1, col2, col3 = st.columns(3)
        md_sel = col1.selectbox("MD", columnas_disponibles, index=adivinar_columna(['MD', 'DEPT']))
        inc_sel = col2.selectbox("INC", columnas_disponibles, index=adivinar_columna(['INC']))
        azi_sel = col3.selectbox("AZI", columnas_disponibles, index=adivinar_columna(['AZI', 'HAZ']))

        opciones_optativas = ["No disponible"] + columnas_disponibles
        
        col4, col5, col6 = st.columns(3)
        tvd_sel = col4.selectbox("TVD Original", opciones_optativas)
        ns_sel = col5.selectbox("N/S Original", opciones_optativas)
        ew_sel = col6.selectbox("E/W Original", opciones_optativas)

        st.divider()

        # EL BOTÓN DE CONTROL
        if st.button("Ejecutar Motor de Curvatura Mínima", type="primary"):
            md_vals = df_raw[md_sel].values
            inc_vals = df_raw[inc_sel].values
            azi_vals = df_raw[azi_sel].values
            
            tvd_tie = df_raw[tvd_sel].iloc[0] if tvd_sel != "No disponible" else 0.0
            ns_tie = df_raw[ns_sel].iloc[0] if ns_sel != "No disponible" else 0.0
            ew_tie = df_raw[ew_sel].iloc[0] if ew_sel != "No disponible" else 0.0
            
            with st.spinner("Procesando matriz direccional..."):
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

        # --- 4. RENDERIZADO REACTIVO (Todo esto debe estar indentado aquí) ---
        if st.session_state.get('calculo_listo', False):
            st.success("¡Cálculo vectorizado exitoso!")
            
            md = st.session_state['md']
            inc_rad = st.session_state['inc_rad']
            azi_rad = st.session_state['azi_rad']
            tvd_calc = st.session_state['tvd']
            ns_calc = st.session_state['ns']
            ew_calc = st.session_state['ew']
            dls_calc = st.session_state['dls']
            
            tiene_originales = tvd_sel != "No disponible" and ns_sel != "No disponible" and ew_sel != "No disponible"
            
            col_izq, col_der = st.columns(2)
            
            with col_der if tiene_originales else st.container():
                st.subheader("Cálculo Propio (Curvatura Mínima)")
                fig_user = go.Figure(data=[go.Scatter3d(x=ew_calc, y=ns_calc, z=tvd_calc * -1, mode='lines', line=dict(color=tvd_calc, colorscale='Inferno', width=4))])
                fig_user.update_layout(scene=dict(aspectratio=dict(x=1, y=1, z=2)), margin=dict(l=0, r=0, b=0, t=0), height=500)
                st.plotly_chart(fig_user, use_container_width=True)

            if tiene_originales:
                with col_izq:
                    st.subheader("Trayectoria Original")
                    fig_orig = go.Figure(data=[go.Scatter3d(x=df_raw[ew_sel], y=df_raw[ns_sel], z=df_raw[tvd_sel] * -1, mode='lines', line=dict(color=df_raw[tvd_sel], colorscale='Inferno', width=4))])
                    fig_orig.update_layout(scene=dict(aspectratio=dict(x=1, y=1, z=2)), margin=dict(l=0, r=0, b=0, t=0), height=500)
                    st.plotly_chart(fig_orig, use_container_width=True)
                
                error_euclidiano = np.sqrt((df_raw[ew_sel].values - ew_calc)**2 + (df_raw[ns_sel].values - ns_calc)**2 + (df_raw[tvd_sel].values - tvd_calc)**2)
                st.subheader("Análisis de Error Espacial")
                st.markdown(f"**Diferencia máxima detectada:** {error_euclidiano.max():.5f} metros")
                fig_error = go.Figure(data=[go.Scatter(x=md, y=error_euclidiano, mode='lines', line=dict(color='darkred', width=2))])
                fig_error.update_layout(xaxis_title="Profundidad Medida (MD) [m]", yaxis_title="Error Euclidiano [m]", margin=dict(l=0, r=0, b=0, t=0), height=300)
                st.plotly_chart(fig_error, use_container_width=True)
                # --- NUEVA GRÁFICA: PERFIL DE SEVERIDAD (DLS) ---
                st.subheader("Análisis de Severidad (DLS)")
                st.markdown(f"**DLS Máximo detectado:** {dls_calc.max():.2f}° / 30m")
                
                fig_dls = go.Figure(data=[go.Scatter(
                    x=md, y=dls_calc, mode='lines', fill='tozeroy', 
                    line=dict(color='darkorange', width=2)
                )])
                
                # Línea roja de peligro estándar de la industria (4°/30m)
                fig_dls.add_hline(y=4.0, line_dash="dot", line_color="red", 
                                  annotation_text="Límite de Fatiga (4°/30m)")
                
                fig_dls.update_layout(
                    xaxis_title="Profundidad Medida (MD) [m]", 
                    yaxis_title="DLS [° / 30m]", 
                    margin=dict(l=0, r=0, b=0, t=0), height=300
                )
                st.plotly_chart(fig_dls, use_container_width=True)

            # --- 5. Módulo de Interpolación Direccional ---
            st.divider()
            st.subheader("🎯 Módulo de Interpolación de Precisión")

            min_md, max_md = float(md.min()), float(md.max())
            md_step = float(np.diff(md).min()) if len(md) > 1 else 1.0
            md_target = st.number_input(
                "Profundidad Objetivo (MD)",
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
                m1.metric("Inclinación", f"{inc_tgt:.2f}°")
                m2.metric("Azimut", f"{azi_tgt:.2f}°")
                m3.metric("TVD", f"{tvd_tgt:.2f} m")
                m4.metric("N/S Offset Local", f"{ns_tgt - ns_calc[0]:.2f} m")
                m5.metric("E/W Offset Local", f"{ew_tgt - ew_calc[0]:.2f} m")

            # --- 6. Exportación de Resultados ---
            st.divider()
            st.subheader("📥 Exportar Datos")
            
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
            st.download_button("Descargar Trayectoria Validada (.csv)", data=csv_export, file_name='trayectoria_validada.csv', mime='text/csv', type="primary")
else:
    st.info("Esperando archivo para iniciar.")
