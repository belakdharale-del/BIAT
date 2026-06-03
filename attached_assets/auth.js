// ============================================================
// BIAT Risk Monitor - auth.js CLEAN
// Auth + header user + logout/settings/support only
// No global navigation interception
// No preventDefault for sidebar links
// No MutationObserver
// No setInterval
// ============================================================

(function () {
  const path = window.location.pathname;

  const isLoginPage =
    path === "/" ||
    path === "/login" ||
    path.includes("login_biat_risk_monitor");

  // Protect internal pages
  if (!isLoginPage) {
    const isAuthenticated = localStorage.getItem("biat_auth") === "true";

    if (!isAuthenticated) {
      window.location.href = "/login";
      return;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const username = localStorage.getItem("biat_user") || "ALA";
    const role = localStorage.getItem("biat_role") || "Risk Officer";

    updateHeaderUser(username, role);
    activateQuickAction();
    activateNotificationIcon();
    activateUserMenu(username, role);
    activateSettingsSupport(username, role);
  });

  function updateHeaderUser(username, role) {
    const header = document.querySelector("header");
    if (!header) return;

    const elements = header.querySelectorAll("p, span, div");

    elements.forEach((el) => {
      const text = (el.innerText || "").trim();

      if (
        text === "A. Mansour" ||
        text === "D. Ben Salem" ||
        text === "R. Khelifi" ||
        text === "R. Dupont" ||
        text === "Risk Officer Name" ||
        text === "ALA"
      ) {
        el.innerText = username;
      }

      if (
        text === "Chief Risk Manager" ||
        text === "Risk Officer" ||
        text === "ADMIN" ||
        text === "Admin"
      ) {
        el.innerText = role;
      }
    });
  }

  function activateQuickAction() {
    document.querySelectorAll("button").forEach((button) => {
      const text = (button.innerText || "").trim().toLowerCase();

      if (text.includes("quick action")) {
        button.onclick = function () {
          window.location.href = "/assistant";
        };
      }
    });
  }

  function activateNotificationIcon() {
    document.querySelectorAll(".material-symbols-outlined").forEach((icon) => {
      const text = (icon.innerText || "").trim();

      if (text === "notifications") {
        icon.style.cursor = "pointer";
        icon.onclick = function () {
          window.location.href = "/notifications";
        };
      }
    });
  }

  function activateUserMenu(username, role) {
    const header = document.querySelector("header");
    if (!header) return;

    let userZone = header.querySelector(".border-l");

    if (!userZone) {
      const divs = header.querySelectorAll("div");
      userZone = divs[divs.length - 1];
    }

    if (!userZone) return;

    userZone.style.cursor = "pointer";

    userZone.onclick = function () {
      const oldMenu = document.getElementById("userMenu");

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
      menu.style.fontFamily = "Inter, Arial, sans-serif";

      menu.innerHTML = `
        <div style="margin-bottom:12px">
          <p style="font-weight:700;margin:0">${username}</p>
          <p style="font-size:12px;color:#bacac3;margin:4px 0 0">${role}</p>
        </div>

        <button id="profileBtn"
          style="
            width:100%;
            padding:10px;
            border-radius:8px;
            background:#1f2942;
            color:#d9e2ff;
            border:none;
            margin-bottom:8px;
            cursor:pointer;
          ">
          Profil utilisateur
        </button>

        <button id="logoutBtn"
          style="
            width:100%;
            padding:10px;
            border-radius:8px;
            background:#93000a;
            color:#ffdad6;
            border:none;
            cursor:pointer;
          ">
          Déconnexion
        </button>
      `;

      document.body.appendChild(menu);

      const profileBtn = document.getElementById("profileBtn");
      const logoutBtn = document.getElementById("logoutBtn");

      if (profileBtn) {
        profileBtn.onclick = function () {
          alert("Utilisateur : " + username + "\nRôle : " + role);
        };
      }

      if (logoutBtn) {
        logoutBtn.onclick = function () {
          localStorage.removeItem("biat_auth");
          localStorage.removeItem("biat_user");
          localStorage.removeItem("biat_role");
          window.location.href = "/login";
        };
      }
    };
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
        z-index: 99998;
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

    const closeBtn = document.getElementById("biat-modal-close");
    if (closeBtn) closeBtn.onclick = closeBiatModal;

    modal.addEventListener("click", function (event) {
      if (event.target === modal.firstElementChild) {
        closeBiatModal();
      }
    });
  }

  function activateSettingsSupport(username, role) {
    document.querySelectorAll("aside a, aside button, aside div, nav a, nav div").forEach((el) => {
      const text = (el.innerText || "").trim().toLowerCase();

      if (text.includes("settings")) {
        el.style.cursor = "pointer";
        el.onclick = function () {
          openBiatModal(
            "Settings",
            `
              <div style="display:grid; gap:14px;">
                <div style="background:#07122a; padding:14px; border-radius:12px;">
                  <strong>Utilisateur connecté</strong><br>
                  ${username}
                </div>

                <div style="background:#07122a; padding:14px; border-radius:12px;">
                  <strong>Rôle</strong><br>
                  ${role}
                </div>

                <div style="background:#07122a; padding:14px; border-radius:12px;">
                  <strong>État système</strong><br>
                  Application locale active sur <code>localhost:5000</code>
                </div>
              </div>
            `
          );
        };
      }

      if (text.includes("support")) {
        el.style.cursor = "pointer";
        el.onclick = function () {
          openBiatModal(
            "Support",
            `
              <div style="display:grid; gap:14px;">
                <div style="background:#07122a; padding:14px; border-radius:12px;">
                  <strong>BIAT Risk Monitor — Aide rapide</strong><br>
                  Pages disponibles : Dashboard, Risk Evolution, Future Prediction,
                  Notifications, Client Profiles, Model Performance, AI Assistant.
                </div>

                <div style="background:#07122a; padding:14px; border-radius:12px;">
                  <strong>Important</strong><br>
                  La navigation doit rester faite par les liens HTML normaux :
                  <code>&lt;a href="/dashboard"&gt;</code>,
                  <code>&lt;a href="/notifications"&gt;</code>, etc.
                </div>
              </div>
            `
          );
        };
      }
    });
  }
})();