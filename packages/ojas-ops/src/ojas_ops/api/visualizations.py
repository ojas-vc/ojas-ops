"""Class-Based ViewSet for Visualizations and HTML/SVG export."""

from django_bolt import ViewSet, action

from ojas_ops.schemas.visualizations import (
    DOODRenderRequest,
    GanttRenderRequest,
    RenderHtmlResponse,
    RenderSvgResponse,
    ReportExportRequest,
    StripboardRenderRequest,
)
from ojas_ops.visualization.dood import DOODRenderer
from ojas_ops.visualization.gantt import GanttRenderer
from ojas_ops.visualization.html_exporter import export_standalone_html
from ojas_ops.visualization.stripboard import StripboardRenderer


class VisualizationViewSet(ViewSet):
    """Class-Based ViewSet managing graphical visualizers and document export."""

    @action(methods=["POST"], detail=False, path="stripboard/html")
    async def render_stripboard_html(
        self,
        request,
        payload: StripboardRenderRequest,
    ) -> RenderHtmlResponse:
        """Render an interactive HTML film production stripboard table with day breaks."""
        html_content = StripboardRenderer.render_html(payload.stripboard_data)
        return RenderHtmlResponse(html=html_content)

    @action(methods=["POST"], detail=False, path="stripboard/svg")
    async def render_stripboard_svg(
        self,
        request,
        payload: StripboardRenderRequest,
    ) -> RenderSvgResponse:
        """Render a vector SVG graphic of a film production stripboard."""
        svg_content = StripboardRenderer.render_svg(payload.stripboard_data, width=payload.width)
        return RenderSvgResponse(svg=svg_content)

    @action(methods=["POST"], detail=False, path="dood/html")
    async def render_dood_html(
        self,
        request,
        payload: DOODRenderRequest,
    ) -> RenderHtmlResponse:
        """Render an interactive HTML Day Out of Days (DOOD) cast utilization matrix."""
        html_content = DOODRenderer.render_html(
            payload.reports,
            total_days=payload.total_days,
            currency_symbol=payload.currency_symbol,
        )
        return RenderHtmlResponse(html=html_content)

    @action(methods=["POST"], detail=False, path="gantt/svg")
    async def render_gantt_svg(
        self,
        request,
        payload: GanttRenderRequest,
    ) -> RenderSvgResponse:
        """Render a vector SVG Gantt chart timeline with discrete resource rows."""
        svg_content = GanttRenderer.render_svg(
            schedule_tasks=payload.tasks,
            resources=payload.resources,
            total_makespan=payload.total_makespan,
            width=payload.width,
            height_per_row=payload.height_per_row,
        )
        return RenderSvgResponse(svg=svg_content)

    @action(methods=["POST"], detail=False, path="report/html")
    async def export_report_html(
        self,
        request,
        payload: ReportExportRequest,
    ) -> RenderHtmlResponse:
        """Export a standalone, responsive, print-ready HTML page embedding schedule fragments."""
        page_html = export_standalone_html(
            title=payload.title,
            sections=payload.sections,
            subtitle=payload.subtitle,
        )
        return RenderHtmlResponse(html=page_html)
