from pathlib import Path

path = Path("global_dashboard_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

old_css = '''
    .bar {
      border-radius: 10px 10px 0 0;
      background: #5ffbd6;
      min-height: 8px;
    }
'''

new_css = '''
    .bar {
      border-radius: 10px 10px 0 0;
      background: #5ffbd6;
      min-height: 8px;
    }

    select,
    input {
      color-scheme: dark;
    }

    select {
      appearance: none;
      background-image:
        linear-gradient(45deg, transparent 50%, #9aa8c7 50%),
        linear-gradient(135deg, #9aa8c7 50%, transparent 50%);
      background-position:
        calc(100% - 20px) calc(50% - 3px),
        calc(100% - 14px) calc(50% - 3px);
      background-size: 6px 6px, 6px 6px;
      background-repeat: no-repeat;
      cursor: pointer;
    }

    select option {
      background: #101b33;
      color: #d9e2ff;
    }

    .premium-glow {
      box-shadow: 0 0 0 1px rgba(95,251,214,.08), 0 18px 60px rgba(0,0,0,.28);
    }

    .soft-grid {
      background-image:
        linear-gradient(rgba(95,251,214,.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(95,251,214,.045) 1px, transparent 1px);
      background-size: 32px 32px;
    }
'''

html = html.replace(old_css, new_css)

html = html.replace(
    '<body>',
    '<body class="soft-grid">'
)

html = html.replace(
    'class="card p-5"',
    'class="card p-5 premium-glow"'
)

html = html.replace(
    'class="card p-6"',
    'class="card p-6 premium-glow"'
)

html = html.replace(
    'class="card overflow-hidden"',
    'class="card overflow-hidden premium-glow"'
)

path.write_text(html, encoding="utf-8")
print("Dashboard design patch applied.")
