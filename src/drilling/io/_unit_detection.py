# Copyright (C) 2026  Emilio Barrera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Heuristic unit-system detection from MD range."""

import warnings

import numpy as np
from numpy.typing import NDArray

from drilling.units import UnitSystem


def detect_unit_system(md: NDArray[np.float64]) -> UnitSystem:
    """Detect the unit system from the MD array's range.

    Heuristic:
      - max(md) < 15_000  -> METRIC (assumes metres)
      - max(md) > 50_000  -> IMPERIAL (assumes feet)
      - 15_000 <= max(md) <= 50_000 -> ambiguous, raises ValueError

    Always emits a UserWarning when detection succeeds, so the caller knows
    the unit system was guessed rather than declared.

    Parameters
    ----------
    md : NDArray[np.float64]
        Measured-depth array. Must be non-empty.

    Returns
    -------
    UnitSystem
        Detected unit system.

    Raises
    ------
    ValueError
        If the MD range is ambiguous between metric and imperial, with a
        message instructing the user to pass unit_system explicitly to the
        parser.
    """
    max_md = float(np.max(md))

    if max_md < 15_000:
        result = UnitSystem.METRIC
    elif max_md > 50_000:
        result = UnitSystem.IMPERIAL
    else:
        raise ValueError(
            "MD range is ambiguous between metric and imperial; "
            "pass unit_system=UnitSystem.METRIC or UnitSystem.IMPERIAL "
            "explicitly to the parser."
        )

    warnings.warn(
        f"Unit system was auto-detected as {result}. "
        f"Pass unit_system explicitly to the parser to suppress this warning.",
        UserWarning,
    )
    return result
