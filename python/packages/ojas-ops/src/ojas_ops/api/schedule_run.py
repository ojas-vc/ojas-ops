"""ModelViewSet for ScheduleRun records."""

from __future__ import annotations

from ojas_ops.api.base import BaseOjasModelViewSet
from ojas_ops.models.schedule_run import ScheduleRun
from ojas_ops.serializers.schedule_run import (
    ScheduleRunCreateSerializer,
    ScheduleRunSerializer,
)


class ScheduleRunModelViewSet(BaseOjasModelViewSet):
    """Full ModelViewSet providing CRUD endpoints for ScheduleRun records on /schedule-runs."""

    queryset = ScheduleRun.objects.all().order_by("-created_at")
    serializer_class = ScheduleRunSerializer
    create_serializer_class = ScheduleRunCreateSerializer
    lookup_field = "id"
