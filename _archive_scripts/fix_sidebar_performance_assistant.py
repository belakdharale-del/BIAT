from pathlib import Path
import re

pages = [
    "performance_mod_le_biat_risk_monitor/code.html",
    "assistant_ia_biat_risk_monitor/code.html",
]

SIDEBAR = r'''
<!-- BIAT_STANDARD_SIDEBAR -->
<aside class="biat-sidebar">
  <div class="biat-brand">
    <h1>BIAT Risk<br>Monitor</h1>
    <p>Vigilant Professionalism</p>
  </div>

  <nav class="biat-nav">
    <a href="/dashboard" data-route="/dashboard"><span class="material-symbols-outlined">dashboard</span>Global Dashboard</a>
    <a href="/evolution" data-route="/evolution"><span class="material-symbols-outlined">trending_up</span>Risk Evolution</a>
    <a href="/future" data-route="/future"><span class="material-symbols-outlined">online_prediction</span>Future Prediction</a>
    <a href="/notifications" data-route="/notifications"><span class="material-symbols-outlined">notifications</span>Notifications <b id="notifBadge">4847</b></a>
    <a href="/client" data-route="/client"><span class="material-symbols-outlined">group</span>Client Profiles</a>
    <a href="/performance" data-route="/performance"><span class="material-symbols-outlined">analytics</span>Model Performance</a>
    <a href="/assistant" data-route="/assistant"><span class="material-symbols-outlined">smart_toy</span>AI Assistant</a>
  </nav>

  <div class="biat-sidebar-bottom">
    <button onclick="window.location.href='/notifications?alert=CRITICAL'" class="critical-btn">
      <span class="material-symbols-outlined">warning</span>
      Critical Alerts
    </button>

    <button onclick="alert('Settings - BIAT Risk Monitor')" class="side-btn">
      <span class="material-symbols-outlined">settings</span>
      Settings
    </button>

    <button onclick="alert('Support - BIAT Risk Monitor')" class="side-btn">
      <span class="material-symbols-outlined">help</span>
      Support
    </button>
  </div>
</aside>
<!-- END BIAT_STANDARD_SIDEBAR -->
'''

CSS = r'''
<!-- BIAT_STANDARD_SIDEBAR_CSS -->
<style id="biat-standard-sidebar-css">
  body {
    padding-left: 240px !important;
    overflow-x: hidden !important;
  }

  .biat-sidebar {
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    width: 240px !important;
    min-width: 240px !important;
    height: 100vh !important;
    z-index: 99999 !important;
    background: #07122a !important;
    border-right: 1px solid #263452 !important;
    display: flex !important;
    flex-direction: column !important;
    color: #d9e2ff !important;
    font-family: Inter, Arial, sans-serif !important;
  }

  .biat-brand {
    padding: 28px 20px 22px 20px !important;
  }

  .biat-brand h1 {
    margin: 0 !important;
    color: white !important;
    font-size: 25px !important;
    line-height: 1.15 !important;
    font-weight: 800 !important;
  }

  .biat-brand p {
    margin-top: 8px !important;
    color: #9aa8c7 !important;
    font-size: 13px !important;
  }

  .biat-nav {
    flex: 1 !important;
    padding: 0 14px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 7px !important;
  }

  .biat-nav a,
  .side-btn {
    min-height: 42px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    color: #b9c6e4 !important;
    text-decoration: none !important;
    font-family: "JetBrains Mono", monospace !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    background: transparent !important;
    border: 0 !important;
    cursor: pointer !important;
    width: 100% !important;
    text-align: left !important;
  }

  .biat-nav a:hover,
  .side-btn:hover {
    background: rgba(95,251,214,.08) !important;
    color: white !important;
  }

  .biat-nav a.active {
    background: rgba(121,143,185,.38) !important;
    color: white !important;
    font-weight: 800 !important;
  }

  .biat-nav .material-symbols-outlined,
  .side-btn .material-symbols-outlined {
    font-size: 22px !important;
  }

  #notifBadge {
    margin-left: auto !important;
    background: #ffb4ab !important;
    color: #690005 !important;
    border-radius: 999px !important;
    padding: 1px 7px !important;
    font-size: 10px !important;
  }

  .biat-sidebar-bottom {
    padding: 14px !important;
    border-top: 1px solid rgba(133,148,142,.25) !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
  }

  .critical-btn {
    width: 100% !important;
    min-height: 46px !important;
    background: #b00020 !important;
    color: white !important;
    border: 0 !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    cursor: pointer !important;
  }

  main,
  .main-content,
  #mainContent {
    margin-left: 0 !important;
    max-width: none !important;
  }

  header {
    left: 240px !important;
    width: calc(100% - 240px) !important;
  }
</style>
<!-- END BIAT_STANDARD_SIDEBAR_CSS -->
'''

JS = r'''
<!-- BIAT_STANDARD_SIDEBAR_JS -->
<script>
(function () {
  function activateSidebar() {
    const path = window.location.pathname;
    document.querySelectorAll(".biat-nav a").forEach(a => {
      if (a.getAttribute("data-route") === path) {
        a.classList.add("active");
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", activateSidebar);
  } else {
    activateSidebar();
  }
})();
</script>
<!-- END BIAT_STANDARD_SIDEBAR_JS -->
'''

for file in pages:
    path = Path(file)
    html = path.read_text(encoding="utf-8", errors="ignore")

    # backup
    backup = path.with_name("code_backup_before_sidebar_standard.html")
    backup.write_text(html, encoding="utf-8")

    # remove previous standard sidebar if exists
    html = re.sub(r'<!-- BIAT_STANDARD_SIDEBAR -->[\s\S]*?<!-- END BIAT_STANDARD_SIDEBAR -->', '', html)
    html = re.sub(r'<!-- BIAT_STANDARD_SIDEBAR_CSS -->[\s\S]*?<!-- END BIAT_STANDARD_SIDEBAR_CSS -->', '', html)
    html = re.sub(r'<!-- BIAT_STANDARD_SIDEBAR_JS -->[\s\S]*?<!-- END BIAT_STANDARD_SIDEBAR_JS -->', '', html)

    # ensure icons font exists
    if "Material+Symbols+Outlined" not in html:
        html = html.replace(
            "</head>",
            '<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />\n</head>'
        )

    # inject CSS in head
    html = html.replace("</head>", CSS + "\n</head>")

    # inject sidebar right after body
    html = re.sub(r'<body([^>]*)>', r'<body\1>' + "\n" + SIDEBAR, html, count=1)

    # inject JS before body end
    html = html.replace("</body>", JS + "\n</body>")

    path.write_text(html, encoding="utf-8")
    print("Sidebar injected:", file)

print("Done.")
