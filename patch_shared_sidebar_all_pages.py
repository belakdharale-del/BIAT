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
<aside class="fixed left-0 top-0 h-screen w-[240px] border-r border-outline-variant bg-surface-container-low flex flex-col py-stack-lg z-50">
  <div class="px-gutter mb-stack-lg">
    <h1 class="font-headline-lg text-headline-lg font-bold text-primary tracking-tight leading-tight">
      BIAT Risk<br>Monitor
    </h1>
    <p class="font-body-sm text-body-sm text-on-surface-variant opacity-70">
      Vigilant Professionalism
    </p>
  </div>

  <nav id="mainNav" class="flex-1 space-y-1 px-base">
    <a data-route="/dashboard" href="/dashboard"
       class="nav-link flex items-center gap-base px-gutter py-stack-md rounded-lg transition-colors duration-200">
      <span class="material-symbols-outlined">dashboard</span>
      <span class="font-label-md text-label-md">Global Dashboard</span>
    </a>

    <a data-route="/evolution" href="/evolution"
       class="nav-link flex items-center gap-base px-gutter py-stack-md rounded-lg transition-colors duration-200">
      <span class="material-symbols-outlined">trending_up</span>
      <span class="font-label-md text-label-md">Risk Evolution</span>
    </a>

    <a data-route="/future" href="/future"
       class="nav-link flex items-center gap-base px-gutter py-stack-md rounded-lg transition-colors duration-200">
      <span class="material-symbols-outlined">online_prediction</span>
      <span class="font-label-md text-label-md">Future Prediction</span>
    </a>

    <a data-route="/notifications" href="/notifications"
       class="nav-link flex items-center gap-base px-gutter py-stack-md rounded-lg transition-colors duration-200 relative">
      <span class="material-symbols-outlined">notifications</span>
      <span class="font-label-md text-label-md">Notifications</span>
      <span id="notifBadge" class="absolute right-4 bg-error text-on-error px-1.5 rounded text-[10px]">0</span>
    </a>

    <a data-route="/client" href="/client"
       class="nav-link flex items-center gap-base px-gutter py-stack-md rounded-lg transition-colors duration-200">
      <span class="material-symbols-outlined">group</span>
      <span class="font-label-md text-label-md">Client Profiles</span>
    </a>

    <a data-route="/performance" href="/performance"
       class="nav-link flex items-center gap-base px-gutter py-stack-md rounded-lg transition-colors duration-200">
      <span class="material-symbols-outlined">analytics</span>
      <span class="font-label-md text-label-md">Model Performance</span>
    </a>

    <a data-route="/assistant" href="/assistant"
       class="nav-link flex items-center gap-base px-gutter py-stack-md rounded-lg transition-colors duration-200">
      <span class="material-symbols-outlined">smart_toy</span>
      <span class="font-label-md text-label-md">AI Assistant</span>
    </a>
  </nav>

  <div class="px-gutter mb-stack-lg">
    <button id="criticalAlertsBtn" class="w-full bg-error-container text-on-error-container py-stack-md rounded-lg font-bold flex items-center justify-center gap-2">
      <span class="material-symbols-outlined text-sm">warning</span>
      Critical Alerts
    </button>
  </div>

  <div class="mt-auto px-base border-t border-outline-variant/30 pt-stack-md space-y-1">
    <a id="settingsBtn" href="#"
       class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 rounded-lg transition-colors duration-200">
      <span class="material-symbols-outlined">settings</span>
      <span class="font-label-md text-label-md">Settings</span>
    </a>

    <a id="supportBtn" href="#"
       class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 rounded-lg transition-colors duration-200">
      <span class="material-symbols-outlined">help</span>
      <span class="font-label-md text-label-md">Support</span>
    </a>
  </div>
