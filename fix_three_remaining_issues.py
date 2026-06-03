from pathlib import Path
import re

# =========================
# 1) FIX ASSISTANT ANOMALY ANSWERS
# =========================

assistant_path = Path("assistant_ia_biat_risk_monitor/code.html")
assistant = assistant_path.read_text(encoding="utf-8", errors="ignore")
assistant_path.with_name("code_backup_before_final_anomaly_logic.html").write_text(assistant, encoding="utf-8")

assistant = re.sub(
    r'<!-- BIAT_FINAL_ANOMALY_LOGIC -->[\s\S]*?<!-- END BIAT_FINAL_ANOMALY_LOGIC -->',
    '',
    assistant
)

assistant_fix = r'''
<!-- BIAT_FINAL_ANOMALY_LOGIC -->
<script>
(function () {
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

  function num(v) {
    const x = Number(String(v ?? "").replace(",", "."));
    return Number.isFinite(x) ? x : 0;
  }

  function buildDiagnostic(r) {
    const anomaly = num(get(r, ["anomaly_score", "score_anomalie", "score"], 0));
    const risk = num(get(r, ["risk_score_percent", "score_risque_pct", "risk_score", "score_percent"], 0));
    const nbrjdep = num(get(r, ["NBRJDEP", "nbrjdep", "days_overdraft"], 0));
    const riskBrut = num(get(r, ["risk_brut", "RISK_BRUT", "exposure", "exposition"], 0));
    const level = String(get(r, ["risk_band", "niveau_actuel", "niveau", "alert_level"], "")).toLowerCase();

    let reasons = [];

    if (anomaly >= 95) {
      reasons.push("anomalie extrême : comportement très éloigné du profil normal du portefeuille");
    } else if (anomaly >= 85) {
      reasons.push("anomalie forte : comportement atypique significatif");
    } else if (anomaly >= 70) {
      reasons.push("anomalie modérée : écart notable par rapport aux clients similaires");
    } else {
      reasons.push("écart comportemental détecté par le modèle non supervisé");
    }

    if (risk >= 85 || level.includes("crit")) {
      reasons.push("score de risque critique ou proche du seuil critique");
    } else if (risk >= 65 || level.includes("elev") || level.includes("élev")) {
      reasons.push("score de risque élevé à surveiller");
    } else if (risk > 0 && risk < 20) {
      reasons.push("risque classique faible mais comportement atypique, donc contrôle recommandé");
    }

    if (nbrjdep >= 120) {
      reasons.push("nombre de jours en dépassement très élevé");
    } else if (nbrjdep >= 30) {
      reasons.push("dépassement prolongé détecté");
    }

    if (riskBrut > 0) {
      reasons.push("exposition financière associée au dossier");
    }

    return reasons.join("; ") + ".";
  }

  async function anomalyClientsAnswer() {
    const res = await fetch("/attached_assets/anomaly_clients.json", { cache: "no-store" });
    const raw = await res.json();

    let rows = [];
    if (Array.isArray(raw)) rows = raw;
    else if (Array.isArray(raw.clients)) rows = raw.clients;
    else if (Array.isArray(raw.anomalies)) rows = raw.anomalies;
    else if (Array.isArray(raw.data)) rows = raw.data;
    else if (raw && typeof raw === "object") {
      rows = Object.entries(raw).map(([key, value]) => {
        if (value && typeof value === "object") return { cpte: key, ...value };
        return { cpte: key, value };
      });
    }

    rows = rows.filter(r => r && typeof r === "object");

    rows.sort((a, b) => {
      const sb = num(get(b, ["anomaly_score", "score_anomalie", "score"], 0));
      const sa = num(get(a, ["anomaly_score", "score_anomalie", "score"], 0));
      return sb - sa;
    });

    // remove duplicated CPTE
    const seen = new Set();
    const unique = [];
    for (const r of rows) {
      const cpte = get(r, ["cpte", "CPTE", "account", "client", "id"], "");
      if (!cpte || seen.has(cpte)) continue;
      seen.add(cpte);
      unique.push(r);
    }

    const top = unique.slice(0, 15);

    if (!top.length) {
      return "Je n’ai pas trouvé de clients anomalies exploitables dans anomaly_clients.json.";
    }

    let answer = `Oui. Voici les clients détectés avec comportement atypique/anomalie.\n\n`;
    answer += `Nombre total d'anomalies détectées : ${unique.length.toLocaleString("fr-FR")}\n\n`;
    answer += `Top clients anomalies :\n\n`;

    top.forEach((r, i) => {
      const cpte = get(r, ["cpte", "CPTE", "account", "client", "id"], "N/A");
      const anomaly = get(r, ["anomaly_score", "score_anomalie", "score"], "N/A");
      const risk = get(r, ["risk_score_percent", "score_risque_pct", "risk_score", "score_percent"], "N/A");
      const nbrjdep = get(r, ["NBRJDEP", "nbrjdep", "days_overdraft"], "N/A");
      const riskBrut = get(r, ["risk_brut", "RISK_BRUT", "exposure", "exposition"], "N/A");

      answer += `${i + 1}. ${cpte}\n`;
      answer += `   - Score anomalie : ${anomaly}\n`;
      answer += `   - Score risque : ${risk}\n`;
      answer += `   - NBRJDEP : ${nbrjdep}\n`;
      answer += `   - Exposition : ${riskBrut}\n`;
      answer += `   - Diagnostic : ${buildDiagnostic(r)}\n`;
      answer += `   - Fiche client : /client?cpte=${encodeURIComponent(cpte)}\n\n`;
    });

    answer += "Action recommandée : ouvrir les fiches clients et contrôler en priorité les dossiers avec anomalie élevée + score risque critique ou dépassement prolongé.";

    return answer;
  }

  const previousAskAssistant = window.askAssistant;

  window.askAssistant = async function (question) {
    const q = String(question || "").toLowerCase();

    const anomalyIntent =
      hasAny(q, ["anomalie", "anomalies", "anomaly", "atypique", "comportement atypique"]) &&
      hasAny(q, ["qui", "sont", "liste", "clients", "donne", "show", "which"]);

    if (anomalyIntent) {
      addAI(await anomalyClientsAnswer());
      return;
    }

    if (typeof previousAskAssistant === "function") {
      return previousAskAssistant(question);
    }

    addAI("Je peux répondre sur les clients risqués, les anomalies, les prédictions futures et les fiches clients.");
  };
})();
</script>
<!-- END BIAT_FINAL_ANOMALY_LOGIC -->
'''

