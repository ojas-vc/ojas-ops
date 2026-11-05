# Rahu Kalam Exclusion Director: Inauspicious Blackout Windows

## Objective

Compute exact inauspicious time segments across the target horizon:

- Rahu Kalam (1/8th interval governed by weekday)
- Yamagandam (1/8th interval governed by weekday)
- Gulika Kalam
- Durmuhurtam

## Invariant Rules

- Rahu Kalam by day (where each part = $\Delta T / 8$):
  - Monday: Part 2
  - Saturday: Part 3
  - Friday: Part 4
  - Wednesday: Part 5
  - Thursday: Part 6
  - Tuesday: Part 7
  - Sunday: Part 8
- Zero margin of error allowed on blackout start and end timestamps.

## Output Artifact

`inauspicious_blackout_windows`: Non-negotiable temporal exclusion intervals.
