# patch_future_navigation.py
# Add the Future Prediction link to all BIAT Risk Monitor HTML sidebars.
# Usage:
#   python patch_future_navigation.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PAGE_DIRS = [
    "global_dashboard_biat_risk_monitor",
    "risk_evolution_biat_risk_monitor",
    "clients_notifier_biat_risk_monitor",
    "fiche_client_biat_risk_monitor",
    "performance_mod_le_biat_risk_monitor",
    "assistant_ia_biat_risk_monitor",
    "home_biat_risk_monitor",
]

FUTURE_LINK = """
      <a href="/future" class="flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:bg-surface-variant/40">
        <span class="material-symbols-outlined">online_prediction</span><span class="mono text-sm">Future Prediction</span>
      </a>"""

def patch_file(path: Path):
    if not path.exists():
        print(f"SKIP missing: {path}")
        return

    html = path.read_text(encoding="utf-8")

    if 'href="/future"' in html or "href='/future'" in html:
        print(f"OK already patched: {path}")
        return

    markers = [
        '<span class="mono text-sm">Risk Evolution</span>',
        "<span class='mono text-sm'>Risk Evolution</span>",
        "Risk Evolution",
    ]

    insert_pos = -1
    for marker in markers:
        pos = html.find(marker)
        if pos != -1:
            close = html.find("</a>", pos)
            if close != -1:
                insert_pos = close + len("</a>")
                break

    if insert_pos == -1:
        pos = html.find('href="/notifications"')
        if pos == -1:
            pos = html.find("href='/notifications'")
        if pos != -1:
            insert_pos = html.rfind("<a", 0, pos)

    if insert_pos == -1:
        print(f"WARN could not find sidebar position: {path}")
        return

    html = html[:insert_pos] + "\n" + FUTURE_LINK + html[insert_pos:]
    path.write_text(html, encoding="utf-8")
    print(f"PATCHED: {path}")

def main():
    for folder in PAGE_DIRS:
        patch_file(BASE_DIR / folder / "code.html")

if __name__ == "__main__":
    main()
