from pathlib import Path

ROOT = Path(__file__).resolve().parent

PAGES = [
    ROOT / "global_dashboard_biat_risk_monitor" / "code.html",
    ROOT / "risk_evolution_biat_risk_monitor" / "code.html",
    ROOT / "future_prediction_biat_risk_monitor" / "code.html",
    ROOT / "clients_notifier_biat_risk_monitor" / "code.html",
    ROOT / "fiche_client_biat_risk_monitor" / "code.html",
    ROOT / "performance_mod_le_biat_risk_monitor" / "code.html",
    ROOT / "assistant_ia_biat_risk_monitor" / "code.html",
]

FUTURE_LINK = """
      <a href="/future" class="flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:bg-surface-variant/40">
        <span class="material-symbols-outlined">online_prediction</span>
        <span class="mono text-sm">Future Prediction</span>
      </a>
"""

AUTH_SCRIPT = '<script src="/attached_assets/auth.js"></script>'

REPLACEMENTS = {
    "PrÃ©dire": "Prédire",
    "prÃ©dire": "prédire",
    "prÃ©dits": "prédits",
    "PrÃ©dits": "Prédits",
    "prÃ©vue": "prévue",
    "PrÃ©vue": "Prévue",
    "Ã‰volution": "Évolution",
    "Ã©volution": "évolution",
    "Ã‰levÃ©": "Élevé",
    "Ã©levÃ©": "élevé",
    "Ã©levÃ©e": "élevée",
    "TrÃ¨s": "Très",
    "trÃ¨s": "très",
    "dÃ©jÃ": "déjà",
    "gÃ©nÃ©rÃ©s": "générés",
    "rÃ©el": "réel",
    "Ã traiter": "à traiter",
    "Ã©dits": "édits",
    "Â·": "·",
    "Â": "",
    "â†’": "→",
    "â€™": "’",
    "â€œ": "“",
    "â€": "”",
}

def backup(path: Path):
    backup_path = path.with_suffix(path.suffix + ".backup_ui_final")
    if path.exists() and not backup_path.exists():
        backup_path.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

def ensure_auth_script(html: str) -> str:
    if "/attached_assets/auth.js" in html:
        return html

    if "</body>" in html:
        return html.replace("</body>", f"  {AUTH_SCRIPT}\n</body>")

    return html + "\n" + AUTH_SCRIPT + "\n"

def fix_encoding(html: str) -> str:
    for bad, good in REPLACEMENTS.items():
        html = html.replace(bad, good)
    return html

def ensure_future_link(html: str) -> str:
    if 'href="/future"' in html or "data-route=\"/future\"" in html:
        return html

    if "</nav>" in html:
        return html.replace("</nav>", FUTURE_LINK + "\n    </nav>", 1)

    return html

def fix_critical_alerts(html: str) -> str:
    html = html.replace('href="/notifications?alert=CRITICAL?alert=CRITICAL"', 'href="/notifications?alert=CRITICAL"')
    html = html.replace('href="/notifications"', 'href="/notifications?alert=CRITICAL"', 1)
    html = html.replace("window.location.href='/notifications'", "window.location.href='/notifications?alert=CRITICAL'")
    html = html.replace('window.location.href="/notifications"', 'window.location.href="/notifications?alert=CRITICAL"')
    return html

def patch_auth_js():
    auth_path = ROOT / "attached_assets" / "auth.js"
    if not auth_path.exists():
        print("auth.js not found")
        return

    backup(auth_path)
    js = auth_path.read_text(encoding="utf-8", errors="ignore")

    force_user = """
// Force clean local user display
try {
  localStorage.setItem("biat_auth", "true");
  const currentUser = localStorage.getItem("biat_user");
  if (!currentUser || ["A. Mansour", "D. Ben Salem", "R. Khelifi", "R. Dupont"].includes(currentUser)) {
    localStorage.setItem("biat_user", "ALA");
  }
  localStorage.setItem("biat_role", "Risk Officer");
} catch (e) {}
"""

    if "Force clean local user display" not in js:
        js = force_user + "\n" + js

    js = js.replace(
        'document.querySelectorAll("aside div, aside button, nav div").forEach((el) => {',
        'document.querySelectorAll("aside a, aside button, aside div, nav a, nav div").forEach((el) => {'
    )

    auth_path.write_text(js, encoding="utf-8")
    print("patched auth.js")

def patch_pages():
    for path in PAGES:
        if not path.exists():
            print("missing:", path)
            continue

        backup(path)
        html = path.read_text(encoding="utf-8", errors="ignore")

        html = fix_encoding(html)
        html = ensure_auth_script(html)

        if path.name == "code.html" and (
            "global_dashboard_biat_risk_monitor" in str(path)
            or "risk_evolution_biat_risk_monitor" in str(path)
        ):
            html = ensure_future_link(html)

        if "future_prediction_biat_risk_monitor" in str(path):
            html = fix_encoding(html)

        path.write_text(html, encoding="utf-8")
        print("patched:", path)

if __name__ == "__main__":
    patch_auth_js()
    patch_pages()
    print("UI patch finished.")