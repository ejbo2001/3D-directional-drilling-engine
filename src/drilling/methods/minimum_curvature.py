# Copyright (C) 2026  Emilio Barrera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Minimum Curvature trajectory calculation."""

import numpy as np
from numpy.typing import NDArray

from drilling.survey import Survey
from drilling.trajectory import Trajectory
from drilling.units import UnitSystem


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


def minimum_curvature(survey: Survey) -> Trajectory:
    """Compute a Trajectory from a Survey using the Minimum Curvature Method.

    High-level wrapper around :func:`minimum_curvature_vectorized` that
    accepts a :class:`Survey` and returns a :class:`Trajectory`. Preferred
    entry point for new code.

    Parameters
    ----------
    survey : Survey
        Validated survey input. The ``unit_system`` field determines the
        DLS normalisation convention that applies to the returned ``dls``
        array.

    Returns
    -------
    Trajectory
        Computed wellbore trajectory including TVD, northing, easting,
        and DLS, with a reference back to the source ``survey``.

    Notes
    -----
    In this stage only :attr:`UnitSystem.METRIC` is supported end-to-end
    because :func:`minimum_curvature_vectorized` currently assumes metres
    and DLS per 30 m. Passing a survey with ``unit_system`` set to
    ``IMPERIAL`` raises :class:`NotImplementedError`.
    """
    if survey.unit_system is not UnitSystem.METRIC:
        raise NotImplementedError(
            "Imperial unit system not yet supported; scheduled for a later refactor stage."
        )
    tvd, ns, ew, dls = minimum_curvature_vectorized(
        survey.md, survey.inc_deg, survey.azi_deg,
        survey.tvd_tie, survey.ns_tie, survey.ew_tie,
    )
    return Trajectory(md=survey.md, tvd=tvd, ns=ns, ew=ew, dls=dls, source_survey=survey)
