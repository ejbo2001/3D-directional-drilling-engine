import numpy as np

def calcular_curvatura_minima_vectorizado(md, inc_deg, azi_deg, tvd_tie=0.0, ns_tie=0.0, ew_tie=0.0):
    inc_rad = np.radians(inc_deg)
    azi_rad = np.radians(azi_deg)
    
    d_md = np.diff(md)
    inc_1, inc_2 = inc_rad[:-1], inc_rad[1:]
    azi_1, azi_2 = azi_rad[:-1], azi_rad[1:]
    
    cos_alpha = np.sin(inc_1) * np.sin(inc_2) * np.cos(azi_2 - azi_1) + np.cos(inc_1) * np.cos(inc_2)
    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
    alpha = np.arccos(cos_alpha)
    
    alpha_safe = np.where(alpha < 1e-9, 1e-9, alpha)
    rf = np.where(alpha < 1e-9, 1.0, (2.0 / alpha_safe) * np.tan(alpha_safe / 2.0))

    d_md_safe = np.where(d_md < 1e-9, 1e-9, d_md)
    dls_interval = np.degrees(alpha) * (30.0 / d_md_safe)
 

    
    delta_tvd = (d_md / 2.0) * (np.cos(inc_1) + np.cos(inc_2)) * rf
    delta_ns = (d_md / 2.0) * (np.sin(inc_1) * np.cos(azi_1) + np.sin(inc_2) * np.cos(azi_2)) * rf
    delta_ew = (d_md / 2.0) * (np.sin(inc_1) * np.sin(azi_1) + np.sin(inc_2) * np.sin(azi_2)) * rf
    
    tvd_calc = np.concatenate(([tvd_tie], tvd_tie + np.cumsum(delta_tvd)))
    ns_calc = np.concatenate(([ns_tie], ns_tie + np.cumsum(delta_ns)))
    ew_calc = np.concatenate(([ew_tie], ew_tie + np.cumsum(delta_ew)))
    dls_calc = np.concatenate(([0.0], dls_interval))

   
    
    return tvd_calc, ns_calc, ew_calc, dls_calc

