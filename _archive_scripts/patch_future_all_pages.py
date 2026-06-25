from pathlib import Path
import re

pages = [
    "risk_evolution_biat_risk_monitor/code.html",
    "clients_notifier_biat_risk_monitor/code.html",
    "fiche_client_biat_risk_monitor/code.html",
    "performance_mod_le_biat_risk_monitor/code.html",
    "assistant_ia_biat_risk_monitor/code.html",
]

future_link_simple = '''
        <a class="nav-link" href="/future">
          <span class="material-symbols-outlined">online_prediction</span>
          <span class="mono text-sm">Future Prediction</span>
        </a>
'''

future_link_tailwind = '''
    <a href="/future" class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200">
      <span class="material-symbols-outlined">online_prediction</span>
      <span class="font-label-md text-label-md">Future Prediction</span>
    </a>
'''

for file in pages:
    path = Path(file)
    if not path.exists():
        print("missing", file)
        continue

    backup = path.with_suffix(".backup_before_future_nav.html")
    if not backup.exists():
        backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

    html = path.read_text(encoding="utf-8", errors="ignore")

    # remove broken duplicate old auto nav patches if present
    html = re.sub(
        r'\s*<!-- BIAT_AUTO_NAV_PATCH -->\s*<script>.*?</script>',
        '',
        html,
        flags=re.S
    )

    # Replace hardcoded names
    html = html.replace("A. Mansour", "ALA")
    html = html.replace("R. Dupont", "ALA")
    html = html.replace("R. Khelifi", "ALA")
    html = html.replace("Chief Risk Manager", "Risk Officer")
    html = html.replace("ADMIN", "Risk Officer")

    # Add Future Prediction only if missing
    if 'href="/future"' not in html and "Future Prediction" not in html:
        if 'class="nav-link' in html:
            # insert before Notifications if possible
            html = re.sub(
                r'(\s*<a class="nav-link[^"]*" href="/notifications"[\s\S]*?</a>)',
                future_link_simple + r'\1',
                html,
                count=1
            )
        elif "</nav>" in html:
            html = html.replace("</nav>", future_link_tailwind + "\n  </nav>", 1)

    # Fix old href="#" links by label
    routes = {
        "Global Dashboard": "/dashboard",
        "Risk Evolution": "/evolution",
        "Future Prediction": "/future",
        "Notifications": "/notifications",
        "Client Profiles": "/client",
        "Model Performance": "/performance",
        "AI Assistant": "/assistant",
    }

    # Add one safe final script to force navigation
    nav_script = '''
<script>
document.addEventListener("DOMContentLoaded", function () {
  const routes = {
    "Global Dashboard": "/dashboard",
    "Risk Evolution": "/evolution",
    "Future Prediction": "/future",
    "Notifications": "/notifications",
    "Client Profiles": "/client",
    "Model Performance": "/performance",
    "AI Assistant": "/assistant"
  };

  document.querySelectorAll("aside a, aside div, aside button").forEach(function(el) {
    const text = (el.innerText || "").trim();

    Object.entries(routes).forEach(function(pair) {
      const label = pair[0];
      const url = pair[1];

      if (text.includes(label)) {
        el.style.cursor = "pointer";

        if (el.tagName === "A") {
          el.setAttribute("href", url);
        } else {
          el.onclick = function () {
            window.location.href = url;
          };
        }
      }
    });
  });

  document.querySelectorAll("button, a, div").forEach(function(el) {
    const text = (el.innerText || "").trim();

    if (text.includes("Critical Alerts")) {
      el.style.cursor = "pointer";
      el.onclick = function () {
        window.location.href = "/notifications?alert=CRITICAL";
      };
    }
  });
});
</script>
'''

    if "const routes = {" not in html or "Future Prediction" not in html.split("const routes = {")[-1]:
        html = html.replace("</body>", nav_script + "\n</body>")

    # Ensure auth.js
    if "/attached_assets/auth.js" not in html:
        html = html.replace("</body>", '<script src="/attached_assets/auth.js"></script>\n</body>')

    path.write_text(html, encoding="utf-8")
    print("patched", file)

print("Future Prediction navigation patched on all pages.")
