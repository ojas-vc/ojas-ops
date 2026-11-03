"""Gantt Chart SVG and HTML visual renderer for discrete machine and operational schedules."""

import html
from typing import Any


class GanttRenderer:
    """Renders operational resource allocation and machine sequencing into SVG and HTML Gantt charts."""

    @staticmethod
    def render_svg(
        schedule_tasks: list[dict[str, Any]],
        resources: list[str],
        total_makespan: int,
        width: int = 900,
        height_per_row: int = 40,
    ) -> str:
        """Renders an SVG Gantt chart timeline with resource rows."""
        header_height = 50
        total_height = header_height + len(resources) * height_per_row + 40
        left_margin = 140
        right_margin = 30
        timeline_width = width - left_margin - right_margin
        scale_x = timeline_width / max(1, total_makespan)

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_height}" width="{width}" height="{total_height}">',
            "<style>",
            "  .label { font-family: sans-serif; font-size: 12px; fill: #374151; font-weight: 500; }",
            "  .time-tick { font-family: monospace; font-size: 10px; fill: #9CA3AF; }",
            "  .task-text { font-family: sans-serif; font-size: 11px; fill: #FFFFFF; font-weight: 600; }",
            "  .grid-line { stroke: #E5E7EB; stroke-dasharray: 2,2; }",
            "</style>",
            f'<text x="10" y="30" font-family="sans-serif" font-size="16px" font-weight="bold" fill="#111827">Schedule Gantt Chart (Makespan: {total_makespan}m)</text>',
        ]

        # Draw time axis ticks
        num_ticks = 6
        for i in range(num_ticks + 1):
            t = int(total_makespan * (i / num_ticks))
            x = left_margin + int(t * scale_x)
            svg_parts.append(
                f'<line x1="{x}" y1="{header_height}" x2="{x}" y2="{total_height - 30}" class="grid-line" />'
            )
            svg_parts.append(
                f'<text x="{x}" y="{total_height - 15}" text-anchor="middle" class="time-tick">{t}m</text>'
            )

        # Map resource to row index
        res_row = {r: idx for idx, r in enumerate(resources)}

        # Draw resource rows
        for idx, res in enumerate(resources):
            y = header_height + idx * height_per_row
            svg_parts.append(
                f'<rect x="{left_margin}" y="{y}" width="{timeline_width}" height="{height_per_row - 4}" fill="#F9FAFB" rx="4"/>'
            )
            svg_parts.append(f'<text x="10" y="{y + 22}" class="label">{html.escape(res)}</text>')

        # Draw task blocks
        colors = ["#2563EB", "#059669", "#D97706", "#7C3AED", "#DB2777", "#4F46E5"]
        for task in schedule_tasks:
            res_id = task.get("resource")
            if res_id not in res_row:
                continue
            row_idx = res_row[res_id]
            start = task.get("start", 0)
            end = task.get("end", 0)
            duration = end - start

            block_x = left_margin + int(start * scale_x)
            block_w = max(4, int(duration * scale_x))
            block_y = header_height + row_idx * height_per_row + 4
            block_h = height_per_row - 12
            color = colors[hash(task.get("task_id", "")) % len(colors)]

            svg_parts.append(
                f'<rect x="{block_x}" y="{block_y}" width="{block_w}" height="{block_h}" '
                f'fill="{color}" rx="3"><title>{html.escape(task.get("task_id", ""))}: {start}-{end}m</title></rect>'
            )
            if block_w > 30:
                svg_parts.append(
                    f'<text x="{block_x + 6}" y="{block_y + 16}" class="task-text">{html.escape(task.get("task_id", ""))}</text>'
                )

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    @staticmethod
    def render_html(
        schedule_tasks: list[dict[str, Any]], resources: list[str], total_makespan: int
    ) -> str:
        """Renders standalone HTML containing SVG Gantt chart and task details table."""
        svg_content = GanttRenderer.render_svg(schedule_tasks, resources, total_makespan)
        return (
            f'<div style="font-family:system-ui, -apple-system, sans-serif; max-width:960px; margin:0 auto; padding:16px;">\n'
            f"  {svg_content}\n"
            f"</div>"
        )
