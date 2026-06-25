from pathlib import Path
import re

PAGES = [
    "global_dashboard_biat_risk_monitor/code.html",
    "risk_evolution_biat_risk_monitor/code.html",
    "future_prediction_biat_risk_monitor/code.html",
    "clients_notifier_biat_risk_monitor/code.html",
    "fiche_client_biat_risk_monitor/code.html",
    "performance_mod_le_biat_risk_monitor/code.html",
    "assistant_ia_biat_risk_monitor/code.html",
]

SIDEBAR = r'''
<!-- BIAT SHARED SIDEBAR -->
<aside class="fixed left-0 top-0 h-screen w-64 bg-[#07122a] border-r border-[#263452] z-50 flex flex-col">
  <div class="px-5 pt-7 pb-6">
    <h1 class="text-2xl font-extrabold text-white leading-tight tracking-tight">
      BIAT Risk<br>Monitor
    </h1>
    <p class="text-sm text-[#9aa8c7] mt-2">Vigilant Professionalism</p>
  </div>

  <nav id="mainNav" class="flex-1 px-4 space-y-2">
    <a data-route="/dashboard" href="/dashboard" class="biat-nav-link">
      <span class="material-symbols-outlined text-[22px]">dashboard</span>
      <span>Global Dashboard</span>
    </a>

    <a data-route="/evolution" href="/evolution" class="biat-nav-link">
      <span class="material-symbols-outlined text-[22px]">trending_up</span>
      <span>Risk Evolution</span>
    </a>

    <a data-route="/future" href="/future" class="biat-nav-link">
      <span class="material-symbols-outlined text-[22px]">online_prediction</span>
      <span>Future Prediction</span>
    </a>

    <a data-route="/notifications" href="/notifications" class="biat-nav-link relative">
      <span class="material-symbols-outlined text-[22px]">notifications</span>
      <span>Notifications</span>
      <span id="notifBadge" class="absolute right-3 bg-[#ffb4ab] text-[#690005] text-[10px] px-2 py-0.5 rounded-full">0</span>
    </a>

    <a data-route="/client" href="/client" class="biat-nav-link">
      <span class="material-symbols-outlined text-[22px]">group</span>
      <span>Client Profiles</span>
    </a>

    <a data-route="/performance" href="/performance" class="biat-nav-link">
      <span class="material-symbols-outlined text-[22px]">analytics</span>
      <span>Model Performance</span>
    </a>

    <a data-route="/assistant" href="/assistant" class="biat-nav-link">
      <span class="material-symbols-outlined text-[22px]">smart_toy</span>
      <span>AI Assistant</span>
    </a>
  </nav>

  <div class="px-4 pb-4 space-y-2">
    <button id="criticalAlertsBtn" class="w-full flex items-center justify-center gap-2 bg-[#b00020] text-white py-3 rounded-lg font-bold">
      <span class="material-symbols-outlined text-[20px]">warning</span>
      <span>Critical Alerts</span>
    </button>

    <button id="settingsBtn" class="biat-nav-link w-full">
      <span class="material-symbols-outlined text-[22px]">settings</span>
      <span>Settings</span>
    </button>

    <button id="supportBtn" class="biat-nav-link w-full">
      <span class="material-symbols-outlined text-[22px]">help</span>
      <span>Support</span>
    </button>
  </div>
</aside>
<!-- END BIAT SHARED SIDEBAR -->
'''

CSS = r'''
<!-- BIAT SIDEBAR CSS -->
<style id="biat-sidebar-css">
  .biat-nav-link {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    min-height: 44px;
    padding: 10px 14px;
    border-radius: 10px;
    color: #b9c6e4;
    font-family: "JetBrains Mono", monospace;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    transition: background .15s ease, color .15s ease;
  }

  .biat-nav-link:hover {
    background: rgba(95, 251, 214, .08);
    color: #ffffff;
  }

  .biat-nav-active {
    background: rgba(121, 143, 185, .35) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
  }
</style>
<!-- END BIAT SIDEBAR CSS -->
'''

