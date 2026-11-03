"""Class-Based ViewSet for Simulation and reactive rescheduling."""

from django_bolt import ViewSet, action

from ojas_ops.schemas.simulation import (
    RescheduleRequest,
    RescheduleResponse,
    SimulateDisruptionRequest,
    SimulateDisruptionResponse,
)
from ojas_ops.services.simulator import (
    reschedule_schedule_service,
    simulate_disruption_service,
)


class SimulationViewSet(ViewSet):
    """Class-Based ViewSet managing disruption impact simulations and reactive rescheduling."""

    @action(methods=["POST"], detail=False, path="simulate")
    async def simulate_disruptions(
        self,
        request,
        payload: SimulateDisruptionRequest,
    ) -> SimulateDisruptionResponse:
        """Simulate operational disruptions (delays, breakdowns, blackouts) on a baseline schedule."""
        return await simulate_disruption_service(payload)

    @action(methods=["POST"], detail=False, path="reschedule")
    async def reschedule_active(
        self,
        request,
        payload: RescheduleRequest,
    ) -> RescheduleResponse:
        """Perform reactive re-optimization balancing makespan with stability relative to baseline."""
        return await reschedule_schedule_service(payload)
