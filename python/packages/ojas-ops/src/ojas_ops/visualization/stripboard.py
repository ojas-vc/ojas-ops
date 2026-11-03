"""Master Stripboard SVG and HTML visual renderer for film production schedules."""

import html
from typing import Any

COLOR_MAP = {
    ("INT", "DAY"): {"bg": "#FFFFFF", "text": "#111827", "border": "#D1D5DB"},
    ("EXT", "DAY"): {"bg": "#FEF3C7", "text": "#78350F", "border": "#FDE68A"},
    ("INT", "NIGHT"): {"bg": "#D1FAE5", "text": "#065F46", "border": "#A7F3D0"},
    ("EXT", "NIGHT"): {"bg": "#DBEAFE", "text": "#1E40AF", "border": "#BFDBFE"},
}


class StripboardRenderer:
    """Renders film production schedules into industry-standard color-coded master stripboards."""

    @staticmethod
    def render_html(stripboard_data: dict[str, Any]) -> str:
        """Renders self-contained HTML stripboard table with day breaks."""
        title = html.escape(stripboard_data.get("project_title", "Master Stripboard"))
        total_days = stripboard_data.get("total_shoot_days", len(stripboard_data.get("days", [])))

        rows = []
        for day in stripboard_data.get("days", []):
            day_num = day.get("day_number", 1)
            date_str = day.get("date", f"Shoot Day {day_num}")
            total_pages = day.get("total_pages_eighths", 0) / 8.0

            # Day Break Strip (Black bar)
            rows.append(
                f'<div style="background:#111827; color:#F9FAFB; padding:8px 16px; margin-top:12px; '
                f'font-weight:bold; font-size:14px; border-radius:4px; display:flex; justify-content:space-between;">'
                f"<span>DAY {day_num} — {html.escape(str(date_str))}</span>"
                f"<span>{total_pages:.2f} Pages | {day.get('total_estimated_minutes', 0)} min</span>"
                f"</div>"
            )

            # Scene Strips
            for strip in day.get("strips", []):
                setting = strip.get("setting", "INT").upper()
                tod = strip.get("time_of_day", "DAY").upper()
                colors = COLOR_MAP.get((setting, tod), COLOR_MAP[("INT", "DAY")])

                scene_num = html.escape(str(strip.get("scene_number", "")))
                synopsis = html.escape(str(strip.get("synopsis", "")))
                location = html.escape(str(strip.get("location_name", "")))
                cast = html.escape(", ".join(str(c) for c in strip.get("character_numbers", [])))
                pages = strip.get("pages_eighths", 8) / 8.0

                rows.append(
                    f'<div style="background:{colors["bg"]}; color:{colors["text"]}; border:1px solid {colors["border"]}; '
                    f"padding:6px 12px; margin:2px 0; font-family:monospace; font-size:12px; "
                    f'display:flex; justify-content:space-between; align-items:center;">'
                    f'<span style="width:60px; font-weight:bold;">SC {scene_num}</span>'
                    f'<span style="width:100px;">{setting}. {tod}</span>'
                    f'<span style="flex:1; margin:0 8px;">{synopsis or location}</span>'
                    f'<span style="width:120px; color:#4B5563;">Cast: [{cast}]</span>'
                    f'<span style="width:60px; text-align:right;">{pages:.2f} pgs</span>'
                    f"</div>"
                )

        body_content = "\n".join(rows)
        return (
            f'<div style="font-family:system-ui, -apple-system, sans-serif; max-width:960px; margin:0 auto; padding:16px;">\n'
            f'  <h2 style="margin-bottom:4px; color:#111827;">{title}</h2>\n'
            f'  <p style="margin-top:0; color:#6B7280; font-size:14px;">Total Shoot Days: {total_days}</p>\n'
            f"  {body_content}\n"
            f"</div>"
        )

    @staticmethod
    def render_svg(stripboard_data: dict[str, Any], width: int = 800) -> str:
        """Renders an SVG stripboard graphic for document embedding."""
        strips_to_draw = []
        for day in stripboard_data.get("days", []):
            strips_to_draw.append({"type": "day", "data": day})
            for s in day.get("strips", []):
                strips_to_draw.append({"type": "scene", "data": s})

        strip_height = 24
        day_height = 30
        height = (
            sum(day_height if s["type"] == "day" else strip_height for s in strips_to_draw) + 60
        )

        svg_elements = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
            "<style>",
            "  .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #111827; }",
            "  .day-text { font-family: sans-serif; font-size: 12px; font-weight: bold; fill: #FFFFFF; }",
            "  .scene-text { font-family: monospace; font-size: 11px; fill: #111827; }",
            "</style>",
            f'<text x="10" y="25" class="title">{html.escape(stripboard_data.get("project_title", "Stripboard"))}</text>',
        ]

        y = 45
        for item in strips_to_draw:
            if item["type"] == "day":
                d = item["data"]
                svg_elements.append(
                    f'<rect x="10" y="{y}" width="{width - 20}" height="{day_height - 4}" fill="#111827" rx="3"/>'
                )
                svg_elements.append(
                    f'<text x="20" y="{y + 18}" class="day-text">DAY {d.get("day_number", 1)} — {d.get("total_pages_eighths", 0) / 8.0:.2f} pgs</text>'
                )
                y += day_height
            else:
                s = item["data"]
                setting = s.get("setting", "INT").upper()
                tod = s.get("time_of_day", "DAY").upper()
                colors = COLOR_MAP.get((setting, tod), COLOR_MAP[("INT", "DAY")])
                svg_elements.append(
                    f'<rect x="10" y="{y}" width="{width - 20}" height="{strip_height - 2}" fill="{colors["bg"]}" stroke="{colors["border"]}" stroke-width="1"/>'
                )
                txt = f"SC {s.get('scene_number', '')}  {setting}. {tod}  {s.get('location_name', '')}"
                svg_elements.append(
                    f'<text x="20" y="{y + 15}" class="scene-text" fill="{colors["text"]}">{html.escape(txt)}</text>'
                )
                y += strip_height

        svg_elements.append("</svg>")
        return "\n".join(svg_elements)
