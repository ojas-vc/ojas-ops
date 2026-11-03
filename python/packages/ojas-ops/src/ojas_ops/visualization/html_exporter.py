"""Zero-dependency standalone HTML document exporter for operational schedules."""

import html


def export_standalone_html(
    title: str,
    sections: list[str],
    subtitle: str = "Ojas Ops Combinatorial Optimization Report",
) -> str:
    """Wraps visualization HTML/SVG fragments into a complete, responsive, print-ready HTML page."""
    escaped_title = html.escape(title)
    escaped_subtitle = html.escape(subtitle)
    body_content = "\n<hr style='border:0; border-top:1px solid #E5E7EB; margin:24px 0;'/>\n".join(
        sections
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escaped_title} — Ojas Ops</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #F9FAFB;
      color: #111827;
      margin: 0;
      padding: 24px;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      background: #FFFFFF;
      border: 1px solid #E5E7EB;
      border-radius: 8px;
      padding: 32px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}
    header {{
      border-bottom: 2px solid #111827;
      padding-bottom: 16px;
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 6px 0;
      font-size: 26px;
      color: #111827;
    }}
    .subtitle {{
      margin: 0;
      color: #6B7280;
      font-size: 14px;
    }}
    @media print {{
      body {{ background: #FFF; padding: 0; }}
      .container {{ border: none; box-shadow: none; padding: 0; max-width: 100%; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>{escaped_title}</h1>
      <p class="subtitle">{escaped_subtitle}</p>
    </header>
    <main>
      {body_content}
    </main>
  </div>
</body>
</html>
"""