SCRIPT = r'''
<!-- BIAT SHARED SIDEBAR SCRIPT -->
<script id="biat-shared-sidebar-script">
document.addEventListener("DOMContentLoaded", function () {
  const currentPath = window.location.pathname.toLowerCase();

  document.querySelectorAll("#mainNav .biat-nav-link").forEach(function(link) {
    const route = link.getAttribute("data-route");
    const isActive =
      route &&
      (
        currentPath === route ||
        currentPath.startsWith(route + "/") ||
        (route === "/client" && currentPath.startsWith("/client")) ||
        (route === "/notifications" && currentPath.startsWith("/notifications")) ||
        (route === "/future" && currentPath.startsWith("/future")) ||
        (route === "/evolution" && currentPath.startsWith("/evolution")) ||
        (route === "/performance" && currentPath.startsWith("/performance")) ||
        (route === "/assistant" && currentPath.startsWith("/assistant"))
      );

    link.classList.toggle("biat-nav-active", !!isActive);
  });

  const criticalBtn = document.getElementById("criticalAlertsBtn");
  if (criticalBtn) {
    criticalBtn.onclick = function () {
      window.location.href = "/notifications?alert=CRITICAL";
    };
  }

  const settingsBtn = document.getElementById("settingsBtn");
  if (settingsBtn) {
    settingsBtn.onclick = function (e) {
      e.preventDefault();
      alert("Settings - BIAT Risk Monitor\nUser: ALA\nRole: Risk Officer");
    };
  }

  const supportBtn = document.getElementById("supportBtn");
  if (supportBtn) {
    supportBtn.onclick = function (e) {
      e.preventDefault();
      alert("Support - BIAT Risk Monitor");
    };
  }

  fetch("/api/future-predictions", { cache: "no-store" })
    .then(r => r.ok ? r.json() : null)
    .then(data => {
      const badge = document.getElementById("notifBadge");
      if (!badge || !data || !data.summary) return;
      const n = data.summary.critical_future_clients || data.summary.aggravation_clients || 0;
      badge.innerText = Number(n).toLocaleString("fr-FR");
    })
    .catch(() => {});
});
</script>
<!-- END BIAT SHARED SIDEBAR SCRIPT -->
'''

def patch_page(file):
    path = Path(file)
    if not path.exists():
        print("MISSING:", file)
        return

    html = path.read_text(encoding="utf-8", errors="ignore")

    backup = path.with_name("code_backup_before_clean_standard_sidebar.html")
    if not backup.exists():
        backup.write_text(html, encoding="utf-8")

    # Remove old shared sidebar/script/css
    html = re.sub(r'<!-- BIAT SHARED SIDEBAR -->[\s\S]*?<!-- END BIAT SHARED SIDEBAR -->', '', html)
    html = re.sub(r'<!-- BIAT SHARED SIDEBAR SCRIPT -->[\s\S]*?<!-- END BIAT SHARED SIDEBAR SCRIPT -->', '', html)
    html = re.sub(r'<!-- BIAT SIDEBAR CSS -->[\s\S]*?<!-- END BIAT SIDEBAR CSS -->', '', html)

    # Replace first aside
    html = re.sub(r'<aside[\s\S]*?</aside>', SIDEBAR, html, count=1)

    # Fix content margin for w-64 = 256px
    html = html.replace("ml-[240px]", "ml-64")
    html = html.replace("ml-[260px]", "ml-64")
    html = html.replace("ml-[280px]", "ml-64")

    # If page uses explicit left padding/margin with old sidebar, normalize
    html = html.replace("pl-[240px]", "pl-64")
    html = html.replace("pl-[260px]", "pl-64")
    html = html.replace("pl-[280px]", "pl-64")

    # Fix names
    html = html.replace("A. Mansour", "ALA")
    html = html.replace("R. Dupont", "ALA")
    html = html.replace("R. Khelifi", "ALA")
    html = html.replace("Chief Risk Manager", "Risk Officer")
    html = html.replace("Chief Risk Officer", "Risk Officer")
    html = html.replace("ADMIN", "Risk Officer")

    # Add CSS in head
    if 'id="biat-sidebar-css"' not in html:
        html = html.replace("</head>", CSS + "\n</head>")

    # Add script before body end
    if 'id="biat-shared-sidebar-script"' not in html:
        html = html.replace("</body>", SCRIPT + "\n</body>")

    path.write_text(html, encoding="utf-8")
    print("PATCHED:", file)

for page in PAGES:
    patch_page(page)

print("DONE: Standard sidebar fixed on all pages.")