</aside>
<!-- END BIAT SHARED SIDEBAR -->
'''

DYNAMIC_SCRIPT = r'''
<!-- BIAT SHARED SIDEBAR SCRIPT -->
<script id="biat-shared-sidebar-script">
document.addEventListener("DOMContentLoaded", function () {
  const currentPath = window.location.pathname.toLowerCase();

  document.querySelectorAll("#mainNav .nav-link").forEach(function(link) {
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

    link.classList.remove(
      "bg-secondary-container",
      "text-on-secondary-container",
      "font-bold",
      "text-on-surface-variant",
      "hover:text-on-surface",
      "hover:bg-surface-variant/30"
    );

    if (isActive) {
      link.classList.add("bg-secondary-container", "text-on-secondary-container", "font-bold");
    } else {
      link.classList.add("text-on-surface-variant", "hover:text-on-surface", "hover:bg-surface-variant/30");
    }
  });

  const criticalBtn = document.getElementById("criticalAlertsBtn");
  if (criticalBtn) {
    criticalBtn.addEventListener("click", function () {
      window.location.href = "/notifications?alert=CRITICAL";
    });
  }

  const settingsBtn = document.getElementById("settingsBtn");
  if (settingsBtn) {
    settingsBtn.addEventListener("click", function (e) {
      e.preventDefault();
      alert("Settings - BIAT Risk Monitor\\nUser: ALA\\nRole: Risk Officer");
    });
  }

  const supportBtn = document.getElementById("supportBtn");
  if (supportBtn) {
    supportBtn.addEventListener("click", function (e) {
      e.preventDefault();
      alert("Support - BIAT Risk Monitor");
    });
  }

  fetch("/api/future-predictions", { cache: "no-store" })
    .then(r => r.ok ? r.json() : null)
    .then(data => {
      if (!data || !data.summary) return;
      const badge = document.getElementById("notifBadge");
      if (badge) {
        const n = data.summary.critical_future_clients || data.summary.aggravation_clients || 0;
        badge.innerText = Number(n).toLocaleString("fr-FR");
      }
    })
    .catch(() => {});
});
</script>
<!-- END BIAT SHARED SIDEBAR SCRIPT -->
'''

def patch_page(file_path):
    path = Path(file_path)
    if not path.exists():
        print("MISSING:", file_path)
        return

    html = path.read_text(encoding="utf-8", errors="ignore")

    backup = path.with_name("code_backup_before_shared_sidebar.html")
    if not backup.exists():
        backup.write_text(html, encoding="utf-8")

    # Remove previous shared sidebar/script
    html = re.sub(
        r'<!-- BIAT SHARED SIDEBAR -->[\s\S]*?<!-- END BIAT SHARED SIDEBAR -->',
        '',
        html,
        flags=re.S
    )
    html = re.sub(
        r'<!-- BIAT SHARED SIDEBAR SCRIPT -->[\s\S]*?<!-- END BIAT SHARED SIDEBAR SCRIPT -->',
        '',
        html,
        flags=re.S
    )

    # Remove duplicate/broken sidebar leftovers around <!-- Main -->
    html = re.sub(
        r'<!-- Sidebar -->\s*<aside[\s\S]*?</aside>\s*</nav>[\s\S]*?</aside>\s*(<!-- Main -->)',
        SIDEBAR + r'\n\n\1',
        html,
        count=1,
        flags=re.S
    )

    # Normal case: replace first aside
    if '<!-- BIAT SHARED SIDEBAR -->' not in html:
        html = re.sub(
            r'<!-- Sidebar -->\s*<aside[\s\S]*?</aside>',
            '<!-- Sidebar -->\n' + SIDEBAR,
            html,
            count=1,
            flags=re.S
        )

    # If no <!-- Sidebar --> marker exists, replace first aside only
    if '<!-- BIAT SHARED SIDEBAR -->' not in html:
        html = re.sub(
            r'<aside[\s\S]*?</aside>',
            SIDEBAR,
            html,
            count=1,
            flags=re.S
        )

    # Fix main margin for 240px sidebar
    html = html.replace('ml-[280px]', 'ml-[240px]')
    html = html.replace('ml-[260px]', 'ml-[240px]')
    html = html.replace('w-[260px]', 'w-[240px]')

    # Fix user name everywhere
    html = html.replace("A. Mansour", "ALA")
    html = html.replace("R. Dupont", "ALA")
    html = html.replace("R. Khelifi", "ALA")
    html = html.replace("Chief Risk Manager", "Risk Officer")
    html = html.replace("Chief Risk Officer", "Risk Officer")
    html = html.replace("ADMIN", "Risk Officer")

    # Remove Last 7 Days if exists
    html = html.replace('<option value="7">Last 7 Days</option>', '')
    html = html.replace('<option value="7d">Last 7 Days</option>', '')

    # Add script before </body>
    if 'id="biat-shared-sidebar-script"' not in html:
      html = html.replace("</body>", DYNAMIC_SCRIPT + "\n</body>")

    path.write_text(html, encoding="utf-8")
    print("PATCHED:", file_path)

for page in PAGES:
    patch_page(page)

print("DONE: Shared sidebar added to all pages.")
