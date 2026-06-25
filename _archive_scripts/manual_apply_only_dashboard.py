from pathlib import Path
import re

path = Path("global_dashboard_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

# Remove previous apply/auto patches
for marker in [
    "BIAT_RESTORE_APPLY_BUTTON_VISUAL",
    "BIAT_REAL_DASHBOARD_FILTERS_FIX",
    "BIAT_DASHBOARD_APPLY_BUTTON_FIX",
    "BIAT_MANUAL_APPLY_ONLY_FIX"
]:
    html = re.sub(
        rf'<!-- {marker} -->[\s\S]*?<!-- END {marker} -->',
        '',
        html
    )

fix = r'''
<!-- BIAT_MANUAL_APPLY_ONLY_FIX -->
<script>
(function () {
  window.__BIAT_ALLOW_MANUAL_APPLY__ = false;

  function isDashboardFilterElement(el) {
    if (!el) return false;

    const tag = String(el.tagName || "").toLowerCase();
    const type = String(el.type || "").toLowerCase();

    const isSelect = tag === "select";
    const isRange = tag === "input" && type === "range";

    if (!isSelect && !isRange) return false;

    const text = String(document.body.innerText || "").toLowerCase();
    return text.includes("minimum score") || text.includes("alert level") || text.includes("period");
  }

  // Stop automatic filtering when user changes select/range
  document.addEventListener("change", function (e) {
    if (isDashboardFilterElement(e.target) && !window.__BIAT_ALLOW_MANUAL_APPLY__) {
      e.stopImmediatePropagation();
    }
  }, true);

  document.addEventListener("input", function (e) {
    if (isDashboardFilterElement(e.target) && !window.__BIAT_ALLOW_MANUAL_APPLY__) {
      e.stopImmediatePropagation();
    }
  }, true);

  function findResetButton() {
    return Array.from(document.querySelectorAll("button, a")).find(el =>
      String(el.innerText || "").toLowerCase().includes("reset filters")
    );
  }

  function addApplyButton() {
    if (document.getElementById("manualApplyFiltersBtn")) return;

    const resetBtn = findResetButton();
    if (!resetBtn || !resetBtn.parentElement) return;

    const btn = document.createElement("button");
    btn.id = "manualApplyFiltersBtn";
    btn.type = "button";
    btn.innerText = "Apply Filters";
    btn.style.background = "#5ffbd6";
    btn.style.color = "#06251f";
    btn.style.border = "0";
    btn.style.borderRadius = "10px";
    btn.style.padding = "11px 22px";
    btn.style.fontWeight = "800";
    btn.style.cursor = "pointer";
    btn.style.marginLeft = "12px";

    btn.addEventListener("click", function () {
      window.__BIAT_ALLOW_MANUAL_APPLY__ = true;

      document.querySelectorAll("select, input[type='range']").forEach(el => {
        el.dispatchEvent(new Event("change", { bubbles: true }));
        el.dispatchEvent(new Event("input", { bubbles: true }));
      });

      setTimeout(() => {
        window.__BIAT_ALLOW_MANUAL_APPLY__ = false;
      }, 300);

      console.log("Manual Apply Filters executed.");
    });

    resetBtn.parentElement.appendChild(btn);
  }

  window.addEventListener("load", function () {
    setTimeout(addApplyButton, 300);
    setTimeout(addApplyButton, 1000);
    setTimeout(addApplyButton, 2000);
  });
})();
</script>
<!-- END BIAT_MANUAL_APPLY_ONLY_FIX -->
'''

html = html.replace("</body>", fix + "\n</body>")
path.write_text(html, encoding="utf-8")

print("Dashboard manual Apply Filters mode activated.")
