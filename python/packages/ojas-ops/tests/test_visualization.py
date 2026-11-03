"""Unit tests for schedule visual renderers (Stripboard, DOOD, Gantt, HTML exporter)."""

from ojas_ops.visualization import (
    DOODRenderer,
    GanttRenderer,
    StripboardRenderer,
    export_standalone_html,
)


def test_stripboard_renderer():
    data = {
        "project_title": "Interstellar Odyssey",
        "total_shoot_days": 2,
        "days": [
            {
                "day_number": 1,
                "date": "2026-11-10",
                "total_pages_eighths": 24,
                "total_estimated_minutes": 240,
                "strips": [
                    {
                        "scene_number": "1A",
                        "setting": "INT",
                        "time_of_day": "DAY",
                        "location_name": "Spaceship Cockpit",
                        "character_numbers": [1, 2],
                        "pages_eighths": 16,
                    },
                    {
                        "scene_number": "2",
                        "setting": "EXT",
                        "time_of_day": "NIGHT",
                        "location_name": "Alien Crater",
                        "character_numbers": [1],
                        "pages_eighths": 8,
                    },
                ],
            }
        ],
    }

    html = StripboardRenderer.render_html(data)
    assert "Interstellar Odyssey" in html
    assert "DAY 1" in html
    assert "SC 1A" in html
    assert "#FFFFFF" in html  # INT.DAY white bg
    assert "#DBEAFE" in html  # EXT.NIGHT blue bg

    svg = StripboardRenderer.render_svg(data)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "DAY 1" in svg
    assert "SC 1A" in svg


def test_dood_renderer():
    reports = [
        {
            "talent_id": "T1",
            "character_name": "Commander Stone",
            "daily_status": {"1": "SW", "2": "H", "3": "WF"},
            "total_work_days": 2,
            "total_hold_days": 1,
            "total_paid_days": 3,
            "hold_cost": 2500.0,
        },
        {
            "talent_id": "T2",
            "character_name": "Navigator Vega",
            "daily_status": {"1": "W", "2": "W", "3": "W"},
            "total_work_days": 3,
            "total_hold_days": 0,
            "total_paid_days": 3,
            "hold_cost": 0.0,
        },
    ]

    html = DOODRenderer.render_html(reports, total_days=3)
    assert "Day Out of Days (DOOD)" in html
    assert "Commander Stone" in html
    assert "Navigator Vega" in html
    assert "SW" in html
    assert "H" in html
    assert "$2,500.00" in html


def test_gantt_renderer():
    tasks = [
        {"task_id": "Milling_1", "resource": "Mill", "start": 0, "end": 60},
        {"task_id": "Drilling_1", "resource": "Drill", "start": 60, "end": 120},
        {"task_id": "Milling_2", "resource": "Mill", "start": 90, "end": 150},
    ]
    resources = ["Mill", "Drill"]

    svg = GanttRenderer.render_svg(tasks, resources, total_makespan=150)
    assert "<svg" in svg
    assert "Mill" in svg
    assert "Drill" in svg
    assert "Milling_1" in svg
    assert "150m" in svg

    html = GanttRenderer.render_html(tasks, resources, total_makespan=150)
    assert "<svg" in html


def test_export_standalone_html():
    s1 = "<div>Section 1</div>"
    s2 = "<div>Section 2</div>"
    doc = export_standalone_html("Production Report", [s1, s2])
    assert "<!DOCTYPE html>" in doc
    assert "<title>Production Report — Ojas Ops</title>" in doc
    assert "Section 1" in doc
    assert "Section 2" in doc
