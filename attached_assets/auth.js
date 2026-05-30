(function () {
  const path = window.location.pathname;
  const isLogin = path === "/login" || path.includes("login_biat_risk_monitor");

  if (!isLogin) {
    const isAuth = localStorage.getItem("biat_auth") === "true";

    if (!isAuth) {
      window.location.href = "/login";
      return;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const username = localStorage.getItem("biat_user") || "Risk Officer";
    const role = localStorage.getItem("biat_role") || "Risk Officer";

    // 1) Remplacer automatiquement le nom utilisateur dans tous les headers
    function updateHeaderUser() {
      const header = document.querySelector("header");
      if (!header) return;

      // Cherche les blocs texte dans le header
      const textElements = header.querySelectorAll("p, span, div");

      textElements.forEach((el) => {
        const txt = (el.innerText || "").trim();

        if (
          txt === "A. Mansour" ||
          txt === "D. Ben Salem" ||
          txt === "R. Khelifi" ||
          txt === "ADMIN" ||
          txt === "Chief Risk Manager" ||
          txt === "Risk Officer"
        ) {
          if (
            txt === "ADMIN" ||
            txt === "Chief Risk Manager" ||
            txt === "Risk Officer"
          ) {
            el.innerText = role;
          } else {
            el.innerText = username;
          }
        }
      });
    }

    updateHeaderUser();

    // 2) Quick Action -> Notifications
    document.querySelectorAll("button").forEach((btn) => {
      const txt = (btn.innerText || "").trim().toLowerCase();

      if (txt.includes("quick action")) {
        btn.onclick = function () {
          window.location.href = "/notifications";
        };
      }
    });

    // 3) Icône notification -> Notifications
    document.querySelectorAll(".material-symbols-outlined").forEach((icon) => {
      const txt = (icon.innerText || "").trim();

      if (txt === "notifications") {
        icon.style.cursor = "pointer";
        icon.onclick = function () {
          window.location.href = "/notifications";
        };
      }
    });

    // 4) Zone utilisateur -> menu Profil / Déconnexion
    function makeUserMenuActive() {
      const header = document.querySelector("header");
      if (!header) return;

      let userZone = null;

      // Cas dashboard
      userZone = header.querySelector(".border-l");

      // Cas risk evolution : souvent dernier bloc du header
      if (!userZone) {
        const divs = header.querySelectorAll("div");
        userZone = divs[divs.length - 1];
      }

      if (!userZone) return;

      userZone.style.cursor = "pointer";

      userZone.onclick = function () {
        let oldMenu = document.getElementById("userMenu");
        if (oldMenu) {
          oldMenu.remove();
          return;
        }

        const menu = document.createElement("div");
        menu.id = "userMenu";
        menu.style.position = "fixed";
        menu.style.top = "64px";
        menu.style.right = "24px";
        menu.style.zIndex = "99999";
        menu.style.width = "240px";
        menu.style.background = "#101b33";
        menu.style.border = "1px solid #3c4a45";
        menu.style.borderRadius = "14px";
        menu.style.padding = "14px";
        menu.style.boxShadow = "0 20px 40px rgba(0,0,0,.45)";
        menu.style.color = "#d9e2ff";
        menu.style.fontFamily = "Inter, sans-serif";

        menu.innerHTML = `
          <div style="margin-bottom:12px">
            <p style="font-weight:700;margin:0">${username}</p>
            <p style="font-size:12px;color:#bacac3;margin:4px 0 0">${role}</p>
          </div>

          <button id="profileBtn"
            style="width:100%;padding:10px;border-radius:8px;background:#1f2942;color:#d9e2ff;border:none;margin-bottom:8px;cursor:pointer">
            Profil utilisateur
          </button>

          <button id="logoutBtn"
            style="width:100%;padding:10px;border-radius:8px;background:#93000a;color:#ffdad6;border:none;cursor:pointer">
            Déconnexion
          </button>
        `;

        document.body.appendChild(menu);

        document.getElementById("profileBtn").onclick = function () {
          alert("Utilisateur : " + username + "\\nRôle : " + role);
        };

        document.getElementById("logoutBtn").onclick = function () {
          localStorage.removeItem("biat_auth");
          localStorage.removeItem("biat_user");
          localStorage.removeItem("biat_role");
          window.location.href = "/login";
        };
      };
    }

    makeUserMenuActive();
  });
})();
/* BIAT SETTINGS AND SUPPORT FIX */
document.addEventListener("DOMContentLoaded", () => {
  function getCurrentUser() {
    return localStorage.getItem("biat_user") || "Risk Officer";
  }

  function getCurrentRole() {
    return localStorage.getItem("biat_role") || "Risk Officer";
  }

  function closeBiatModal() {
    const oldModal = document.getElementById("biat-global-modal");
    if (oldModal) oldModal.remove();
  }

  function openBiatModal(title, bodyHtml) {
    closeBiatModal();

    const modal = document.createElement("div");
    modal.id = "biat-global-modal";
    modal.innerHTML = `
      <div style="
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.55);
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 24px;
      ">
        <div style="
          width: min(560px, 95vw);
          background: #101b33;
          color: #d9e2ff;
          border: 1px solid rgba(95,251,214,0.25);
          border-radius: 18px;
          box-shadow: 0 24px 80px rgba(0,0,0,0.45);
          overflow: hidden;
          font-family: Inter, Arial, sans-serif;
        ">
          <div style="
            padding: 18px 22px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            display: flex;
            align-items: center;
            justify-content: space-between;
          ">
            <div style="
              font-size: 18px;
              font-weight: 800;
              color: #5ffbd6;
              letter-spacing: 0.02em;
            ">
              ${title}
            </div>
            <button id="biat-modal-close" style="
              background: transparent;
              border: 0;
              color: #d9e2ff;
              font-size: 24px;
              cursor: pointer;
              line-height: 1;
            ">×</button>
          </div>

          <div style="padding: 22px; line-height: 1.65; font-size: 14px;">
            ${bodyHtml}
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("biat-modal-close").onclick = closeBiatModal;

    modal.addEventListener("click", (event) => {
      if (event.target === modal.firstElementChild) {
        closeBiatModal();
      }
    });
  }

  function openSettings() {
    const user = getCurrentUser();
    const role = getCurrentRole();

    openBiatModal(
      "Settings",
      `
        <div style="display:grid; gap:14px;">
          <div style="background:#07122a; padding:14px; border-radius:12px; border:1px solid rgba(255,255,255,0.08);">
            <strong>Utilisateur connecté</strong><br>
            ${user}
          </div>

          <div style="background:#07122a; padding:14px; border-radius:12px; border:1px solid rgba(255,255,255,0.08);">
            <strong>Rôle</strong><br>
            ${role}
          </div>

          <div style="background:#07122a; padding:14px; border-radius:12px; border:1px solid rgba(255,255,255,0.08);">
            <strong>État système</strong><br>
            Application locale active sur <code>localhost:5000</code><br>
            Données synchronisées depuis <code>attached_assets</code>
          </div>

          <button id="biat-logout-btn" style="
            margin-top:8px;
            background:#93000a;
            color:#ffdad6;
            border:0;
            padding:12px 16px;
            border-radius:10px;
            font-weight:700;
            cursor:pointer;
          ">
            Se déconnecter
          </button>
        </div>
      `
    );

    setTimeout(() => {
      const logoutBtn = document.getElementById("biat-logout-btn");
      if (logoutBtn) {
        logoutBtn.onclick = () => {
          localStorage.removeItem("biat_auth");
          localStorage.removeItem("biat_user");
          localStorage.removeItem("biat_role");
          window.location.href = "/login";
        };
      }
    }, 50);
  }

  function openSupport() {
    openBiatModal(
      "Support",
      `
        <div style="display:grid; gap:14px;">
          <div style="background:#07122a; padding:14px; border-radius:12px; border:1px solid rgba(255,255,255,0.08);">
            <strong>BIAT Risk Monitor — Aide rapide</strong><br>
            Cette application permet de suivre les clients à risque, les anomalies, les notifications et les performances du modèle.
          </div>

          <div style="background:#07122a; padding:14px; border-radius:12px; border:1px solid rgba(255,255,255,0.08);">
            <strong>Pages principales</strong><br>
            • Global Dashboard : vue globale du portefeuille<br>
            • Risk Evolution : évolution du risque<br>
            • Notifications : clients à notifier<br>
            • Client Profiles : analyse client par CPTE<br>
            • Model Performance : performances ML<br>
            • AI Assistant : assistant conversationnel
          </div>

          <div style="background:#07122a; padding:14px; border-radius:12px; border:1px solid rgba(255,255,255,0.08);">
            <strong>Exemples de questions Assistant IA</strong><br>
            • Combien de clients critiques avons-nous ?<br>
            • Quels clients notifier en priorité ?<br>
            • Analyse le client CPTE_001508<br>
            • Comment évoluent les clients critiques ?<br>
            • Compare scoring ML et anomalies
          </div>

          <div style="background:#07122a; padding:14px; border-radius:12px; border:1px solid rgba(255,255,255,0.08);">
            <strong>Note</strong><br>
            Si Groq ne répond pas, l’assistant utilise automatiquement les données locales réelles via le fallback.
          </div>
        </div>
      `
    );
  }

  document.querySelectorAll("aside div, aside button, nav div").forEach((el) => {
    const text = (el.innerText || "").trim().toLowerCase();

    if (text.includes("settings")) {
      el.style.cursor = "pointer";
      el.onclick = openSettings;
    }

    if (text.includes("support")) {
      el.style.cursor = "pointer";
      el.onclick = openSupport;
    }
  });
});