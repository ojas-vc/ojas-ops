"""Django-Bolt ModelViewSet definitions for ORM models."""

from django_bolt import ModelViewSet, PageNumberPagination

from ojas_ops.api.serializers import (
    DisruptionLogCreateSerializer,
    DisruptionLogSerializer,
    OptimizationJobCreateSerializer,
    OptimizationJobSerializer,
    ScenarioRecordCreateSerializer,
    ScenarioRecordSerializer,
    ScheduleRunCreateSerializer,
    ScheduleRunSerializer,
)
from ojas_ops.models.disruption_log import DisruptionLog
from ojas_ops.models.optimization_job import OptimizationJob
from ojas_ops.models.scenario_record import ScenarioRecord
from ojas_ops.models.schedule_run import ScheduleRun


class BaseOjasModelViewSet(ModelViewSet):
    """Base ModelViewSet adding tenant filtering and standard pagination."""

    pagination_class = PageNumberPagination

    async def filter_queryset(self, queryset):
        """Filter queryset by tenant_id query parameter when provided."""
        tenant_id = None
        if hasattr(self.request, "query") and isinstance(self.request.query, dict):
            tenant_id = self.request.query.get("tenant_id")
        elif hasattr(self.request, "GET"):
            tenant_id = self.request.GET.get("tenant_id")
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        return queryset


class ScheduleRunModelViewSet(BaseOjasModelViewSet):
    """Full ModelViewSet providing CRUD endpoints for ScheduleRun records."""

    queryset = ScheduleRun.objects.all().order_by("-created_at")
    serializer_class = ScheduleRunSerializer
    create_serializer_class = ScheduleRunCreateSerializer


class OptimizationJobModelViewSet(BaseOjasModelViewSet):
    """Full ModelViewSet providing CRUD endpoints for OptimizationJob records."""

    queryset = OptimizationJob.objects.all().order_by("-created_at")
    serializer_class = OptimizationJobSerializer
    create_serializer_class = OptimizationJobCreateSerializer


class ScenarioRecordModelViewSet(BaseOjasModelViewSet):
    """Full ModelViewSet providing CRUD endpoints for ScenarioRecord records."""

    queryset = ScenarioRecord.objects.all().order_by("-created_at")
    serializer_class = ScenarioRecordSerializer
    create_serializer_class = ScenarioRecordCreateSerializer


class DisruptionLogModelViewSet(BaseOjasModelViewSet):
    """Full ModelViewSet providing CRUD endpoints for DisruptionLog records."""

    queryset = DisruptionLog.objects.all().order_by("-created_at")
    serializer_class = DisruptionLogSerializer
    create_serializer_class = DisruptionLogCreateSerializer
