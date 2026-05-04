# Copyright (C) 2026  Emilio Barrera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Whitespace-delimited TXT survey file parser."""

import io

import numpy as np
import pandas as pd

from drilling.io._column_mapping import (
    AZI_CANDIDATES,
    INC_CANDIDATES,
    MD_CANDIDATES,
    guess_column,
)
from drilling.io._unit_detection import detect_unit_system
from drilling.survey import Survey
from drilling.units import UnitSystem


def parse_txt(
    content: bytes,
    unit_system: UnitSystem | None = None,
) -> Survey:
    """Parse whitespace-delimited TXT survey content into a validated Survey object.

    Locates the header row by scanning for a line containing both ``MD`` and
    ``INC`` (case-insensitive substrings), then parses the remainder as a
    whitespace-delimited table. Non-numeric rows (e.g. unit annotation rows
    such as ``[m] [deg] [deg]``) are dropped via ``pd.to_numeric(..., errors='coerce')``.
    Auto-maps MD, INC, AZI columns using the mnemonic dictionaries from
    drilling.io._column_mapping.
    Auto-detects unit system from MD range if unit_system is None.
    Canonicalises azimuth to [0, 360) at parse time.
    Tie-in defaults to (0, 0, 0) — the first survey row is treated as the
    surface reference.

    Parameters
    ----------
    content : bytes
        Raw bytes of the TXT file. Decoded as UTF-8 with replacement.
    unit_system : UnitSystem | None
        If provided, overrides auto-detection. If None, detect_unit_system
        is called and may emit a UserWarning.

    Returns
    -------
    Survey
        Validated survey with unit_system either explicit or auto-detected.

    Raises
    ------
    ValueError
        If required columns (MD/INC/AZI) cannot be located, no header row
        is found, the file is empty, or unit detection is ambiguous.
    """
    text = content.decode("utf-8", errors="replace")
    lines = text.splitlines()

    start_idx = None
    for i, line in enumerate(lines):
        upper = line.upper()
        if "MD" in upper and "INC" in upper:
            start_idx = i
            break
    if start_idx is None:
        raise ValueError(
            "Could not locate a header row containing both 'MD' and 'INC'."
        )

    clean_text = "\n".join(lines[start_idx:])
    df = pd.read_csv(io.StringIO(clean_text), sep=r"\s+")

    # Drop rows that can't be parsed numerically (e.g. unit annotation rows).
    # Replaces the deprecated ``errors='ignore'`` pattern.
    df = df.apply(pd.to_numeric, errors="coerce").dropna(how="any")

    columns = df.columns.tolist()
    md_col = guess_column(columns, MD_CANDIDATES)
    if md_col is None:
        raise ValueError(
            f"Could not locate column for MD; expected one of {MD_CANDIDATES}"
        )
    inc_col = guess_column(columns, INC_CANDIDATES)
    if inc_col is None:
        raise ValueError(
            f"Could not locate column for INC; expected one of {INC_CANDIDATES}"
        )
    azi_col = guess_column(columns, AZI_CANDIDATES)
    if azi_col is None:
        raise ValueError(
            f"Could not locate column for AZI; expected one of {AZI_CANDIDATES}"
        )

    md = df[md_col].to_numpy(dtype=np.float64)
    inc = df[inc_col].to_numpy(dtype=np.float64)
    azi = df[azi_col].to_numpy(dtype=np.float64)

    # Maps both negative azimuths and values >= 360 into [0, 360).
    azi = np.mod(azi, 360.0)

    if unit_system is None:
        unit_system = detect_unit_system(md)

    return Survey(md=md, inc_deg=inc, azi_deg=azi, unit_system=unit_system)
