from pathlib import Path
import re

path = Path("global_dashboard_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

# 1) Remove duplicated old navigation patches
html = re.sub(
    r'\s*<!-- BIAT_AUTO_NAV_PATCH -->\s*<script>.*?</script>',
    '',
    html,
    flags=re.S
)

# 2) Replace hardcoded user name/role
html = html.replace("A. Mansour", "ALA")
html = html.replace("Chief Risk Manager", "Risk Officer")

# 3) Add Future Prediction link if missing
future_link = '''
<a class="flex items-center gap-base px-gutter py-stack-md text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/30 transition-colors duration-200" href="/future">
<span class="material-symbols-outlined" data-icon="online_prediction">online_prediction</span>
<span class="font-label-md text-label-md">Future Prediction</span>
</a>
'''

if 'href="/future"' not in html and 'Future Prediction' not in html:
    # insert after Risk Evolution item
    pattern = r'(<a[^>]*href="#"[^>]*>.*?<span[^>]*>Risk Evolution</span>\s*</a>)'
    html = re.sub(pattern, r'\1\n' + future_link, html, count=1, flags=re.S)

# 4) Ensure auth.js is loaded
if "/attached_assets/auth.js" not in html:
    html = html.replace("</body>", '  <script src="/attached_assets/auth.js"></script>\n</body>')

# 5) Add one clean final navigation script
clean_nav = r'''
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

  const currentPath = window.location.pathname;

  document.querySelectorAll("aside a").forEach((link) => {
    const text = (link.innerText || "").trim();

    Object.entries(routes).forEach(([label, url]) => {
      if (text.includes(label)) {
        link.setAttribute("href", url);

        link.classList.remove(
          "bg-secondary-container",
          "text-on-secondary-container",
          "font-bold",
          "scale-[0.98]"
        );

        link.classList.add(
          "text-on-surface-variant",
          "hover:text-on-surface",
          "hover:bg-surface-variant/30"
        );

        if (currentPath === url) {
          link.classList.remove(
            "text-on-surface-variant",
            "hover:text-on-surface",
            "hover:bg-surface-variant/30"
          );

          link.classList.add(
            "bg-secondary-container",
            "text-on-secondary-container",
            "rounded-lg",
            "font-bold",
            "scale-[0.98]"
          );
        }
      }
    });
  });

  document.querySelectorAll("button, a").forEach((el) => {
    const text = (el.innerText || "").trim();

    if (text.includes("Critical Alerts")) {
      el.style.cursor = "pointer";
      el.onclick = function () {
        window.location.href = "/notifications?alert=CRITICAL";
      };
    }

    if (text.includes("Quick Action")) {
      el.style.cursor = "pointer";
      el.onclick = function () {
        window.location.href = "/assistant";
      };
    }
  });
});
</script>
'''

html = html.replace("</body>", clean_nav + "\n</body>")

path.write_text(html, encoding="utf-8")
print("Dashboard patched successfully.")
