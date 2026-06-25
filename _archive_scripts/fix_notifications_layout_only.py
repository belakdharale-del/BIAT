from pathlib import Path
import re

path = Path("clients_notifier_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

# remove old notification layout fix if exists
html = re.sub(
    r'<!-- BIAT_NOTIFICATIONS_LAYOUT_FIX -->[\s\S]*?<!-- END BIAT_NOTIFICATIONS_LAYOUT_FIX -->',
    '',
    html
)

css = r'''
<!-- BIAT_NOTIFICATIONS_LAYOUT_FIX -->
<style id="biat-notifications-layout-fix">
  body {
    padding-left: 240px !important;
    overflow-x: hidden !important;
  }

  aside {
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    width: 240px !important;
    min-width: 240px !important;
    height: 100vh !important;
    z-index: 9999 !important;
  }

  main,
  .main-content,
  #mainContent {
    margin-left: 0 !important;
    width: 100% !important;
  }

  header {
    left: 240px !important;
    width: calc(100% - 240px) !important;
  }
</style>
<!-- END BIAT_NOTIFICATIONS_LAYOUT_FIX -->
'''

html = html.replace("</head>", css + "\n</head>")
path.write_text(html, encoding="utf-8")
print("Notifications layout fixed.")
