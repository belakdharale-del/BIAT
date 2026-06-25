from pathlib import Path
import re

path = Path("global_dashboard_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

# Remove old duplicated nav patches
html = re.sub(
    r'\s*<!-- BIAT_AUTO_NAV_PATCH -->\s*<script>.*?</script>',
    '',
    html,
    flags=re.S
)

# Clean sidebar
sidebar = r'''
<aside class="fixed left-0 top-0 h-screen w-[280px] border-r border-outline-variant bg-surface-container-low flex flex-col py-stack-lg z-50">
  <div class="px-gutter mb-stack-lg">
    <h1 class="font-headline-lg text-headline-lg font-bold text-primary tracking-tight">BIAT Risk Monitor</h1>
    <p class="font-body-sm text-body-sm text-on-surface-variant opacity-70">Vigilant Professionalism</p>
  </div>

  <nav class="flex-1 space-y-1 px-base">
    <a href="/dashboard" class="flex items-center gap-base px-gutter py-stack-md bg-secondary-container text-on-secondary-container rounded-lg font-bold scale-[0.98] transition-transform">
      <span class="material-symbols-outlined">dashboard</span>
      <span class="font-label-md text-label-md">Global Dashboard</span>
    </a>

    <a href="/evolution" class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200">
      <span class="material-symbols-outlined">trending_up</span>
      <span class="font-label-md text-label-md">Risk Evolution</span>
    </a>

    <a href="/future" class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200">
      <span class="material-symbols-outlined">online_prediction</span>
      <span class="font-label-md text-label-md">Future Prediction</span>
    </a>

    <a href="/notifications" class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200 relative">
      <span class="material-symbols-outlined">notifications</span>
      <span class="font-label-md text-label-md">Notifications</span>
      <span class="absolute right-4 bg-error text-on-error px-1.5 rounded text-[10px]">12</span>
    </a>

    <a href="/client" class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200">
      <span class="material-symbols-outlined">group</span>
      <span class="font-label-md text-label-md">Client Profiles</span>
    </a>

    <a href="/performance" class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200">
      <span class="material-symbols-outlined">analytics</span>
      <span class="font-label-md text-label-md">Model Performance</span>
    </a>

    <a href="/assistant" class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200">
      <span class="material-symbols-outlined">smart_toy</span>
      <span class="font-label-md text-label-md">AI Assistant</span>
    </a>
  </nav>

  <div class="px-gutter mb-stack-lg">
    <button onclick="window.location.href='/notifications?alert=CRITICAL'" class="w-full bg-error-container text-on-error-container py-stack-md rounded-lg font-bold flex items-center justify-center gap-2">
      <span class="material-symbols-outlined text-sm">warning</span>
      Critical Alerts
    </button>
  </div>

  <div class="mt-auto px-base border-t border-outline-variant/30 pt-stack-md space-y-1">
    <button id="settingsBtn" class="w-full flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200">
      <span class="material-symbols-outlined">settings</span>
      <span class="font-label-md text-label-md">Settings</span>
    </button>

    <button id="supportBtn" class="w-full flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200">
      <span class="material-symbols-outlined">help</span>
      <span class="font-label-md text-label-md">Support</span>
    </button>
  </div>
</aside>
'''

# Replace complete aside
html = re.sub(
    r'<aside\b[\s\S]*?</aside>',
    sidebar,
    html,
    count=1
)

# Clean header
header = r'''
<header class="flex justify-between items-center h-16 px-container-padding ml-[280px] bg-surface-dim/80 backdrop-blur-xl border-b border-outline-variant sticky top-0 z-40">
  <div class="flex items-center gap-gutter flex-1 max-w-xl">
    <div class="relative w-full group">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm">search</span>
      <input class="w-full bg-surface-container-lowest border-none rounded-lg pl-10 pr-4 py-2 font-body-sm text-on-surface placeholder:text-on-surface-variant/50 focus:ring-2 focus:ring-primary-container"
             placeholder="Search risky CPTE, clients or alerts..."
             type="text"/>
    </div>
  </div>

  <div class="flex items-center gap-gutter">
    <button onclick="window.location.href='/assistant'" class="bg-primary text-on-primary px-gutter py-2 rounded-lg font-bold text-label-md hover:bg-primary-container transition-colors">
      Quick Action
    </button>

    <button onclick="window.location.href='/notifications'" class="text-on-surface-variant hover:text-primary transition-colors">
      <span class="material-symbols-outlined">notifications</span>
    </button>

    <div class="flex items-center gap-4 border-l border-outline-variant/30 pl-4">
      <div class="w-8 h-8 rounded-full border border-primary/20 bg-surface-container-high"></div>
      <div class="hidden lg:block text-left">
        <p class="font-label-md text-primary leading-none">ALA</p>
        <p class="text-[10px] text-on-surface-variant">Risk Officer</p>
      </div>
    </div>
  </div>
</header>
'''

# Replace complete header
html = re.sub(
    r'<header\b[\s\S]*?</header>',
    header,
    html,
    count=1
)

# Add modal script for settings/support
modal_script = r'''
<script>
document.addEventListener("DOMContentLoaded", function () {
  const settings = document.getElementById("settingsBtn");
  const support = document.getElementById("supportBtn");

  if (settings) {
    settings.onclick = function () {
      alert("Settings - BIAT Risk Monitor\nUser: ALA\nRole: Risk Officer\nMode: Localhost");
    };
  }

  if (support) {
    support.onclick = function () {
      alert("Support - BIAT Risk Monitor\nPages: Dashboard, Evolution, Future, Notifications, Client, Performance, Assistant.");
    };
  }
});
</script>
'''

if "Settings - BIAT Risk Monitor" not in html:
    html = html.replace("</body>", modal_script + "\n</body>")

# Ensure auth.js
if "/attached_assets/auth.js" not in html:
    html = html.replace("</body>", '<script src="/attached_assets/auth.js"></script>\n</body>')

path.write_text(html, encoding="utf-8")
print("STRONG dashboard UI patch done.")
