# 02 Survey Design Notes

## 1. Purpose
Survey is a validated container for wellbore survey input data. Once constructed, it guarantees that any Survey object represents physically-plausible wellbore measurements with sorted measured depths, values within valid ranges, no missing data, and a known unit system. By acting as a strict gatekeeper, it ensures that downstream code can completely trust the inputs without ever needing to re-validate them. This drastically simplifies the mathematical engine that consumes these surveys.

## 2. The seven validation checks
- **Unit System Instance Check:** Prevents users from passing arbitrary strings (like "metric") instead of the required UnitSystem enum member. Downstream symptom: the engine's identity check (survey.unit_system is UnitSystem.METRIC) fails for any non-enum value, so the engine misleadingly raises NotImplementedError claiming Imperial isn't supported even when the user intended metric.

- **1-D NumPy Array Check:** Prevents passing lists or 2D matrices (e.g., shape (N, 1)). Downstream symptom: Silent, unintended array broadcasting or dimension expansion during vector operations, yielding matrices instead of vectors.

- **Equal Length Check:** Prevents mismatched station data (e.g., truncated columns from bad CSV parsing). Downstream symptom: IndexError during minimum curvature iteration or silent misalignment of depths to angles.

- **Minimum Stations Check (≥ 2):** Ensures there is at least one interval to calculate. Downstream symptom: IndexError when trying to access index [1] to calculate the first trajectory interval.

- **Strict Monotonicity Check:** Ensures Measured Depth strictly increases. Downstream symptom: Division by zero in Dogleg Severity (DLS) or Minimum Curvature calculations where Δ_MD is used in the denominator.

- **Finite Values Check:** Prevents missing data points (NaN) or infinities from creeping into the arrays. Downstream symptom: A single NaN poisons all subsequent array math, silently yielding final trajectory arrays full of NaNs.

- **Angle Bounds Check:** Prevents physically impossible inputs, like an inclination of 190° or an azimuth of 400°. Downstream symptom: Trigonometric functions silently wrapping around, masking data-entry errors and producing valid-looking but entirely incorrect spatial coordinates.

## 3. The "parse, don't validate" pattern
The Survey class follows a pattern known in software engineering as "parse, don't validate," a concept popularized by a well-known essay by Alexis King. In a defensive "validating-everywhere" approach, every function that calculates Dogleg Severity or Minimum Curvature would need its own assertions to ensure arrays are the same length, depths are sorted, and no NaNs exist. This scatters validation logic across the entire codebase, making it hard to read and easy to forget a check.

Instead, Survey acts as a parser: it takes raw, untrusted data and transforms it into a strictly trusted type. All the checks happen exactly once, at the boundary of the system during object construction (__post_init__). Once the data successfully passes through this constructor, it is no longer "raw data"—it is a Survey. Downstream functions can then blindly accept a Survey object, completely confident that the data is pristine, which strips away layers of redundant defensive boilerplate.

## 4. Why `frozen=True` matters
A validated object without frozen=True provides only a moment-in-time guarantee. It means the data was valid at the exact millisecond the object was created. However, without immutability, a user or a stray script could later do something like s.md = np.array([100, 50, 200]). This mutation would instantly invalidate the data (breaking monotonicity and array lengths) without triggering the __post_init__ checks again, reintroducing the exact bugs the constructor was built to prevent.

By using @dataclass(frozen=True), we upgrade Survey to provide a lifetime guarantee. Once a Survey is constructed and validated, it is valid forever. If any code attempts to overwrite a field, Python will immediately raise a FrozenInstanceError. This strict immutability ensures that downstream code can trust the Survey unconditionally, knowing the rug cannot be pulled out from under it.

## 5. Why `Survey` is unhashable
To use an object as a dictionary key or store it in a set, Python needs it to be "hashable". You can think of a hash as a permanent "serial number" assigned based on the object's contents. If the contents were to change, the serial number would change, which breaks the dictionary's internal mapping. Usually, making a dataclass frozen=True tells Python "this object will never change, so it's safe to calculate a permanent serial number for it."

However, Survey contains NumPy arrays, and NumPy arrays are inherently unhashable (Python refuses to hash them because arrays themselves are mutable, even if their parent object is frozen). Because Python cannot compute a serial number for the underlying arrays, it refuses to compute one for the Survey. If a user tries to use it as a key (e.g., cache[my_survey] = results), they will see TypeError: unhashable type: 'Survey'. The standard workaround is to avoid hashing the object directly, and instead hash a derived key—such as a tuple of the unit_system and the hashed bytes of the md array.

## 6. Why strict monotonicity (not just non-decreasing)
The requirement that np.diff(md) > 0 enforces strict monotonicity, meaning duplicate Measured Depth (MD) values are instantly rejected. We enforce this for two main reasons. First, duplicate MDs are a physical impossibility: because pipe length doesn't time-travel, each MD corresponds to a unique, singular moment of measurement in the wellbore. Second, it guarantees mathematical safety. If two consecutive stations had the same MD, the difference (Δ_MD) would be zero, which would cause an immediate division-by-zero error in Dogleg Severity formulas and when calculating the radius of curvature ($R = \Delta MD / \alpha$).

A strong steelman counterargument is that duplicate MDs can naturally appear due to tool precision limitations, or when multiple readings are taken at the same depth while the drillstring is stationary. While it might seem friendlier to tolerate these duplicates by silently merging them or averaging the angles, we chose strict rejection. Silent merging introduces a different class of hidden bugs—how do you handle it when two stationary readings genuinely differ? The strictness catches a class of file-corruption bugs that would otherwise silently produce subtly wrong trajectories. We decided it is safer to reject ambiguous inputs and force the user to clean their data explicitly.

## 7. Open issues / future improvements
- **Tighten azimuth validation:** Update the bounds check to a half-open interval [0°, 360°), as 360° is mathematically identical to 0° and generally avoided in normalized data.

- **Unit-aware DLS computations:** Connect unit_system to the actual Dogleg Severity computation (currently, the Survey knows the unit, but the computation engine does not yet dynamically use it).

- **Custom Exceptions:** Consider replacing generic ValueError exceptions with specific, custom exception classes (e.g., MonotonicityError, InvalidAngleError) so calling code can programmatically catch and handle specific data failures.

