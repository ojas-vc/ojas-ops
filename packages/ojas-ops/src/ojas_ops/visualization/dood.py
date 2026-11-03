"""Day Out of Days (DOOD) cast utilization matrix visual renderer."""

import html
from typing import Any

STATUS_STYLES = {
    "SW": {"bg": "#DBEAFE", "color": "#1E40AF"},
    "W": {"bg": "#D1FAE5", "color": "#065F46"},
    "H": {"bg": "#FEF3C7", "color": "#92400E"},
    "WF": {"bg": "#FEE2E2", "color": "#991B1B"},
    "SWF": {"bg": "#EDE9FE", "color": "#5B21B6"},
    "DROP": {"bg": "#F3F4F6", "color": "#6B7280"},
    "-": {"bg": "transparent", "color": "#D1D5DB"},
}


class DOODRenderer:
    """Renders Day Out of Days (DOOD) cast matrix with utilization metrics and hold liabilities."""

    @staticmethod
    def render_html(
        reports: list[dict[str, Any]],
        total_days: int = 10,
        currency_symbol: str = "$",
    ) -> str:
        """Renders an interactive HTML Day Out of Days matrix."""
        headers = ["ID", "Character / Performer"]
        for d in range(1, total_days + 1):
            headers.append(f"D{d}")
        headers.extend(["Work", "Hold", "Paid", "Hold Cost"])

        th_html = "".join(
            f'<th style="padding:8px; border:1px solid #E5E7EB; background:#F9FAFB; font-size:12px; font-weight:600;">{html.escape(h)}</th>'
            for h in headers
        )

        rows = []
        for r in reports:
            talent_id = html.escape(str(r.get("talent_id", "")))
            char_name = html.escape(str(r.get("character_name", "")))
            daily_status = r.get("daily_status", {})

            row_cells = [
                f'<td style="padding:6px 10px; border:1px solid #E5E7EB; font-family:monospace; font-size:12px;">{talent_id}</td>',
                f'<td style="padding:6px 10px; border:1px solid #E5E7EB; font-weight:500; font-size:13px;">{char_name}</td>',
            ]

            for d in range(1, total_days + 1):
                status = daily_status.get(str(d), daily_status.get(d, "-"))
                st = STATUS_STYLES.get(status, STATUS_STYLES["-"])
                row_cells.append(
                    f'<td style="padding:6px 4px; border:1px solid #E5E7EB; text-align:center; '
                    f'font-size:11px; font-weight:bold; background:{st["bg"]}; color:{st["color"]};">{status}</td>'
                )

            work_days = r.get("total_work_days", 0)
            hold_days = r.get("total_hold_days", 0)
            paid_days = r.get("total_paid_days", work_days + hold_days)
            hold_cost = r.get("hold_cost", 0.0)

            row_cells.append(
                f'<td style="padding:6px 8px; border:1px solid #E5E7EB; text-align:center; font-weight:600;">{work_days}</td>'
            )
            row_cells.append(
                f'<td style="padding:6px 8px; border:1px solid #E5E7EB; text-align:center; color:#B45309; font-weight:600;">{hold_days}</td>'
            )
            row_cells.append(
                f'<td style="padding:6px 8px; border:1px solid #E5E7EB; text-align:center; font-weight:600;">{paid_days}</td>'
            )
            row_cells.append(
                f'<td style="padding:6px 8px; border:1px solid #E5E7EB; text-align:right; font-family:monospace;">{currency_symbol}{hold_cost:,.2f}</td>'
            )

            rows.append(f"<tr>{''.join(row_cells)}</tr>")

        table_rows = "\n".join(rows)

        return (
            f'<div style="font-family:system-ui, -apple-system, sans-serif; max-width:1100px; margin:0 auto; padding:16px;">\n'
            f'  <h2 style="margin-bottom:4px; color:#111827;">Day Out of Days (DOOD) Cast Matrix</h2>\n'
            f'  <p style="margin-top:0; color:#6B7280; font-size:13px;">\n'
            f'    Legend: <span style="background:#DBEAFE; color:#1E40AF; padding:2px 6px; border-radius:3px;">SW = Start Work</span>\n'
            f'    <span style="background:#D1FAE5; color:#065F46; padding:2px 6px; border-radius:3px;">W = Work</span>\n'
            f'    <span style="background:#FEF3C7; color:#92400E; padding:2px 6px; border-radius:3px;">H = Hold</span>\n'
            f'    <span style="background:#FEE2E2; color:#991B1B; padding:2px 6px; border-radius:3px;">WF = Work Finish</span>\n'
            f"  </p>\n"
            f'  <div style="overflow-x:auto;">\n'
            f'    <table style="border-collapse:collapse; width:100%; border:1px solid #E5E7EB;">\n'
            f"      <thead><tr>{th_html}</tr></thead>\n"
            f"      <tbody>{table_rows}</tbody>\n"
            f"    </table>\n"
            f"  </div>\n"
            f"</div>"
        )
