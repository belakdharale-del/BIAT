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

shared = r'''
<!-- BIAT_SHARED_SIDEBAR_FINAL -->
<style>
  aside.biat-sidebar {
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    width: 240px !important;
    height: 100vh !important;
    z-index: 9999 !important;
    background: #071126 !important;
    border-right: 1px solid rgba(148,163,184,.18) !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 26px 14px 16px 14px !important;
    box-sizing: border-box !important;
    font-family: Inter, Arial, sans-serif !important;
  }

  aside.biat-sidebar .brand {
    padding: 0 8px 26px 8px !important;
  }

  aside.biat-sidebar .brand h1 {
    margin: 0 !important;
    font-size: 28px !important;
    line-height: 1.12 !important;
    font-weight: 900 !important;
    color: #f3f7ff !important;
    letter-spacing: .2px !important;
  }

  aside.biat-sidebar .brand p {
    margin: 8px 0 0 0 !important;
    font-size: 14px !important;
    color: rgba(217,226,255,.72) !important;
  }

  aside.biat-sidebar nav {
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
  }

  aside.biat-sidebar .nav-link {
    height: 46px !important;
    display: flex !important;
    align-items: center !important;
    gap: 13px !important;
    padding: 0 16px !important;
    border-radius: 10px !important;
    color: rgba(217,226,255,.82) !important;
    text-decoration: none !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    box-sizing: border-box !important;
    white-space: nowrap !important;
  }

  aside.biat-sidebar .nav-link:hover {
    background: rgba(148,163,184,.14) !important;
    color: white !important;
  }

  aside.biat-sidebar .nav-link.active {
    background: rgba(148,163,184,.28) !important;
    color: white !important;
  }

  aside.biat-sidebar .material-symbols-outlined {
    font-size: 22px !important;
    width: 24px !important;
    min-width: 24px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
  }

  aside.biat-sidebar .badge {
    margin-left: auto !important;
    background: #ffb4ab !important;
    color: #3b0505 !important;
    border-radius: 999px !important;
    padding: 2px 7px !important;
    font-size: 10px !important;
    font-weight: 800 !important;
  }

  aside.biat-sidebar .bottom {
    margin-top: auto !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    border-top: 1px solid rgba(148,163,184,.16) !important;
    padding-top: 14px !important;
  }

  aside.biat-sidebar .critical-btn,
  aside.biat-sidebar .bottom-btn {
    height: 46px !important;
    width: 100% !important;
    border-radius: 10px !important;
    border: 0 !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    font-size: 14px !important;
    font-weight: 800 !important;
  }

  aside.biat-sidebar .critical-btn {
    background: #b00012 !important;
    color: white !important;
  }

  aside.biat-sidebar .bottom-btn {
    background: transparent !important;
    color: rgba(217,226,255,.82) !important;
  }

  aside.biat-sidebar .bottom-btn:hover {
    background: rgba(148,163,184,.14) !important;
    color: white !important;
  }

  body {
    padding-left: 240px !important;
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
  const path = window.location.pathname;

  document.querySelectorAll(".biat-sidebar .nav-link").forEach(link => {
    const route = link.getAttribute("data-route");
    if (route === path || (route === "/client" && path.startsWith("/client"))) {
      link.classList.add("active");
    }
  });

  document.querySelectorAll(".biat-sidebar a[href]").forEach(link => {
    link.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (href && href.startsWith("/")) {
        e.preventDefault();
        window.location.href = href;
      }
    });
  });

  const criticalBtn = document.getElementById("criticalAlertsBtn");
  if (criticalBtn) {
    criticalBtn.addEventListener("click", function () {
      window.location.href = "/notifications?alert=CRITICAL";
    });
  }

  const settingsBtn = document.getElementById("settingsBtn");
  if (settingsBtn) {
    settingsBtn.addEventListener("click", function () {
      alert("Settings - BIAT Risk Monitor\\n\\nParamètres locaux : thème sombre, navigation, seuils de risque et préférences d'affichage.");
    });
  }

  const supportBtn = document.getElementById("supportBtn");
  if (supportBtn) {
    supportBtn.addEventListener("click", function () {
      alert("Support - BIAT Risk Monitor\\n\\nPages disponibles : Dashboard, Risk Evolution, Future Prediction, Notifications, Client Profiles, Model Performance, AI Assistant.");
    });
  }
})();
</script>
<!-- END BIAT_SHARED_SIDEBAR_FINAL -->
'''

for file in pages:
    p = Path(file)
    if not p.exists():
        print("Missing:", file)
        continue

    html = p.read_text(encoding="utf-8", errors="ignore")
    p.with_name("code_backup_before_shared_sidebar_final.html").write_text(html, encoding="utf-8")

    # Remove old shared sidebar block if exists
    html = re.sub(
        r'<!-- BIAT_SHARED_SIDEBAR_FINAL -->[\s\S]*?<!-- END BIAT_SHARED_SIDEBAR_FINAL -->',
        '',
        html
    )

    # Remove first existing aside only
    html = re.sub(
        r'<aside[\s\S]*?</aside>',
        shared,
        html,
        count=1,
        flags=re.IGNORECASE
    )

    p.write_text(html, encoding="utf-8")
    print("Shared sidebar installed:", file)

print("Done.")
