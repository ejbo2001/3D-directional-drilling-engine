# Copyright (C) 2026  Emilio Barrera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Unit system definitions and conversions for drilling calculations."""

from enum import Enum


class UnitSystem(Enum):
    """Supported unit systems for drilling calculations."""

    METRIC = "metric"
    IMPERIAL = "imperial"


# Industry convention: DLS reported per 30 metres in metric wells.
DLS_NORMALIZATION_METRIC: float = 30.0

# Industry convention: DLS reported per 100 feet in imperial wells.
DLS_NORMALIZATION_IMPERIAL: float = 100.0


def dls_normalization_length(unit_system: UnitSystem) -> float:
    """Return the DLS normalisation length for the given unit system.

    Parameters
    ----------
    unit_system : UnitSystem
        The unit system in use.

    Returns
    -------
    float
        30.0 for METRIC (metres), 100.0 for IMPERIAL (feet).

    Raises
    ------
    ValueError
        If an unrecognised ``UnitSystem`` member is passed.
    """
    if unit_system is UnitSystem.METRIC:
        return DLS_NORMALIZATION_METRIC
    if unit_system is UnitSystem.IMPERIAL:
        return DLS_NORMALIZATION_IMPERIAL
    raise ValueError(
        f"Unknown unit system {unit_system!r}. "
        f"Expected one of {list(UnitSystem)}."
    )
