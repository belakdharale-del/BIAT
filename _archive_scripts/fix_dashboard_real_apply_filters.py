from pathlib import Path
import re

path = Path("global_dashboard_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

# Remove old fake apply button fix
html = re.sub(
    r'<!-- BIAT_DASHBOARD_APPLY_BUTTON_FIX -->[\s\S]*?<!-- END BIAT_DASHBOARD_APPLY_BUTTON_FIX -->',
    '',
    html
)

# Remove previous real fix if exists
html = re.sub(
    r'<!-- BIAT_REAL_DASHBOARD_FILTERS_FIX -->[\s\S]*?<!-- END BIAT_REAL_DASHBOARD_FILTERS_FIX -->',
    '',
    html
)

fix = r'''
<!-- BIAT_REAL_DASHBOARD_FILTERS_FIX -->
<script>
(function () {
  let dashboardRows = [];

  function txt(el) {
    return String(el?.innerText || el?.textContent || "").trim().toLowerCase();
  }

  function num(v) {
    const x = Number(String(v ?? "").replace(",", ".").replace(/[^\d.-]/g, ""));
    return Number.isFinite(x) ? x : 0;
  }

  function get(r, keys, fallback = "") {
    for (const k of keys) {
      if (r && r[k] !== undefined && r[k] !== null && r[k] !== "") return r[k];
    }
    return fallback;
  }

  function cpteOf(r) {
    return get(r, ["cpte", "CPTE", "account", "id"], "N/A");
  }

  function scoreOf(r) {
    let s = get(r, ["risk_score_percent", "score_percent", "score_risque_pct", "risk_score", "score"], 0);
    s = num(s);
    if (s <= 1) s *= 100;
    return Math.max(0, Math.min(100, s));
  }

  function bandOf(r) {
    const raw = String(get(r, ["risk_band", "alert_level", "niveau", "niveau_actuel"], "")).toLowerCase();

    if (raw.includes("crit")) return "critical";
    if (raw.includes("high") || raw.includes("élev") || raw.includes("elev") || raw.includes("warning")) return "warning";
    if (raw.includes("moy") || raw.includes("medium")) return "medium";
    if (raw.includes("faible") || raw.includes("low")) return "low";

    const s = scoreOf(r);
    if (s >= 85) return "critical";
    if (s >= 65) return "warning";
    if (s >= 40) return "medium";
    return "low";
  }

  function exposureOf(r) {
    return num(get(r, ["risk_brut", "RISK_BRUT", "exposure", "exposition", "montant_risque"], 0));
  }

  function formatInt(v) {
    return Math.round(num(v)).toLocaleString("fr-FR");
  }

  function formatMoney(v) {
    v = num(v);
    if (v >= 1000000) return (v / 1000000).toFixed(1).replace(".", ",") + "M TND";
    if (v >= 1000) return (v / 1000).toFixed(1).replace(".", ",") + "K TND";
    return formatInt(v) + " TND";
  }

  function getFilterValues() {
    const selects = Array.from(document.querySelectorAll("select"));
    const inputs = Array.from(document.querySelectorAll("input"));

    let alertValue = "all";
    let minScore = 0;

    for (const s of selects) {
      const v = String(s.value || s.options?.[s.selectedIndex]?.text || "").toLowerCase();
      const label = txt(s.parentElement);

      if (
        label.includes("alert") ||
        v.includes("critical") ||
        v.includes("warning") ||
        v.includes("all levels") ||
        v.includes("critique") ||
        v.includes("élev") ||
        v.includes("elev")
      ) {
        alertValue = v;
      }
    }

    for (const input of inputs) {
      if (input.type === "range") {
        minScore = num(input.value);
      }
    }

    return { alertValue, minScore };
  }

  function matchAlert(row, alertValue) {
    if (!alertValue || alertValue.includes("all")) return true;

    const band = bandOf(row);

    if (alertValue.includes("crit")) return band === "critical";
    if (alertValue.includes("warn") || alertValue.includes("high") || alertValue.includes("élev") || alertValue.includes("elev")) return band === "warning";
    if (alertValue.includes("moy") || alertValue.includes("medium")) return band === "medium";
    if (alertValue.includes("low") || alertValue.includes("faible")) return band === "low";

    return true;
  }

  function filteredRows() {
    const f = getFilterValues();

    return dashboardRows.filter(r => {
      const score = scoreOf(r);
      if (score < f.minScore) return false;
      if (!matchAlert(r, f.alertValue)) return false;
      return true;
    });
  }

  function setCardValue(labelWords, value) {
    const cards = Array.from(document.querySelectorAll("div, section")).filter(el => {
      const t = txt(el);
      return labelWords.every(w => t.includes(w));
    });

    const card = cards.find(el => el.querySelectorAll("div, span, p").length < 40);
    if (!card) return;

    const candidates = Array.from(card.querySelectorAll("p, div, span, h2, h3"))
      .filter(el => {
        const t = txt(el);
        return t === "—" || t === "--" || /^\d/.test(t) || t.includes("m tnd") || t.includes("%");
      });

    const target = candidates.find(el => {
      const t = txt(el);
      return t === "—" || t === "--" || /^\d/.test(t);
    });

    if (target) target.innerText = value;
  }

  function rebuildTopTable(rows) {
    const table = document.querySelector("table");
    if (!table) return;

    const tbody = table.querySelector("tbody");
    if (!tbody) return;

    const top = rows
      .slice()
      .sort((a, b) => scoreOf(b) - scoreOf(a))
      .slice(0, 12);

    tbody.innerHTML = top.map(r => {
      const cpte = cpteOf(r);
      const score = scoreOf(r);
      const band = bandOf(r);
      const exp = exposureOf(r);
      const action = get(r, ["recommended_action", "action", "recommendation"], band === "critical" ? "Intervention immédiate" : "Suivi quotidien");

      return `
        <tr>
          <td class="px-4 py-3 font-bold">${cpte}</td>
          <td class="px-4 py-3">${score.toFixed(1)}%</td>
          <td class="px-4 py-3">${band.toUpperCase()}</td>
          <td class="px-4 py-3">${formatMoney(exp)}</td>
          <td class="px-4 py-3">${action}</td>
          <td class="px-4 py-3">
            <a href="/client?cpte=${encodeURIComponent(cpte)}" style="color:#5ffbd6;font-weight:800">Open</a>
          </td>
        </tr>
      `;
    }).join("");
  }

  function applyRealDashboardFilters() {
    const rows = filteredRows();

    const total = rows.length;
    const critical = rows.filter(r => bandOf(r) === "critical").length;
    const warning = rows.filter(r => bandOf(r) === "warning").length;
    const toNotify = critical + warning;
    const avg = total ? rows.reduce((s, r) => s + scoreOf(r), 0) / total : 0;
    const exposure = rows.reduce((s, r) => s + exposureOf(r), 0);

    setCardValue(["total", "scor"], formatInt(total));
    setCardValue(["crit"], formatInt(critical));
    setCardValue(["élev"], formatInt(warning));
    setCardValue(["notify"], formatInt(toNotify));
    setCardValue(["score", "moy"], Math.round(avg) + "%");
    setCardValue(["exposition"], formatMoney(exposure));

    rebuildTopTable(rows);

    console.log("Apply Filters OK", {
      total,
      critical,
      warning,
      toNotify,
      avg,
      exposure,
      filters: getFilterValues()
    });
  }

  function addApplyButton() {
    if (document.getElementById("realApplyFiltersBtn")) return;

    const reset = Array.from(document.querySelectorAll("button, a"))
      .find(el => txt(el).includes("reset filters"));

    const btn = document.createElement("button");
    btn.id = "realApplyFiltersBtn";
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

    btn.onclick = applyRealDashboardFilters;

    if (reset && reset.parentElement) {
      reset.parentElement.appendChild(btn);
    }
  }

  async function initRealFilters() {
    try {
      const res = await fetch("/attached_assets/dashboard_clients_full.json", { cache: "no-store" });
      const raw = await res.json();

      if (Array.isArray(raw)) dashboardRows = raw;
      else if (Array.isArray(raw.clients)) dashboardRows = raw.clients;
      else if (Array.isArray(raw.data)) dashboardRows = raw.data;
      else dashboardRows = Object.values(raw || {});

      addApplyButton();

      document.querySelectorAll("select, input[type='range']").forEach(el => {
        el.addEventListener("change", applyRealDashboardFilters);
        el.addEventListener("input", function () {
          if (el.type === "range") applyRealDashboardFilters();
        });
      });

      console.log("Dashboard real filters ready:", dashboardRows.length);
    } catch (e) {
      console.error("Dashboard real filters failed", e);
    }
  }

  window.applyRealDashboardFilters = applyRealDashboardFilters;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRealFilters);
  } else {
    initRealFilters();
  }
})();
</script>
<!-- END BIAT_REAL_DASHBOARD_FILTERS_FIX -->
'''

html = html.replace("</body>", fix + "\n</body>")
path.write_text(html, encoding="utf-8")
print("Real dashboard Apply Filters fixed.")
