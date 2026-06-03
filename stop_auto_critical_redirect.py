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

for file in pages:
    p = Path(file)
    if not p.exists():
        continue

    html = p.read_text(encoding="utf-8", errors="ignore")
    p.with_name("code_backup_before_stop_auto_critical_redirect.html").write_text(html, encoding="utf-8")

    # Remove inline automatic redirect to critical notifications
    html = re.sub(
        r'onclick=["\']\s*window\.location\.href\s*=\s*["\']/notifications\?alert=CRITICAL["\']\s*["\']',
        '',
        html
    )

    html = re.sub(
        r'onclick=["\']\s*window\.location\.href\s*=\s*["\']/notifications["\']\s*["\']',
        '',
        html
    )

    # Remove any script line that forces critical alerts navigation
    html = re.sub(
        r'window\.location\.href\s*=\s*["\']/notifications\?alert=CRITICAL["\'];?',
        '',
        html
    )

    html = re.sub(
        r'location\.href\s*=\s*["\']/notifications\?alert=CRITICAL["\'];?',
        '',
        html
    )

    html = re.sub(
        r'location\.assign\(["\']/notifications\?alert=CRITICAL["\']\);?',
        '',
        html
    )

    # Make critical button safe: only visual button, no automatic page change
    html = re.sub(
        r'<button([^>]*)class="([^"]*critical[^"]*)"([^>]*)>',
        r'<button\1class="\2"\3 type="button">',
        html,
        flags=re.IGNORECASE
    )

    p.write_text(html, encoding="utf-8")
    print("Cleaned critical redirect:", file)

print("Done. Automatic Critical Alerts redirect removed.")
