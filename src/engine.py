# Copyright (C) 2026  Emilio Barrera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Deprecated legacy module.

Prefer :mod:`drilling.methods.minimum_curvature` for new code.
"""
from drilling.methods.minimum_curvature import (
    minimum_curvature_vectorized as _impl,
)


def calcular_curvatura_minima_vectorizado(
    md, inc_deg, azi_deg, tvd_tie=0.0, ns_tie=0.0, ew_tie=0.0
):
    """Spanish-named alias kept for backward compatibility.

    Deprecated: use
    ``drilling.methods.minimum_curvature.minimum_curvature_vectorized``.
    """
    return _impl(md, inc_deg, azi_deg, tvd_tie, ns_tie, ew_tie)
