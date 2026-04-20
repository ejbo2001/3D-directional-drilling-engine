# Copyright (C) 2026  Emilio Barrera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Trajectory computation result containers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    import pandas as pd
    from drilling.survey import Survey


@dataclass(frozen=True)
class Trajectory:
    """Result of a wellbore trajectory computation.

    All arrays are 1-D and share the same length as the source ``md`` array.
    Units follow the ``unit_system`` of the originating ``Survey``: depths and
    offsets are in metres (METRIC) or feet (IMPERIAL); DLS is in degrees per
    30 m (METRIC) or degrees per 100 ft (IMPERIAL).

    Parameters
    ----------
    md : NDArray[np.float64]
        Measured depth at each survey station.
    tvd : NDArray[np.float64]
        True vertical depth at each survey station.
    ns : NDArray[np.float64]
        Northing offset at each survey station.
    ew : NDArray[np.float64]
        Easting offset at each survey station.
    dls : NDArray[np.float64]
        Dogleg severity at each survey station (first station is always 0.0).
    source_survey : Survey
        The ``Survey`` object from which this trajectory was computed.
    """

    md: NDArray[np.float64]
    tvd: NDArray[np.float64]
    ns: NDArray[np.float64]
    ew: NDArray[np.float64]
    dls: NDArray[np.float64]
    source_survey: Survey

    @property
    def max_dls(self) -> float:
        """Maximum dogleg severity across all survey stations."""
        return float(np.max(self.dls))

    @property
    def total_md(self) -> float:
        """Total measured depth span from first to last station."""
        return float(self.md[-1] - self.md[0])

    def to_dataframe(self) -> pd.DataFrame:
        """Return trajectory arrays as a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            Columns: MD, TVD, NS, EW, DLS.
        """
        import pandas as pd

        return pd.DataFrame({
            "MD": self.md,
            "TVD": self.tvd,
            "NS": self.ns,
            "EW": self.ew,
            "DLS": self.dls,
        })
