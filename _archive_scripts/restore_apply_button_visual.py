from pathlib import Path
import re

path = Path("global_dashboard_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

html = re.sub(
    r'<!-- BIAT_RESTORE_APPLY_BUTTON_VISUAL -->[\s\S]*?<!-- END BIAT_RESTORE_APPLY_BUTTON_VISUAL -->',
    '',
    html
)

fix = r'''
<!-- BIAT_RESTORE_APPLY_BUTTON_VISUAL -->
<script>
(function () {
  function addApplyButton() {
    if (document.getElementById("applyFiltersBtn")) return;

    const resetBtn = Array.from(document.querySelectorAll("button, a"))
      .find(el => String(el.innerText || "").toLowerCase().includes("reset filters"));

    if (!resetBtn || !resetBtn.parentElement) return;

    const btn = document.createElement("button");
    btn.id = "applyFiltersBtn";
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
      document.querySelectorAll("select, input").forEach(el => {
        el.dispatchEvent(new Event("change", { bubbles: true }));
        el.dispatchEvent(new Event("input", { bubbles: true }));
      });
      console.log("Apply Filters clicked: automatic filters refreshed.");
    });

    resetBtn.parentElement.appendChild(btn);
  }

  window.addEventListener("load", function () {
    setTimeout(addApplyButton, 300);
    setTimeout(addApplyButton, 1200);
  });
})();
</script>
<!-- END BIAT_RESTORE_APPLY_BUTTON_VISUAL -->
'''

html = html.replace("</body>", fix + "\n</body>")
path.write_text(html, encoding="utf-8")

print("Apply Filters button restored visually.")
