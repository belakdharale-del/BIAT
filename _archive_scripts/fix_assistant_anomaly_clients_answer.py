from pathlib import Path
import re

path = Path("assistant_ia_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

html = re.sub(
    r'<!-- BIAT_ASSISTANT_ANOMALY_CLIENTS_FIX -->[\s\S]*?<!-- END BIAT_ASSISTANT_ANOMALY_CLIENTS_FIX -->',
    '',
    html
)

fix = r'''
<!-- BIAT_ASSISTANT_ANOMALY_CLIENTS_FIX -->
<script>
(function () {
  let lastTopic = "";

  function hasAny(text, words) {
    text = String(text || "").toLowerCase();
    return words.some(w => text.includes(w));
  }

  function get(obj, keys, fallback = "") {
    for (const k of keys) {
      if (obj && obj[k] !== undefined && obj[k] !== null && obj[k] !== "") return obj[k];
    }
    return fallback;
  }

  function toNumber(v) {
    const x = Number(String(v ?? "").replace(",", "."));
    return Number.isFinite(x) ? x : 0;
  }

  async function getAnomalyClientsAnswer() {
    const res = await fetch("/attached_assets/anomaly_clients.json", { cache: "no-store" });
    const raw = await res.json();

    let rows = [];

    if (Array.isArray(raw)) {
      rows = raw;
    } else if (Array.isArray(raw.clients)) {
      rows = raw.clients;
    } else if (Array.isArray(raw.anomalies)) {
      rows = raw.anomalies;
    } else if (Array.isArray(raw.data)) {
      rows = raw.data;
    } else if (raw && typeof raw === "object") {
      rows = Object.entries(raw).map(([key, value]) => {
        if (value && typeof value === "object") return { cpte: key, ...value };
        return { cpte: key, value };
      });
    }

    rows = rows.filter(r => r && typeof r === "object");

    rows.sort((a, b) => {
      const sb = toNumber(get(b, ["anomaly_score", "score_anomalie", "score", "risk_score", "risk_score_percent"], 0));
      const sa = toNumber(get(a, ["anomaly_score", "score_anomalie", "score", "risk_score", "risk_score_percent"], 0));
      return sb - sa;
    });

    const top = rows.slice(0, 15);

    if (!top.length) {
      return "Je n’ai pas trouvé de clients exploitables dans anomaly_clients.json.";
    }

    let answer = `Oui. Voici les clients détectés avec comportement atypique/anomalie.\n\n`;
    answer += `Nombre total d'anomalies détectées : ${rows.length.toLocaleString("fr-FR")}\n\n`;
    answer += `Top clients anomalies :\n\n`;

    top.forEach((r, i) => {
      const cpte = get(r, ["cpte", "CPTE", "account", "client", "id"], "N/A");
      const anomalyScore = get(r, ["anomaly_score", "score_anomalie", "score"], "N/A");
      const level = get(r, ["niveau_anomalie", "alert_level", "risk_band", "niveau_actuel", "niveau"], "N/A");
      const risk = get(r, ["risk_score_percent", "score_risque_pct", "risk_score", "score_percent"], "N/A");
      const diagnostic = get(r, ["diagnostic", "reason", "explanation", "anomaly_action", "recommendation"], "Comportement inhabituel détecté.");

      answer += `${i + 1}. ${cpte}\n`;
      answer += `   - Score anomalie : ${anomalyScore}\n`;
      answer += `   - Niveau : ${level}\n`;
      answer += `   - Score risque : ${risk}\n`;
      answer += `   - Diagnostic : ${diagnostic}\n`;
      answer += `   - Fiche client : /client?cpte=${encodeURIComponent(cpte)}\n\n`;
    });

    answer += `Action recommandée : contrôler ces dossiers en priorité, car l’anomalie peut signaler un comportement atypique même si le score classique ne suffit pas.`;

    return answer;
  }

  const oldAskAssistant = window.askAssistant;

  window.askAssistant = async function (question) {
    const q = String(question || "").toLowerCase();

    const isAnomalyQuestion =
      hasAny(q, ["anomalie", "anomaly", "anomalies", "atypique", "comportement atypique"]);

    const asksWho =
      hasAny(q, ["qui", "sont", "liste", "donne", "clients", "which", "show"]);

    if (isAnomalyQuestion) {
      lastTopic = "anomalies";
    }

    if (
      (isAnomalyQuestion && asksWho) ||
      (lastTopic === "anomalies" && hasAny(q, ["qui", "sont", "lesquels", "liste", "donne", "show"]))
    ) {
      addAI(await getAnomalyClientsAnswer());
      return;
    }

    if (typeof oldAskAssistant === "function") {
      return oldAskAssistant(question);
    }

    addAI("Je n’ai pas compris la question. Essaie : Qui sont les clients qui ont des anomalies ?");
  };
})();
</script>
<!-- END BIAT_ASSISTANT_ANOMALY_CLIENTS_FIX -->
'''

html = html.replace("</body>", fix + "\n</body>")
path.write_text(html, encoding="utf-8")

print("Assistant anomaly client answer fixed.")
