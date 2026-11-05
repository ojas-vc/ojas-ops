# Panchang Ephemeris Director: Ephemeris Calculations

## Objective

Compute the five classical pillars of Panchang (Tithi, Vara, Nakshatra, Yoga, Karana) along with local sunrise, solar noon, and sunset for the target coordinates.

## Invariant Rules

- Coordinates must be specified (default: Mumbai 19.0760° N, 72.8777° E or Hyderabad 17.3850° N, 78.4867° E).
- Calculate solar diurnal duration $\Delta T = Sunset - Sunrise$ divided into 8 equal daytime intervals.

## Output Artifact

`planetary_ephemeris_data`: Detailed astronomical table across the evaluation dates.
