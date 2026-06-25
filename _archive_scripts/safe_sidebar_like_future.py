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

sidebar = r'''
<!-- BIAT_SAFE_FUTURE_STYLE_SIDEBAR -->
<style>
  body {
    padding-left: 240px !important;
  }

  .biat-sidebar {
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    width: 240px !important;
    height: 100vh !important;
    z-index: 99999 !important;
    background: #071126 !important;
    border-right: 1px solid rgba(148,163,184,.18) !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 24px 14px 16px 14px !important;
    box-sizing: border-box !important;
  }

  .biat-sidebar .brand {
    padding: 0 6px 28px 6px !important;
  }

  .biat-sidebar .brand h1 {
    margin: 0 !important;
    color: #f3f7ff !important;
    font-size: 26px !important;
    line-height: 1.14 !important;
    font-weight: 900 !important;
    letter-spacing: .2px !important;
    font-family: Inter, Arial, sans-serif !important;
  }

  .biat-sidebar .brand p {
    margin: 8px 0 0 0 !important;
    color: rgba(217,226,255,.72) !important;
    font-size: 13px !important;
    font-family: Inter, Arial, sans-serif !important;
  }

  .biat-sidebar nav {
    display: flex !important;
    flex-direction: column !important;
    gap: 7px !important;
  }

  .biat-sidebar .nav-link {
    height: 46px !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 0 14px !important;
    border-radius: 10px !important;
    color: #b9c6e4 !important;
    text-decoration: none !important;
    font-family: "JetBrains Mono", monospace !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    box-sizing: border-box !important;
    white-space: nowrap !important;
  }

  .biat-sidebar .nav-link:hover {
    background: rgba(95,251,214,.08) !important;
    color: #ffffff !important;
  }

  .biat-sidebar .nav-link.active {
    background: rgba(121,143,185,.35) !important;
    color: #ffffff !important;
    font-weight: 900 !important;
  }

  .biat-sidebar .material-symbols-outlined {
    font-size: 22px !important;
    width: 24px !important;
    min-width: 24px !important;
    line-height: 1 !important;
  }

  .biat-sidebar .badge {
    margin-left: auto !important;
    background: #ffb4ab !important;
    color: #3b0505 !important;
    border-radius: 999px !important;
    padding: 2px 7px !important;
    font-size: 10px !important;
    font-weight: 900 !important;
  }

  .biat-sidebar .bottom {
    margin-top: auto !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    border-top: 1px solid rgba(148,163,184,.16) !important;
    padding-top: 14px !important;
  }

  .biat-sidebar .critical-btn,
  .biat-sidebar .bottom-btn {
    height: 46px !important;
    width: 100% !important;
    border-radius: 10px !important;
    border: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    cursor: pointer !important;
    font-family: "JetBrains Mono", monospace !important;
    font-size: 13px !important;
    font-weight: 900 !important;
  }

  .biat-sidebar .critical-btn {
    background: #b00012 !important;
    color: white !important;
  }

  .biat-sidebar .bottom-btn {
    background: transparent !important;
    color: #b9c6e4 !important;
  }

  .biat-sidebar .bottom-btn:hover {
    background: rgba(95,251,214,.08) !important;
    color: white !important;
  }

  main {
    margin-left: 0 !important;
  }
</style>

<aside class="biat-sidebar">
  <div class="brand">
    <h1>BIAT Risk<br>Monitor</h1>
    <p>Vigilant Professionalism</p>
  </div>

  <nav>
    <a class="nav-link" data-route="/dashboard" href="/dashboard">
      <span class="material-symbols-outlined">dashboard</span>
      <span>Global Dashboard</span>
    </a>

    <a class="nav-link" data-route="/evolution" href="/evolution">
      <span class="material-symbols-outlined">trending_up</span>
      <span>Risk Evolution</span>
    </a>

    <a class="nav-link" data-route="/future" href="/future">
      <span class="material-symbols-outlined">online_prediction</span>
      <span>Future Prediction</span>
    </a>

    <a class="nav-link" data-route="/notifications" href="/notifications">
      <span class="material-symbols-outlined">notifications</span>
      <span>Notifications</span>
      <span class="badge" id="notifBadge">4847</span>
    </a>

    <a class="nav-link" data-route="/client" href="/client">
      <span class="material-symbols-outlined">group</span>
      <span>Client Profiles</span>
    </a>

    <a class="nav-link" data-route="/performance" href="/performance">
      <span class="material-symbols-outlined">analytics</span>
      <span>Model Performance</span>
    </a>

    <a class="nav-link" data-route="/assistant" href="/assistant">
      <span class="material-symbols-outlined">smart_toy</span>
      <span>AI Assistant</span>
    </a>
  </nav>

  <div class="bottom">
    <button type="button" class="critical-btn" id="criticalAlertsBtn">
      <span class="material-symbols-outlined">warning</span>
      <span>Critical Alerts</span>
    </button>

    <button type="button" class="bottom-btn" id="settingsBtn">
      <span class="material-symbols-outlined">settings</span>
      <span>Settings</span>
    </button>

    <button type="button" class="bottom-btn" id="supportBtn">
      <span class="material-symbols-outlined">help</span>
      <span>Support</span>
    </button>
  </div>
</aside>

<script>
(function () {
  const currentPath = window.location.pathname;

  document.querySelectorAll(".biat-sidebar .nav-link").forEach(link => {
    const route = link.getAttribute("data-route");

    if (route === currentPath || (route === "/client" && currentPath.startsWith("/client"))) {
      link.classList.add("active");
    }

    link.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = this.getAttribute("href");
    });
  });

  const criticalBtn = document.getElementById("criticalAlertsBtn");
  if (criticalBtn) {
    criticalBtn.onclick = function () {
      window.location.href = "/notifications?alert=CRITICAL";
    };
  }

  const settingsBtn = document.getElementById("settingsBtn");
  if (settingsBtn) {
    settingsBtn.onclick = function () {
      alert("Settings - BIAT Risk Monitor");
    };
  }

  const supportBtn = document.getElementById("supportBtn");
  if (supportBtn) {
    supportBtn.onclick = function () {
      alert("Support - BIAT Risk Monitor");
    };
  }
})();
</script>
<!-- END BIAT_SAFE_FUTURE_STYLE_SIDEBAR -->
'''

