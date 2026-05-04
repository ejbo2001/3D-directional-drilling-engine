# Survey Design Notes

## Purpose

(One paragraph: what is `Survey` and why does it exist?)

## The seven validation checks

(For each of the seven `__post_init__` checks: what bug it catches, why it matters.)

## The "parse, don't validate" pattern

(Why we do all checks at construction and never re-check downstream.)

## Why `frozen=True` matters

(Lifetime guarantee vs moment-in-time guarantee. The bug it prevents.)

## Why `Survey` is unhashable

(NumPy arrays, recursive immutability, what error users see, the workaround.)

## Why strict monotonicity (not just non-decreasing)

(Physical impossibility argument plus math-safety argument.)

## Open issues / future improvements

(Tighten azimuth to half-open `[0°, 360°)`. Connect to `unit_system` for unit-aware DLS. Etc.)