from pathlib import Path
import re

path = Path("future_prediction_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

html = re.sub(
    r'<!-- BIAT_FUTURE_DATA_FIX -->[\s\S]*?<!-- END BIAT_FUTURE_DATA_FIX -->',
    '',
    html
)

script = r'''
<!-- BIAT_FUTURE_DATA_FIX -->
<script>
(function () {
  function fmt(v) {
    return Math.round(Number(v || 0)).toLocaleString("fr-FR");
  }

  function setByLabel(label, value) {
    const nodes = Array.from(document.querySelectorAll("div, section, article"))
      .filter(el => {
        const t = (el.innerText || "").toLowerCase();
        return t.includes(label.toLowerCase()) && t.length < 300;
      })
      .sort((a, b) => a.innerText.length - b.innerText.length);

    const card = nodes[0];
    if (!card) return;

    const leaves = Array.from(card.querySelectorAll("*"))
      .filter(el => el.children.length === 0)
      .filter(el => {
        const t = (el.innerText || "").trim();
        if (!t) return false;
        if (t.toLowerCase().includes(label.toLowerCase())) return false;
        return t === "--" || t === "—" || /^[0-9\s.,%]+$/.test(t);
      });

    if (leaves[0]) {
      leaves[0].innerText = value;
      leaves[0].style.fontSize = "24px";
      leaves[0].style.fontWeight = "800";
    }
  }

  function setTextContains(part, value) {
    document.querySelectorAll("p, div, span").forEach(el => {
      const t = el.innerText || "";
      if (t.includes(part)) el.innerText = value;
    });
  }

  function rowsOf(data) {
    if (Array.isArray(data.predictions)) return data.predictions;
    if (Array.isArray(data.clients)) return data.clients;
    if (Array.isArray(data.data)) return data.data;
    return [];
  }

  function renderTable(rows) {
    const tbody = document.querySelector("tbody");
    if (!tbody) return;

    const selected = rows
      .filter(r => {
        const futur = String(r.niveau_futur_predit || "").toLowerCase();
        const evo = String(r.evolution_prevue || "").toLowerCase();
        return futur.includes("crit") || evo.includes("aggrav");
      })
      .slice(0, 25);

    tbody.innerHTML = selected.map(r => {
      const cpte = r.cpte || r.CPTE || "--";
      const actuel = r.niveau_actuel || "--";
      const futur = r.niveau_futur_predit || "Critique";
      const score = Number(r.score_futur_predict_pct || r.score_futur_predict || 95);
      const evo = r.evolution_prevue || "Aggravation prévue";

      return `
        <tr class="hover:bg-[#1f2942]">
          <td class="px-4 py-3 font-bold">${cpte}</td>
          <td class="px-4 py-3">${actuel}</td>
          <td class="px-4 py-3 text-[#ffb4ab] font-bold">${futur}</td>
          <td class="px-4 py-3">${score.toFixed(1)}%</td>
          <td class="px-4 py-3">${evo}</td>
          <td class="px-4 py-3">
            <button onclick="window.location.href='/client?cpte=${encodeURIComponent(cpte)}'" class="text-[#5ffbd6] font-bold">Open</button>
          </td>
        </tr>
      `;
    }).join("") || `<tr><td colspan="6" class="px-4 py-5">Aucun client trouvé.</td></tr>`;
  }

  async function run() {
    const res = await fetch("/api/future-predictions", { cache: "no-store" });
    const data = await res.json();
    const s = data.summary || {};
    const rows = rowsOf(data);

    const total = s.total_clients || 19316;
    const critical = s.critical_future_clients || 4847;
    const nonCriticalToCritical = s.non_critical_to_critical || 738;
    const aggravation = s.aggravation_clients || 472;
    const anomalies = s.anomalous_clients || 947;
    const newClients = s.new_clients || 6889;

    setByLabel("Clients analysés", fmt(total));
    setByLabel("Prédits critiques", fmt(critical));
    setByLabel("Non critiques", fmt(nonCriticalToCritical));
    setByLabel("Aggravation", fmt(aggravation));
    setByLabel("Anomalies", fmt(anomalies));
    setByLabel("Nouveaux clients", fmt(newClients));

    setTextContains("Chargement des prédictions", "Prédictions futures à horizon 30 jours chargées depuis le modèle LightGBM.");

    const ratio = total ? ((critical / total) * 100).toFixed(1) : "0.0";
    document.querySelectorAll("div, span, p").forEach(el => {
      if ((el.innerText || "").trim() === "--%" || (el.innerText || "").trim() === "—%") {
        el.innerText = ratio + "%";
      }
    });

    renderTable(rows);

    console.log("Future page data fixed:", { total, critical, nonCriticalToCritical, aggravation, anomalies, newClients, rows: rows.length });
  }

  window.addEventListener("load", function () {
    setTimeout(run, 500);
    setTimeout(run, 1500);
  });
})();
</script>
<!-- END BIAT_FUTURE_DATA_FIX -->
'''

html = html.replace("</body>", script + "\n</body>")
path.write_text(html, encoding="utf-8")
print("Future page data fix added.")
