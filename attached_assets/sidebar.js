(function () {
  const routes = [
    { href: "/dashboard", icon: "dashboard", label: "Global Dashboard" },
    { href: "/evolution", icon: "trending_up", label: "Risk Evolution" },
    { href: "/future", icon: "online_prediction", label: "Future Prediction" },
    { href: "/notifications", icon: "notifications", label: "Notifications", badge: "4847" },
    { href: "/client", icon: "group", label: "Client Profiles" },
    { href: "/performance", icon: "analytics", label: "Model Performance" },
    { href: "/assistant", icon: "smart_toy", label: "AI Assistant" }
  ];

  function removeOldBiatSidebars() {
    document.querySelectorAll("aside").forEach((aside) => {
      const txt = (aside.innerText || "").toLowerCase();

      const isBiatSidebar =
        txt.includes("biat risk") &&
        txt.includes("global dashboard") &&
        txt.includes("risk evolution");

      if (isBiatSidebar) {
        aside.remove();
      }
    });

    document.querySelectorAll(".biat-sidebar").forEach((el) => el.remove());
  }

  function injectStyles() {
    if (document.getElementById("biat-sidebar-style")) return;

    const style = document.createElement("style");
    style.id = "biat-sidebar-style";
    style.textContent = `
      body {
        padding-left: 240px !important;
      }

      .biat-sidebar {
        position: fixed !important;
        left: 0 !important;
        top: 0 !important;
        width: 240px !important;
        height: 100vh !important;
        background: #071126 !important;
        border-right: 1px solid rgba(148, 163, 184, 0.18) !important;
        z-index: 99999 !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 24px 14px 16px 14px !important;
        box-sizing: border-box !important;
        font-family: "JetBrains Mono", Inter, Arial, sans-serif !important;
      }

      .biat-sidebar .brand {
        padding: 0 6px 28px 6px !important;
      }

      .biat-sidebar .brand-title {
        margin: 0 !important;
        color: #f3f7ff !important;
        font-size: 26px !important;
        line-height: 1.14 !important;
        font-weight: 900 !important;
        letter-spacing: .2px !important;
        font-family: Inter, Arial, sans-serif !important;
      }

      .biat-sidebar .brand-subtitle {
        margin: 8px 0 0 0 !important;
        color: rgba(217, 226, 255, .72) !important;
        font-size: 13px !important;
        font-family: Inter, Arial, sans-serif !important;
      }

      .biat-sidebar nav {
        display: flex !important;
        flex-direction: column !important;
        gap: 7px !important;
      }

      .biat-sidebar .nav-link {
        height: 46px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 0 14px !important;
        border-radius: 10px !important;
        color: #b9c6e4 !important;
        text-decoration: none !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        box-sizing: border-box !important;
        white-space: nowrap !important;
        overflow: hidden !important;
      }

      .biat-sidebar .nav-link:hover {
        background: rgba(95, 251, 214, .08) !important;
        color: white !important;
      }

      .biat-sidebar .nav-link.active {
        background: rgba(121, 143, 185, .35) !important;
        color: white !important;
        font-weight: 900 !important;
      }

      .biat-sidebar .material-symbols-outlined {
        font-size: 22px !important;
        width: 24px !important;
        min-width: 24px !important;
        line-height: 1 !important;
      }

      .biat-sidebar .label {
        overflow: hidden !important;
        text-overflow: ellipsis !important;
      }

      .biat-sidebar .badge {
        margin-left: auto !important;
        background: #ffb4ab !important;
        color: #3b0505 !important;
        border-radius: 999px !important;
        padding: 2px 7px !important;
        font-size: 10px !important;
        font-weight: 900 !important;
      }

      .biat-sidebar .bottom {
        margin-top: auto !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
        border-top: 1px solid rgba(148, 163, 184, .16) !important;
        padding-top: 14px !important;
      }

      .biat-sidebar .critical-btn,
      .biat-sidebar .bottom-btn {
        height: 46px !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        cursor: pointer !important;
        font-size: 13px !important;
        font-weight: 900 !important;
      }

      .biat-sidebar .critical-btn {
        background: #b00012 !important;
        color: white !important;
      }

      .biat-sidebar .bottom-btn {
        background: transparent !important;
        color: #b9c6e4 !important;
      }

      .biat-sidebar .bottom-btn:hover {
        background: rgba(95, 251, 214, .08) !important;
        color: white !important;
      }

      main {
        margin-left: 0 !important;
      }
    `;

    document.head.appendChild(style);
  }

  function injectSidebar() {
    removeOldBiatSidebars();
    injectStyles();

    const currentPath = window.location.pathname;

    const aside = document.createElement("aside");
    aside.className = "biat-sidebar";

    aside.innerHTML = `
      <div class="brand">
        <h1 class="brand-title">BIAT Risk<br>Monitor</h1>
        <p class="brand-subtitle">Vigilant Professionalism</p>
      </div>

      <nav>
        ${routes.map((r) => {
          const active =
            r.href === currentPath ||
            (r.href === "/client" && currentPath.startsWith("/client"));

          return `
            <a class="nav-link ${active ? "active" : ""}" href="${r.href}">
              <span class="material-symbols-outlined">${r.icon}</span>
              <span class="label">${r.label}</span>
              ${r.badge ? `<span class="badge">${r.badge}</span>` : ""}
            </a>
          `;
        }).join("")}
      </nav>

      <div class="bottom">
        <button type="button" class="critical-btn" id="criticalAlertsBtn">
          <span class="material-symbols-outlined">warning</span>
          <span>Critical Alerts</span>
        </button>

        <button type="button" class="bottom-btn" id="settingsBtn">
          <span class="material-symbols-outlined">settings</span>
          <span>Settings</span>
        </button>

        <button type="button" class="bottom-btn" id="supportBtn">
          <span class="material-symbols-outlined">help</span>
          <span>Support</span>
        </button>
      </div>
    `;

    document.body.prepend(aside);

    aside.querySelectorAll("a[href]").forEach((a) => {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = this.getAttribute("href");
      });
    });

    document.getElementById("criticalAlertsBtn")?.addEventListener("click", function () {
      window.location.href = "/notifications?alert=CRITICAL";
    });

    document.getElementById("settingsBtn")?.addEventListener("click", function () {
      alert("Settings - BIAT Risk Monitor");
    });

    document.getElementById("supportBtn")?.addEventListener("click", function () {
      alert("Support - BIAT Risk Monitor");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectSidebar);
  } else {
    injectSidebar();
  }
})();