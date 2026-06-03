from pathlib import Path
import re

path = Path("global_dashboard_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

# Remove the injected Apply Filters scripts/buttons
html = re.sub(
    r'<!-- BIAT_DASHBOARD_APPLY_BUTTON_FIX -->[\s\S]*?<!-- END BIAT_DASHBOARD_APPLY_BUTTON_FIX -->',
    '',
    html
)

html = re.sub(
    r'<!-- BIAT_REAL_DASHBOARD_FILTERS_FIX -->[\s\S]*?<!-- END BIAT_REAL_DASHBOARD_FILTERS_FIX -->',
    '',
    html
)

# Remove any button with id created by patches if it exists as static HTML
html = re.sub(
    r'<button[^>]*id=["\'](?:realApplyFiltersBtn|biatApplyFiltersBtn)["\'][\s\S]*?</button>',
    '',
    html
)

path.write_text(html, encoding="utf-8")
print("Apply Filters button removed. Automatic filters kept from original dashboard.")