assistant = assistant.replace("</body>", assistant_fix + "\n</body>")
assistant_path.write_text(assistant, encoding="utf-8")


# =========================
# 2) GLOBAL SETTINGS + SUPPORT MODALS
# =========================

pages = [
    "global_dashboard_biat_risk_monitor/code.html",
    "risk_evolution_biat_risk_monitor/code.html",
    "future_prediction_biat_risk_monitor/code.html",
    "clients_notifier_biat_risk_monitor/code.html",
    "fiche_client_biat_risk_monitor/code.html",
    "performance_mod_le_biat_risk_monitor/code.html",
    "assistant_ia_biat_risk_monitor/code.html",
]

modal_fix = r'''
<!-- BIAT_SETTINGS_SUPPORT_FIX -->
<style>
  #biatModalOverlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.58);
    z-index: 999999;
    display: none;
    align-items: center;
    justify-content: center;
  }

  #biatModalBox {
    width: min(560px, 92vw);
    background: #101b33;
    border: 1px solid rgba(95,251,214,.35);
    border-radius: 16px;
    color: #d9e2ff;
    padding: 22px;
    box-shadow: 0 30px 80px rgba(0,0,0,.45);
    font-family: Inter, Arial, sans-serif;
  }

  #biatModalBox h2 {
    margin: 0 0 14px 0;
    color: #5ffbd6;
    font-size: 22px;
    font-weight: 800;
  }

  #biatModalBox p {
    color: #b9c6e4;
    line-height: 1.6;
  }

  #biatModalClose {
    margin-top: 18px;
    background: #5ffbd6;
    color: #06251f;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 800;
    cursor: pointer;
  }
</style>

<div id="biatModalOverlay">
  <div id="biatModalBox">
    <h2 id="biatModalTitle">BIAT Risk Monitor</h2>
    <p id="biatModalText"></p>
    <button id="biatModalClose">Fermer</button>
  </div>
</div>

<script>
(function () {
  function showModal(title, text) {
    let overlay = document.getElementById("biatModalOverlay");
    let titleEl = document.getElementById("biatModalTitle");
    let textEl = document.getElementById("biatModalText");

    if (!overlay || !titleEl || !textEl) {
      alert(title + "\\n\\n" + text);
      return;
    }

    titleEl.innerText = title;
    textEl.innerText = text;
    overlay.style.display = "flex";
  }

  document.addEventListener("click", function (e) {
    const close = e.target.closest("#biatModalClose");
    if (close) {
      document.getElementById("biatModalOverlay").style.display = "none";
      return;
    }

    const settings = e.target.closest("#settingsBtn, .side-btn, button, a");
    if (settings && String(settings.innerText || "").toLowerCase().includes("settings")) {
      e.preventDefault();
      showModal(
        "Settings",
        "Paramètres locaux BIAT Risk Monitor : thème sombre, navigation, synchronisation portefeuille, seuils de risque et préférences d'affichage. Cette version utilise les données locales du projet."
      );
      return;
    }

    const support = e.target.closest("#supportBtn, .side-btn, button, a");
    if (support && String(support.innerText || "").toLowerCase().includes("support")) {
      e.preventDefault();
      showModal(
        "Support",
        "Aide rapide : Dashboard pour la vue globale, Risk Evolution pour les transitions, Future Prediction pour les clients qui vont devenir critiques, Notifications pour la liste opérationnelle, Client Profiles pour les fiches individuelles, AI Assistant pour les questions métier."
      );
      return;
    }
  }, true);
})();
</script>
<!-- END BIAT_SETTINGS_SUPPORT_FIX -->
'''

