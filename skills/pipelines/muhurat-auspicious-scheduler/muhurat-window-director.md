# Muhurat Window Director: Shubh Muhurat Search & Gate

## Objective

Search the feasible intervals outside all inauspicious blackout windows to identify optimal Shubh Muhurat windows. Present candidates to the Astrological Consultant for human approval.

## Invariant Rules

- Hard Disjunction: $Window \cap Blackouts = \emptyset$.
- Prefer midday Abhijit Muhurat (centered on solar noon $\pm 24$ minutes).
- Score favorable Choghadiya intervals (Amrit > Shubh > Labh).
- Require human sign-off before docket certification.

## Output Artifact

`candidate_muhurat_windows`: Ranked list of auspicious intervals with astrological rationale.
