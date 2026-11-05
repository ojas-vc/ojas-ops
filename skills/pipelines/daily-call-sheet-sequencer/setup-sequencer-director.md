# Setup Sequencer Director: Camera Rotation & Setup Minimization

## Objective
Cluster intra-day camera setups to minimize camera axis turnarounds ($\Delta \theta \le 45^\circ$) and sound/lighting rig relocations.

## Invariant Rules
- Consecutive camera setups pointing in identical directions must be shot together to eliminate lighting turnaround times.
- Cast arrival and hair/makeup call times must stagger to minimize trailer idle times.

## Output Artifact
`intra_day_shot_sequence`: Ordered list of setups with camera angles, cast requirements, and estimated completion times.
