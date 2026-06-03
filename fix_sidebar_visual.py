from pathlib import Path
import re

pages = [
    "global_dashboard_biat_risk_monitor/code.html",
    "risk_evolution_biat_risk_monitor/code.html",
    "future_prediction_biat_risk_monitor/code.html",
    "clients_notifier_biat_risk_monitor/code.html",
    "fiche_client_biat_risk_monitor/code.html",
    "performance_mod_le_biat_risk_monitor/code.html",
    "assistant_ia_biat_risk_monitor/code.html",
]

css = r'''
<!-- BIAT_SIDEBAR_VISUAL_FIX -->
<style>
  aside {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    left: 0 !important;
    top: 0 !important;
    height: 100vh !important;
    position: fixed !important;
    overflow: hidden !important;
    z-index: 9999 !important;
    background: #071126 !important;
    border-right: 1px solid rgba(133,148,142,.22) !important;
  }

  aside h1 {
    font-size: 26px !important;
    line-height: 1.15 !important;
    margin: 0 !important;
    color: #f3f7ff !important;
    letter-spacing: .2px !important;
  }

  aside p {
    font-size: 13px !important;
    margin-top: 8px !important;
    color: rgba(217,226,255,.75) !important;
  }

  aside nav {
    margin-top: 22px !important;
    padding: 0 14px !important;
  }

  aside nav a,
  aside a,
  aside button {
    display: flex !important;
    align-items: center !important;
    gap: 14px !important;
    width: 100% !important;
    min-height: 46px !important;
    padding: 0 16px !important;
    box-sizing: border-box !important;
    border-radius: 10px !important;
    text-decoration: none !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    color: rgba(217,226,255,.82) !important;
    font-size: 14px !important;
    font-weight: 700 !important;
  }

  aside nav a:hover,
  aside a:hover {
    background: rgba(148,163,184,.18) !important;
    color: #ffffff !important;
  }

  aside nav a.bg-surface-variant,
  aside nav a[class*="bg-surface-variant"],
  aside nav a.active,
  aside nav a[aria-current="page"] {
    background: rgba(148,163,184,.28) !important;
    color: #ffffff !important;
  }

  aside .material-symbols-outlined {
    font-size: 22px !important;
    min-width: 24px !important;
    width: 24px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
  }

  aside span:not(.material-symbols-outlined) {
    display: inline-block !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }

  aside button {
    justify-content: center !important;
    background: #b00012 !important;
    color: white !important;
    border: none !important;
    cursor: pointer !important;
  }

  main,
  .main-content,
  body > div:not(aside) {
    margin-left: 240px;
  }

  @media (max-width: 900px) {
    aside {
      width: 220px !important;
      min-width: 220px !important;
      max-width: 220px !important;
    }

    main,
    .main-content,
    body > div:not(aside) {
      margin-left: 220px;
    }
  }
</style>
<!-- END BIAT_SIDEBAR_VISUAL_FIX -->
'''

for file in pages:
    p = Path(file)
    if not p.exists():
        continue

    html = p.read_text(encoding="utf-8", errors="ignore")
    p.with_name("code_backup_before_sidebar_visual_fix.html").write_text(html, encoding="utf-8")

    html = re.sub(
        r'<!-- BIAT_SIDEBAR_VISUAL_FIX -->[\s\S]*?<!-- END BIAT_SIDEBAR_VISUAL_FIX -->',
        '',
        html
    )

    html = html.replace("</head>", css + "\n</head>")
    p.write_text(html, encoding="utf-8")
    print("Sidebar visual fixed:", file)

print("Done.")
