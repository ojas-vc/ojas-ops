# Shift Demand Director: Ratio Sizing & Staffing Demand

## Objective

Convert patient acuity levels into required nursing hours per shift (Day: 07:00-19:00, Night: 19:00-07:00).

## Invariant Rules

- Enforce statutory California Title 22 staffing ratios:
  - ICU: max 2 patients per RN.
  - Step-Down: max 3 patients per RN.
  - Med-Surg: max 4 patients per RN.
- Dedicated Charge Nurse must be budgeted in addition to bedside nurses.

## Output Artifact

`nurse_demand_matrix`: Hourly required Registered Nurse (RN) headcount per unit.
