from pathlib import Path

path = Path("global_dashboard_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

replacements = {
    '<body class="soft-grid">': '<body>',
    '<body>': '<body>',
    'w-[290px]': 'w-[260px]',
    'ml-[290px]': 'ml-[260px]',
    'h-20': 'h-16',
    'p-7 space-y-6': 'p-5 space-y-4',
    'text-4xl': 'text-3xl',
    'text-3xl font-extrabold': 'text-2xl font-extrabold',
    'p-6': 'p-4',
    'p-5': 'p-4',
    'h-64': 'h-52',
    'text-2xl font-extrabold': 'text-xl font-extrabold',
    'rounded-xl': 'rounded-lg',
    'gap-6': 'gap-4',
    'gap-4': 'gap-3',
}

for old, new in replacements.items():
    html = html.replace(old, new)

# Remove aggressive glow if it exists
html = html.replace(" premium-glow", "")
html = html.replace("premium-glow ", "")

# Replace current CSS sizes with a softer BIAT compact style
html = html.replace(
'''    .card {
      background: rgba(16,27,51,.88);
      border: 1px solid rgba(95,251,214,.16);
      border-radius: 18px;
    }''',
'''    .card {
      background: rgba(16,27,51,.72);
      border: 1px solid rgba(133,148,142,.22);
      border-radius: 14px;
      box-shadow: 0 12px 35px rgba(0,0,0,.18);
    }'''
)

html = html.replace(
'''    .donut {
      width: 170px;
      height: 170px;''',
'''    .donut {
      width: 140px;
      height: 140px;'''
)

html = html.replace(
'''    .donut::after {
      content: "";
      position: absolute;
      inset: 25px;''',
'''    .donut::after {
      content: "";
      position: absolute;
      inset: 22px;'''
)

# Add softer background pattern
if "body::before" not in html:
    html = html.replace(
'''    body {
      margin: 0;
      background: #07122a;
      color: #d9e2ff;
      font-family: Inter, sans-serif;
    }''',
'''    body {
      margin: 0;
      background: #07122a;
      color: #d9e2ff;
      font-family: Inter, sans-serif;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(90deg, rgba(95,251,214,.035) 1px, transparent 1px),
        linear-gradient(rgba(95,251,214,.035) 1px, transparent 1px);
      background-size: 34px 34px;
      opacity: .65;
      z-index: -1;
    }'''
)

path.write_text(html, encoding="utf-8")
print("Soft dashboard design applied.")
