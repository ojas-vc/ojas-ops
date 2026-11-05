# Geo Cluster Director: Service Order Clustering & Territory Mapping

## Objective
Cluster pending maintenance work orders, customer appointments, and emergency dispatch tickets into compact geographical routing sectors.

## Invariant Rules
- Travel transit times between consecutive work orders within the same sector must not exceed 25 minutes.
- Match technician skill certifications (HVAC, Electrical, Fiber Optic) to job requirements.

## Output Artifact
`geographic_work_clusters`: Geocoded ticket clusters assigned to regional technician pools.
