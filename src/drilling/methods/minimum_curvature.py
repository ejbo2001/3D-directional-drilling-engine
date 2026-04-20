# Copyright (C) 2026  Emilio Barrera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Minimum Curvature trajectory calculation."""

import numpy as np
from numpy.typing import NDArray


def minimum_curvature_vectorized(
    md: NDArray[np.float64],
    inc_deg: NDArray[np.float64],
    azi_deg: NDArray[np.float64],
    tvd_tie: float = 0.0,
    ns_tie: float = 0.0,
    ew_tie: float = 0.0,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Compute wellbore position using the Minimum Curvature Method.

    Calculates true vertical depth, northing, easting, and dogleg severity
    for every survey station along a wellbore. The computation is fully
    vectorized over all survey intervals in a single NumPy pass.

    Parameters
    ----------
    md : NDArray[np.float64]
        Measured depth along the wellbore in metres. Must be monotonically
        increasing.
    inc_deg : NDArray[np.float64]
        Inclination at each survey station in degrees from vertical
        (0° = vertical, 90° = horizontal).
    azi_deg : NDArray[np.float64]
        Azimuth at each survey station in degrees, clockwise from true north,
        in the range [0°, 360°).
    tvd_tie : float, optional
        Tie-in true vertical depth in metres in the local North/East/TVD
        frame. Default is 0.0.
    ns_tie : float, optional
        Tie-in northing offset in metres in the local North/East/TVD frame.
        Default is 0.0.
    ew_tie : float, optional
        Tie-in easting offset in metres in the local North/East/TVD frame.
        Default is 0.0.

    Returns
    -------
    tvd : NDArray[np.float64]
        True vertical depth at each survey station in metres. 1-D array of
        the same length as ``md``.
    ns : NDArray[np.float64]
        Northing offset at each survey station in metres. 1-D array of the
        same length as ``md``.
    ew : NDArray[np.float64]
        Easting offset at each survey station in metres. 1-D array of the
        same length as ``md``.
    dls : NDArray[np.float64]
        Dogleg severity at each survey station in degrees per 30 m. 1-D array
        of the same length as ``md``. The first station is always 0.0.

    Notes
    -----
    Minimum Curvature with ratio factor RF = 2/α · tan(α/2), where α is the
    dog-leg angle between consecutive survey stations.

    The DLS normalisation constant is hardcoded to 30 m, so ``md`` must be in
    metres for the DLS units (°/30 m) to be correct.

    References
    ----------
    Sawaryn, S.J. and Thorogood, J.L. (2005), "A Compendium of Directional
    Calculations Based on the Minimum Curvature Method", SPE Drilling &
    Completion, Volume 20, Issue 1, pages 24–36, SPE-84246-PA.
    """
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
