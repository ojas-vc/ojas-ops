"""ModelViewSet for DisruptionLog audit records."""

from __future__ import annotations

from ojas_ops.api.base import BaseOjasModelViewSet
from ojas_ops.models.disruption_log import DisruptionLog
from ojas_ops.serializers.disruption_log import (
    DisruptionLogCreateSerializer,
    DisruptionLogSerializer,
)


class DisruptionLogModelViewSet(BaseOjasModelViewSet):
    """Full ModelViewSet providing CRUD endpoints for DisruptionLog records on /disruption-logs."""

    queryset = DisruptionLog.objects.all().order_by("-created_at")
    serializer_class = DisruptionLogSerializer
    create_serializer_class = DisruptionLogCreateSerializer
    lookup_field = "id"
