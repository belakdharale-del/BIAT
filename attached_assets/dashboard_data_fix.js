(function () {
  let rows = [];

  function n(v) {
    if (v === null || v === undefined) return 0;
    const x = Number(String(v).replace(",", ".").replace(/[^\d.-]/g, ""));
    return Number.isFinite(x) ? x : 0;
  }

  function get(row, keys, fallback = "") {
    for (const k of keys) {
      if (row && row[k] !== undefined && row[k] !== null && row[k] !== "") {
        return row[k];
      }
    }
    return fallback;
  }

  function riskScore(row) {
    let s = n(get(row, [
      "risk_score",
      "score_risque",
      "score",
      "SCORE",
      "score_pct",
      "risk_score_percent",
      "probabilite",
      "probability"
    ], 0));

    if (s <= 1) s = s * 100;
    return Math.max(0, Math.min(100, s));
  }

  function riskLevel(row) {
    const raw = String(get(row, [
      "alert_level",
      "risk_level",
      "niveau_risque",
      "niveau",
      "classe",
      "level"
    ], "")).toLowerCase();

    if (raw.includes("crit")) return "critical";
    if (raw.includes("high") || raw.includes("warning") || raw.includes("élev") || raw.includes("elev")) return "warning";
    if (raw.includes("moy") || raw.includes("medium")) return "medium";
    if (raw.includes("low") || raw.includes("faible") || raw.includes("stable")) return "low";

    const s = riskScore(row);
    if (s >= 85) return "critical";
    if (s >= 65) return "warning";
    if (s >= 40) return "medium";
    return "low";
  }

  function exposure(row) {
    return n(get(row, [
      "risk_brut",
      "RISK_BRUT",
      "exposition",
      "exposure",
      "montant",
      "amount_at_risk"
    ], 0));
  }

  function cpte(row) {
    return get(row, [
      "cpte",
      "CPTE",
      "account",
      "compte",
      "client_id",
      "id"
    ], "N/A");
  }

  function fmtInt(v) {
    return Math.round(n(v)).toLocaleString("fr-FR");
  }

  function fmtMoney(v) {
    v = n(v);
    if (v >= 1000000) return (v / 1000000).toFixed(1).replace(".", ",") + "M TND";
    if (v >= 1000) return (v / 1000).toFixed(1).replace(".", ",") + "K TND";
    return fmtInt(v) + " TND";
  }

  function selectedFilters() {
    const selects = Array.from(document.querySelectorAll("select"));
    const ranges = Array.from(document.querySelectorAll("input[type='range']"));

    let level = "all";
    let minScore = 0;

    selects.forEach(sel => {
      const value = String(sel.value || sel.options?.[sel.selectedIndex]?.text || "").toLowerCase();
      const parentText = String(sel.closest("div, section")?.innerText || "").toLowerCase();

      if (parentText.includes("alert") || value.includes("critical") || value.includes("warning") || value.includes("medium") || value.includes("stable")) {
        level = value;
      }
    });

    if (ranges.length) {
      minScore = n(ranges[0].value);
    }

    return { level, minScore };
  }

  function matchLevel(row, level) {
    if (!level || level.includes("all")) return true;

    const l = riskLevel(row);

    if (level.includes("crit")) return l === "critical";
    if (level.includes("warn") || level.includes("high") || level.includes("élev")) return l === "warning";
    if (level.includes("medium") || level.includes("moy")) return l === "medium";
    if (level.includes("stable") || level.includes("low") || level.includes("faible")) return l === "low";

    return true;
  }

  function findCard(labelWords) {
    const cards = Array.from(document.querySelectorAll("div, section, article"));

    const matches = cards
      .map(el => {
        const text = String(el.innerText || "").toLowerCase();
        const ok = labelWords.every(w => text.includes(w));
        const rect = el.getBoundingClientRect();
        return { el, ok, area: rect.width * rect.height };
      })
      .filter(x => x.ok && x.area > 500)
      .sort((a, b) => a.area - b.area);

    return matches.length ? matches[0].el : null;
  }

  function setCard(labelWords, value) {
    const card = findCard(labelWords);
    if (!card) return;

    const children = Array.from(card.querySelectorAll("*"))
      .filter(el => el.children.length === 0)
      .filter(el => {
        const t = String(el.innerText || "").trim();
        if (!t) return false;
        const low = t.toLowerCase();
        if (labelWords.some(w => low.includes(w))) return false;
        return t === "—" || t === "--" || /\d/.test(t) || t.includes("TND") || t.includes("%");
      });

    const target = children[0];
    if (target) target.innerText = value;
  }

  function render(dataRows, sourceLabel) {
    const total = dataRows.length;
    const critical = dataRows.filter(r => riskLevel(r) === "critical").length;
    const warning = dataRows.filter(r => riskLevel(r) === "warning").length;
    const medium = dataRows.filter(r => riskLevel(r) === "medium").length;
    const low = dataRows.filter(r => riskLevel(r) === "low").length;
    const notify = critical + warning;
    const avg = total ? dataRows.reduce((s, r) => s + riskScore(r), 0) / total : 0;
    const exp = dataRows.reduce((s, r) => s + exposure(r), 0);

    setCard(["total"], fmtInt(total));
    setCard(["crit"], fmtInt(critical));
    setCard(["élev"], fmtInt(warning));
    setCard(["notifier"], fmtInt(notify));
    setCard(["score", "moy"], Math.round(avg) + "%");
    setCard(["exposition"], fmtMoney(exp));

    updateResultBox({
      sourceLabel,
      total,
      critical,
      warning,
      medium,
      low,
      notify,
      avg,
      exp,
      dataRows
    });
  }

  function updateResultBox(stats) {
    let box = document.getElementById("dashboardDataFixBox");

    if (!box) {
      box = document.createElement("div");
      box.id = "dashboardDataFixBox";
      box.style.margin = "14px 0";
      box.style.padding = "14px 18px";
      box.style.border = "1px solid rgba(95,251,214,.35)";
      box.style.borderRadius = "12px";
      box.style.background = "rgba(7,17,38,.85)";
      box.style.color = "#d9e2ff";
      box.style.fontSize = "14px";

      const filterZone = Array.from(document.querySelectorAll("div, section"))
        .find(el => {
          const txt = String(el.innerText || "").toLowerCase();
          return txt.includes("minimum score") && txt.includes("alert");
        });

      if (filterZone && filterZone.parentElement) {
        filterZone.parentElement.insertBefore(box, filterZone.nextSibling);
      } else {
        document.body.appendChild(box);
      }
    }

    const top = stats.dataRows
      .slice()
      .sort((a, b) => riskScore(b) - riskScore(a))
      .slice(0, 8);

    box.innerHTML = `
      <div style="font-weight:900;color:#5ffbd6;margin-bottom:8px">
        Dashboard data loaded — ${stats.sourceLabel}
      </div>

      <div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:12px">
        <span>Total: <b>${fmtInt(stats.total)}</b></span>
        <span>Critical: <b>${fmtInt(stats.critical)}</b></span>
        <span>Warning: <b>${fmtInt(stats.warning)}</b></span>
        <span>Medium: <b>${fmtInt(stats.medium)}</b></span>
        <span>Low: <b>${fmtInt(stats.low)}</b></span>
        <span>To notify: <b>${fmtInt(stats.notify)}</b></span>
        <span>Avg score: <b>${Math.round(stats.avg)}%</b></span>
        <span>Exposure: <b>${fmtMoney(stats.exp)}</b></span>
      </div>

      <div style="font-weight:900;color:#ffb4ab;margin-bottom:6px">
        Top clients
      </div>

      <div style="display:grid;gap:6px">
        ${top.map(r => `
          <div style="display:grid;grid-template-columns:160px 90px 120px 130px 80px;gap:10px;border-bottom:1px solid rgba(148,163,184,.18);padding:6px 0">
            <b>${cpte(r)}</b>
            <span>${riskScore(r).toFixed(1)}%</span>
            <span>${riskLevel(r).toUpperCase()}</span>
            <span>${fmtMoney(exposure(r))}</span>
            <a href="/client?cpte=${encodeURIComponent(cpte(r))}" style="color:#5ffbd6;font-weight:900">Open</a>
          </div>
        `).join("")}
      </div>
    `;
  }

  function findApplyButton() {
    return Array.from(document.querySelectorAll("button, a"))
      .find(el => String(el.innerText || "").toLowerCase().includes("apply filters"));
  }

  function connectButtons() {
    const apply = findApplyButton();

    if (apply) {
      apply.onclick = function (e) {
        e.preventDefault();
        e.stopPropagation();

        const f = selectedFilters();

        const filtered = rows.filter(r => {
          if (riskScore(r) < f.minScore) return false;
          if (!matchLevel(r, f.level)) return false;
          return true;
        });

        render(filtered, "manual filters applied");
      };
    }

    const reset = Array.from(document.querySelectorAll("button, a"))
      .find(el => String(el.innerText || "").toLowerCase().includes("reset filters"));

    if (reset) {
      reset.onclick = function (e) {
        e.preventDefault();
        e.stopPropagation();
        render(rows, "reset / full portfolio");
      };
    }
  }

  async function init() {
    try {
      const res = await fetch("/attached_assets/dashboard_clients_full.json?nocache=" + Date.now());
      const json = await res.json();

      if (Array.isArray(json)) rows = json;
      else if (Array.isArray(json.data)) rows = json.data;
      else if (Array.isArray(json.clients)) rows = json.clients;
      else rows = Object.values(json || {});

      console.log("BIAT dashboard data fix loaded:", rows.length);

      render(rows, "full portfolio");
      connectButtons();

      setTimeout(connectButtons, 1000);
      setTimeout(connectButtons, 2000);
    } catch (err) {
      console.error("BIAT dashboard data fix error:", err);
      alert("Erreur dashboard: impossible de charger dashboard_clients_full.json");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();