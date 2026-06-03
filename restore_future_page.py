from pathlib import Path
import re

path = Path("future_prediction_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

html = re.sub(
    r'<!-- BIAT_FUTURE_DATA_FIX -->[\s\S]*?<!-- END BIAT_FUTURE_DATA_FIX -->',
    '',
    html
)

path.write_text(html, encoding="utf-8")
print("Future page restored.")