for file in pages:
    p = Path(file)
    if not p.exists():
        print("Missing:", file)
        continue

    html = p.read_text(encoding="utf-8", errors="ignore")
    p.with_name("code_backup_before_safe_future_sidebar.html").write_text(html, encoding="utf-8")

    # Remove old injected sidebar/style blocks only
    for marker in [
        "BIAT_SIDEBAR_VISUAL_FIX",
        "BIAT_SHARED_SIDEBAR_FINAL",
        "BIAT_UNIFIED_FUTURE_STYLE_SIDEBAR",
        "BIAT_SAFE_FUTURE_STYLE_SIDEBAR"
    ]:
        html = re.sub(
            rf'<!-- {marker} -->[\s\S]*?<!-- END {marker} -->',
            '',
            html
        )

    # Remove only BIAT sidebar, not assistant internal panels
    html = re.sub(
        r'<aside[^>]*class=["\'][^"\']*biat-sidebar[^"\']*["\'][\s\S]*?</aside>',
        '',
        html,
        flags=re.IGNORECASE
    )

    # Remove old real sidebar only if it contains BIAT Risk Monitor + Global Dashboard
    def remove_old_sidebar(match):
        block = match.group(0)
        low = block.lower()
        if "biat risk" in low and "global dashboard" in low:
            return ""
        return block

    html = re.sub(
        r'<aside[\s\S]*?</aside>',
        remove_old_sidebar,
        html,
        count=1,
        flags=re.IGNORECASE
    )

    # Inject safe sidebar immediately after body
    html = re.sub(
        r'<body([^>]*)>',
        r'<body\1>' + sidebar,
        html,
        count=1,
        flags=re.IGNORECASE
    )

    p.write_text(html, encoding="utf-8")
    print("Safe future-style sidebar installed:", file)

print("DONE.")
