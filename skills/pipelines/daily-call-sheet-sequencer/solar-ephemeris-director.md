# Solar Ephemeris Director: Lighting Windows & Astronomical Azimuth

## Objective
Compute precise solar elevation, azimuth, golden hour intervals, and blue hour twilight for scheduled exterior production locations.

## Invariant Rules
- Golden hour shots must be bounded within 45 minutes prior to sunset / after sunrise.
- High-noon harsh shadow periods (11:30 - 13:30) must be prioritized for interior shooting or crew lunch breaks.

## Output Artifact
`sun_azimuth_windows`: Astronomical ephemeris schedule specifying optimal lighting windows per exterior scene.
