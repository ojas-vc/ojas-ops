# Forecast Director: Multi-Echelon Lead Times & Demand Waves

## Objective
Model customer order demand waves and multi-tier supplier lead times to calculate safety stock thresholds and reorder points.

## Invariant Rules
- Maintain minimum safety stock days of supply (DOS) across all distribution centers.
- Factor maritime, rail, and trucking variability into replenishment lead times.

## Output Artifact
`demand_forecast_waves`: Projected demand time series by SKU and regional fulfillment hub.