for file in pages:
    p = Path(file)
    if not p.exists():
        continue

    html = p.read_text(encoding="utf-8", errors="ignore")
    p.with_name("code_backup_before_settings_support_fix.html").write_text(html, encoding="utf-8")

    html = re.sub(
        r'<!-- BIAT_SETTINGS_SUPPORT_FIX -->[\s\S]*?<!-- END BIAT_SETTINGS_SUPPORT_FIX -->',
        '',
        html
    )

    html = html.replace("</body>", modal_fix + "\n</body>")
    p.write_text(html, encoding="utf-8")


# =========================
# 3) ADD APPLY FILTERS BUTTON ON DASHBOARD
# =========================

dashboard_path = Path("global_dashboard_biat_risk_monitor/code.html")
dashboard = dashboard_path.read_text(encoding="utf-8", errors="ignore")
dashboard_path.with_name("code_backup_before_apply_button_fix.html").write_text(dashboard, encoding="utf-8")

dashboard = re.sub(
    r'<!-- BIAT_DASHBOARD_APPLY_BUTTON_FIX -->[\s\S]*?<!-- END BIAT_DASHBOARD_APPLY_BUTTON_FIX -->',
    '',
    dashboard
)

apply_fix = r'''
<!-- BIAT_DASHBOARD_APPLY_BUTTON_FIX -->
<script>
(function () {
  function findResetButton() {
    return Array.from(document.querySelectorAll("button, a")).find(el =>
      String(el.innerText || "").toLowerCase().includes("reset filters")
    );
  }

  function applyDashboardFilters() {
    const funcs = [
      "applyFilters",
      "renderDashboard",
      "renderAll",
      "updateDashboard",
      "loadDashboard",
      "filterDashboard"
    ];

    let called = false;

    funcs.forEach(name => {
      if (typeof window[name] === "function") {
        try {
          window[name]();
          called = true;
        } catch (e) {
          console.warn("Filter function failed:", name, e);
        }
      }
    });

    document.querySelectorAll("select, input").forEach(el => {
      el.dispatchEvent(new Event("change", { bubbles: true }));
      el.dispatchEvent(new Event("input", { bubbles: true }));
    });

    if (!called) {
      console.log("Apply filters clicked: no specific function found, events dispatched.");
    }
  }

  function addApplyButton() {
    if (document.getElementById("biatApplyFiltersBtn")) return;

    const reset = findResetButton();

    const btn = document.createElement("button");
    btn.id = "biatApplyFiltersBtn";
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

    btn.addEventListener("click", applyDashboardFilters);

    if (reset && reset.parentElement) {
      reset.parentElement.appendChild(btn);
    } else {
      const filterBox = Array.from(document.querySelectorAll("div, section")).find(el =>
        String(el.innerText || "").toLowerCase().includes("minimum score")
      );

      if (filterBox) {
        filterBox.appendChild(btn);
      }
    }
  }

  window.addEventListener("load", function () {
    setTimeout(addApplyButton, 500);
    setTimeout(addApplyButton, 1500);
  });
})();
</script>
<!-- END BIAT_DASHBOARD_APPLY_BUTTON_FIX -->
'''

dashboard = dashboard.replace("</body>", apply_fix + "\n</body>")
dashboard_path.write_text(dashboard, encoding="utf-8")

print("Fixed: assistant anomaly diagnostics, settings/support modals, dashboard Apply Filters button.")
