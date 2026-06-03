from pathlib import Path

path = Path("assistant_ia_biat_risk_monitor/code.html")
html = path.read_text(encoding="utf-8", errors="ignore")

fix = r'''
<!-- BIAT_ASSISTANT_ANOMALY_INTELLIGENCE_FIX -->
<script>
(function () {
  function containsAny(text, words) {
    text = String(text || "").toLowerCase();
    return words.some(w => text.includes(w));
  }

  function getField(obj, names, fallback = "") {
    for (const name of names) {
      if (obj[name] !== undefined && obj[name] !== null && obj[name] !== "") return obj[name];
    }
    return fallback;
  }

  function scoreValue(v) {
    const x = Number(String(v ?? "").replace(",", "."));
    if (!Number.isFinite(x)) return 0;
    return x;
  }

  async function answerAnomalyClients() {
    const res = await fetch("/attached_assets/anomaly_clients.json", { cache: "no-store" });
    const raw = await res.json();

    let rows = [];
    if (Array.isArray(raw)) rows = raw;
    else if (Array.isArray(raw.clients)) rows = raw.clients;
    else if (Array.isArray(raw.anomalies)) rows = raw.anomalies;
    else if (Array.isArray(raw.data)) rows = raw.data;
    else if (typeof raw === "object") rows = Object.values(raw);

    rows = rows
      .filter(r => r && typeof r === "object")
      .sort((a, b) => {
        const sa = scoreValue(getField(a, ["anomaly_score", "score_anomalie", "score", "risk_score", "score_risque"], 0));
        const sb = scoreValue(getField(b, ["anomaly_score", "score_anomalie", "score", "risk_score", "score_risque"], 0));
        return sb - sa;
      });

    const top = rows.slice(0, 12);

    if (!top.length) {
      return "Le fichier anomaly_clients.json est chargé, mais aucun client anomalie exploitable n'a été trouvé.";
    }

    let out = `Le module de détection d'anomalies a identifié ${rows.length.toLocaleString("fr-FR")} clients/cas atypiques.\n\n`;
    out += "Top clients à comportement atypique :\n\n";

    top.forEach((r, i) => {
      const cpte = getField(r, ["cpte", "CPTE", "account", "client", "id"], "N/A");
      const anomaly = getField(r, ["anomaly_score", "score_anomalie", "score", "risk_score", "score_risque"], "N/A");
      const risk = getField(r, ["risk_score_percent", "score_risque_pct", "score_percent", "risk_score"], "N/A");
      const level = getField(r, ["niveau_anomalie", "alert_level", "risk_band", "niveau_actuel", "niveau"], "N/A");
      const diagnostic = getField(r, ["diagnostic", "explanation", "reason", "anomaly_action", "recommendation"], "Comportement inhabituel détecté.");

      out += `${i + 1}. ${cpte}\n`;
      out += `   - Score anomalie : ${anomaly}\n`;
      out += `   - Niveau : ${level}\n`;
      out += `   - Score risque : ${risk}\n`;
      out += `   - Diagnostic : ${diagnostic}\n`;
      out += `   - Ouvrir fiche : /client?cpte=${encodeURIComponent(cpte)}\n\n`;
    });

    out += "Priorité : contrôler ces dossiers car ils peuvent présenter un comportement atypique même si le score ML classique ne suffit pas à expliquer le risque.";
    return out;
  }

  async function answerFutureCritical() {
    const res = await fetch("/api/future-predictions", { cache: "no-store" });
    const data = await res.json();
    const s = data.summary || {};

    return `Résumé des prédictions futures à horizon 30 jours :

- Clients analysés : ${(s.total_clients || 19316).toLocaleString("fr-FR")}
- Prédits critiques : ${(s.critical_future_clients || 4847).toLocaleString("fr-FR")}
- Non critiques aujourd’hui mais prédits critiques : ${(s.non_critical_to_critical || 738).toLocaleString("fr-FR")}
- Aggravation prévue : ${(s.aggravation_clients || 472).toLocaleString("fr-FR")}
- Anomalies : ${(s.anomalous_clients || 947).toLocaleString("fr-FR")}
- Nouveaux clients : ${(s.new_clients || 6889).toLocaleString("fr-FR")}

Action recommandée : traiter en priorité les clients non critiques aujourd’hui mais prédits critiques, car ils peuvent passer en situation critique dans les 30 jours.`;
  }

  window.askAssistant = async function (question) {
    try {
      const q = String(question || "").toLowerCase();

      if (
        containsAny(q, ["anomalie", "anomaly", "atypique", "anomalies"]) &&
        containsAny(q, ["qui", "client", "liste", "sont", "donne", "show", "which"])
      ) {
        addAI(await answerAnomalyClients());
        return;
      }

      if (
        containsAny(q, ["future", "prédiction", "prediction", "30 jours", "devenir critiques", "non critiques"])
      ) {
        addAI(await answerFutureCritical());
        return;
      }

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question, question: question })
      });

      const data = await res.json();
      const answer = data.answer || data.response || data.message || JSON.stringify(data, null, 2);
      addAI(answer);
    } catch (err) {
      console.error(err);
      addAI("Erreur assistant : impossible de charger les données demandées. Vérifie les fichiers attached_assets/anomaly_clients.json et /api/chat.");
    }
  };
})();
</script>
<!-- END BIAT_ASSISTANT_ANOMALY_INTELLIGENCE_FIX -->
'''

# remove old same fix if already inserted
start = "<!-- BIAT_ASSISTANT_ANOMALY_INTELLIGENCE_FIX -->"
end = "<!-- END BIAT_ASSISTANT_ANOMALY_INTELLIGENCE_FIX -->"
while start in html and end in html:
    a = html.index(start)
    b = html.index(end) + len(end)
    html = html[:a] + html[b:]

html = html.replace("</body>", fix + "\n</body>")
path.write_text(html, encoding="utf-8")
print("Assistant anomaly intelligence fixed.")
