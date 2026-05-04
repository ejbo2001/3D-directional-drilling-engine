# Copyright (C) 2026  Emilio Barrera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Heuristic column mapping for survey input files.

The ``MD_CANDIDATES``, ``INC_CANDIDATES``, and ``AZI_CANDIDATES`` lists
encode the canonical LAS/CSV mnemonic conventions used in directional
surveys (e.g. ``DEPT``/``DEPTH`` for measured depth in LAS, ``HAZI`` for
horizontal azimuth, ``DEVI`` for deviation/inclination).
"""


def guess_column(
    available_columns: list[str],
    candidates: list[str],
) -> str | None:
    """Find the first available column whose name contains any candidate keyword (case-insensitive).

    Parameters
    ----------
    available_columns : list[str]
        The column names present in the parsed file.
    candidates : list[str]
        Candidate keywords to look for, in priority order.

    Returns
    -------
    str | None
        The matching column name from available_columns, or None if no match.
    """
    for cand in candidates:
        cand_upper = cand.upper()
        for col in available_columns:
            if cand_upper in col.upper():
                return col
    return None


MD_CANDIDATES: list[str] = ["MD", "DEPT", "DEPTH"]
INC_CANDIDATES: list[str] = ["INC", "INCL", "DEVI"]
AZI_CANDIDATES: list[str] = ["AZI", "HAZI", "AZIM"]
