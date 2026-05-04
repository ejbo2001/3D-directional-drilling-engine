# Deferred improvements (noted during refactor, to address later)

## Input validation
- `Survey.azi_deg` currently allows `[0°, 360°]`. Industry convention is
  half-open `[0°, 360°)` because 360° aliases to 0°. Tighten after Week 1.

## Numerical
- MC formula uses `rf = 1.0` when `alpha < 1e-9`. For small but non-zero
  alpha, switch to a Taylor-series expansion to avoid precision loss.
  Scheduled for before Week 2 validation.

## Unit handling
- DLS hardcoded to 30 m in `minimum_curvature_vectorized`. Should use
  `dls_normalization_length(unit_system)` once imperial support lands.
