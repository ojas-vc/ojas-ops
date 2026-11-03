"""Base ViewSet with multi-tenant filtering and pagination."""

from __future__ import annotations

from typing import Any

from django_bolt import ModelViewSet, PageNumberPagination


class BaseOjasModelViewSet(ModelViewSet):
    """Base ModelViewSet providing tenant isolation and standard pagination."""

    pagination_class = PageNumberPagination

    async def filter_queryset(self, queryset: Any) -> Any:
        """Filter queryset by tenant_id query parameter when provided."""
        tenant_id = None
        if hasattr(self.request, "query") and isinstance(self.request.query, dict):
            tenant_id = self.request.query.get("tenant_id")
        elif hasattr(self.request, "GET"):
            tenant_id = self.request.GET.get("tenant_id")
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        return queryset
