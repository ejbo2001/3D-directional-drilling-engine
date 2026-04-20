# Copyright (C) 2026  Emilio Barrera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Survey input data structures with validation."""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from .units import UnitSystem


@dataclass(frozen=True)
class Survey:
    """Validated wellbore survey input.

    Holds the raw measurement arrays (MD, inclination, azimuth) together
    with tie-in coordinates and the unit system. Validation is performed at
    construction time via ``__post_init__``; a ``ValueError`` is raised for
    any inconsistency in the inputs.

    Note: ``frozen=True`` disables mutation but does *not* make instances
    hashable because NumPy arrays have no ``__hash__``. Do not use ``Survey``
    objects as dict keys or set members.

    Parameters
    ----------
    md : NDArray[np.float64]
        Measured depth along the wellbore. Must be a 1-D array with at least
        two stations, strictly monotonically increasing, in the units implied
        by ``unit_system`` (metres for METRIC, feet for IMPERIAL).
    inc_deg : NDArray[np.float64]
        Inclination at each station in degrees from vertical
        (0° = vertical, 90° = horizontal). Must be in [0°, 180°].
    azi_deg : NDArray[np.float64]
        Azimuth at each station in degrees, clockwise from true north.
        Must be in [0°, 360°].
    unit_system : UnitSystem
        Unit system that applies to the numerical values in this survey.
    tvd_tie : float
        Tie-in true vertical depth in the local coordinate frame. Default 0.0.
    ns_tie : float
        Tie-in northing offset in the local coordinate frame. Default 0.0.
    ew_tie : float
        Tie-in easting offset in the local coordinate frame. Default 0.0.
    """

    md: NDArray[np.float64]
    inc_deg: NDArray[np.float64]
    azi_deg: NDArray[np.float64]
    unit_system: UnitSystem
    tvd_tie: float = 0.0
    ns_tie: float = 0.0
    ew_tie: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.unit_system, UnitSystem):
            raise ValueError(
                f"unit_system must be a UnitSystem instance, got {type(self.unit_system)!r}."
            )

        for name, arr in (("md", self.md), ("inc_deg", self.inc_deg), ("azi_deg", self.azi_deg)):
            if not isinstance(arr, np.ndarray) or arr.ndim != 1:
                raise ValueError(
                    f"'{name}' must be a 1-D NumPy array, got {type(arr).__name__} "
                    f"with ndim={getattr(arr, 'ndim', 'N/A')}."
                )

        if not (len(self.md) == len(self.inc_deg) == len(self.azi_deg)):
            raise ValueError(
                f"md, inc_deg, and azi_deg must all have the same length; "
                f"got {len(self.md)}, {len(self.inc_deg)}, {len(self.azi_deg)}."
            )

        if len(self.md) < 2:
            raise ValueError(
                f"Survey must contain at least 2 stations; got {len(self.md)}."
            )

        if not np.all(np.diff(self.md) > 0):
            raise ValueError(
                "md must be strictly monotonically increasing."
            )

        for name, arr in (("md", self.md), ("inc_deg", self.inc_deg), ("azi_deg", self.azi_deg)):
            if not np.all(np.isfinite(arr)):
                raise ValueError(
                    f"'{name}' contains NaN or infinite values."
                )

        if np.any(self.inc_deg < 0.0) or np.any(self.inc_deg > 180.0):
            raise ValueError(
                "inc_deg values must be in [0°, 180°]."
            )

        if np.any(self.azi_deg < 0.0) or np.any(self.azi_deg > 360.0):
            raise ValueError(
                "azi_deg values must be in [0°, 360°]."
            )
