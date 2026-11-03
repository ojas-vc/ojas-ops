"""Visualization request and response schemas."""

from typing import Any

import msgspec


class StripboardRenderRequest(msgspec.Struct, kw_only=True):
    """Request payload to render film production stripboard."""

    stripboard_data: dict[str, Any]
    width: int = 800


class DOODRenderRequest(msgspec.Struct, kw_only=True):
    """Request payload to render Day-Out-of-Days cast utilization matrix."""

    reports: list[dict[str, Any]]
    total_days: int = 10
    currency_symbol: str = "$"


class GanttRenderRequest(msgspec.Struct, kw_only=True):
    """Request payload to render machine or operational schedule Gantt chart."""

    tasks: list[dict[str, Any]]
    resources: list[str]
    total_makespan: int
    width: int = 900
    height_per_row: int = 40


class ReportExportRequest(msgspec.Struct, kw_only=True):
    """Request payload to export print-ready standalone HTML report."""

    title: str
    sections: list[str]
    subtitle: str = "Ojas Ops Combinatorial Optimization Report"


class RenderHtmlResponse(msgspec.Struct, kw_only=True):
    """Response containing rendered HTML fragment or document."""

    html: str


class RenderSvgResponse(msgspec.Struct, kw_only=True):
    """Response containing vector SVG string."""

    svg: str
