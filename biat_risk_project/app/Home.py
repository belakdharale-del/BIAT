"""
BIAT Risk Monitor — Home Page
Executive landing page with KPIs and navigation.
"""
import os, sys
# Add biat_risk_project root to path so `app.utils.*` imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

st.set_page_config(
    page_title="BIAT Risk Monitor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.utils.style import apply_global_style, page_header, kpi_card, section_header
from app.utils.data_loader import load_scoring_clients, load_model_comparison, get_current_period_data

apply_global_style()

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 10px 0 20px;">
        <div style="font-size:2.2rem;">🏦</div>
        <div style="font-size:1.1rem; font-weight:700; color:#f1f5f9;">BIAT Risk Monitor</div>
        <div style="font-size:0.72rem; color:#64748b; margin-top:2px;">Vigilant Professionalism</div>
    </div>
    <hr style="border-color:#1e2d4a; margin:0 0 16px;">
    """, unsafe_allow_html=True)
    st.markdown("**Navigation**")
    st.page_link("Home.py",                          label="🏠 Accueil")
    st.page_link("pages/1_Dashboard_global.py",      label="📊 Dashboard Global")
    st.page_link("pages/2_Evolution_risque.py",      label="📈 Évolution du Risque")
    st.page_link("pages/3_Clients_a_notifier.py",    label="🔔 Clients à Notifier")
    st.page_link("pages/4_Fiche_client.py",          label="👤 Fiche Client")
    st.page_link("pages/5_Performance_modele.py",    label="🎯 Performance Modèle")
    st.page_link("pages/6_Chatbot.py",               label="🤖 Assistant BIAT Risk")

# ── Hero section ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 60%,#0f3460 100%);
     border:1px solid #1e3a5f; border-radius:16px; padding:36px 40px; margin-bottom:28px;">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:20px;">
        <div>
            <div style="font-size:0.78rem; color:#3b82f6; font-weight:600;
                 text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">
                PFE 2025 — BIAT
            </div>
            <h1 style="font-size:2.2rem; font-weight:800; color:#f1f5f9; margin:0; line-height:1.15;">
                BIAT Risk Monitor
            </h1>
            <p style="font-size:1.05rem; color:#94a3b8; margin-top:8px; margin-bottom:20px;">
                Système de prédiction du risque de dépassement de découvert à 30 jours
            </p>
            <div style="display:flex; flex-wrap:wrap; gap:8px;">
                <span style="background:#1e3a5f; color:#93c5fd; padding:4px 12px;
                      border-radius:999px; font-size:0.75rem; font-weight:600;">Prédiction 30 jours</span>
                <span style="background:#1a2e1a; color:#86efac; padding:4px 12px;
                      border-radius:999px; font-size:0.75rem; font-weight:600;">LightGBM</span>
                <span style="background:#1e1a2e; color:#c4b5fd; padding:4px 12px;
                      border-radius:999px; font-size:0.75rem; font-weight:600;">Streamlit</span>
                <span style="background:#2e1a1a; color:#fca5a5; padding:4px 12px;
                      border-radius:999px; font-size:0.75rem; font-weight:600;">Power BI</span>
                <span style="background:#1a2a2e; color:#67e8f9; padding:4px 12px;
                      border-radius:999px; font-size:0.75rem; font-weight:600;">SHAP-ready</span>
            </div>
        </div>
        <div style="text-align:center; padding:16px 24px; background:rgba(59,130,246,0.08);
             border:1px solid #1e3a5f; border-radius:12px;">
            <div style="font-size:0.72rem; color:#64748b; margin-bottom:4px;">SCORE MODÈLE</div>
            <div style="font-size:3rem; font-weight:800; color:#22c55e;">98.9%</div>
            <div style="font-size:0.75rem; color:#94a3b8;">ROC-AUC LightGBM</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
section_header("Indicateurs Clés de Performance", margin_top="0")

mc = load_model_comparison()
lgbm_row = mc[mc["Modèle"] == "LightGBM"]
roc  = float(lgbm_row["ROC-AUC"].values[0])  if not lgbm_row.empty else 0.9889
rec  = float(lgbm_row["Recall"].values[0])   if not lgbm_row.empty else 0.9372
f1   = float(lgbm_row["F1-score"].values[0]) if not lgbm_row.empty else 0.9450

try:
    df = load_scoring_clients()
    cur = get_current_period_data(df)
    n_clients  = len(cur)
    n_critique = int((cur["niveau_alerte"] == "Critique").sum())
    avg_score  = cur["score_pct"].mean()
    data_ok = True
except Exception:
    n_clients, n_critique, avg_score, data_ok = 0, 0, 0, False

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:  kpi_card("ROC-AUC",  f"{roc:.4f}",  "green",  "LightGBM")
with col2:  kpi_card("Recall",   f"{rec:.4f}",  "blue",   "Priorité métier")
with col3:  kpi_card("F1-Score", f"{f1:.4f}",   "purple", "Équilibre P/R")
with col4:  kpi_card("Clients Scorés",  f"{n_clients:,}" if data_ok else "—", "blue",   "Dernière période")
with col5:  kpi_card("Clients Critiques", f"{n_critique:,}" if data_ok else "—", "red",  "Intervention immédiate")
with col6:  kpi_card("Score Moyen",     f"{avg_score:.1f}%" if data_ok else "—", "orange", "Risque portefeuille")

st.markdown("<hr>", unsafe_allow_html=True)

# ── About ────────────────────────────────────────────────────────────────────
col_a, col_b = st.columns([3, 2])
with col_a:
    section_header("À propos du projet")
    st.markdown("""
    <div class="info-box">
    <p>Ce système prédit <strong>30 jours à l'avance</strong> le risque de dépassement de découvert
    pour chaque client BIAT. Il transforme les données bancaires historiques en
    <strong>alertes opérationnelles</strong> permettant aux gestionnaires de comptes d'intervenir
    avant qu'une situation ne se dégrade.</p>
    <p style="margin-top:10px;">Le moteur ML analyse les comportements transactionnels mensuels et attribue à chaque
    compte un <strong>score de risque de 0 à 100 %</strong>, convertible en niveau d'alerte
    (Faible, Moyen, Élevé, Critique) avec une action recommandée associée.</p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    section_header("Technologies utilisées")
    techs = [
        ("🐍", "Python 3.x",        "#3b82f6"),
        ("🐼", "Pandas / NumPy",     "#22c55e"),
        ("🔬", "Scikit-learn",       "#a855f7"),
        ("⚡", "LightGBM",           "#eab308"),
        ("📊", "Streamlit",          "#ef4444"),
        ("📈", "Plotly",             "#f97316"),
        ("📉", "Power BI",           "#0284c7"),
        ("🔍", "SHAP-ready",         "#64748b"),
    ]
    for icon, name, color in techs:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; padding:4px 0;">
            <span style="font-size:1rem;">{icon}</span>
            <span style="background:{color}22; color:{color}; padding:2px 10px;
                  border-radius:999px; font-size:0.8rem; font-weight:600; border:1px solid {color}44;">
                {name}
            </span>
        </div>
        """, unsafe_allow_html=True)

# ── Navigation cards ─────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
section_header("Modules de l'Application")

pages = [
    ("📊", "Dashboard Global",      "Vue d'ensemble KPIs et distribution des risques",    "#3b82f6"),
    ("📈", "Évolution du Risque",   "Suivi des transitions et tendances du portefeuille",  "#a855f7"),
    ("🔔", "Clients à Notifier",    "Liste opérationnelle priorisée des clients à risque", "#ef4444"),
    ("👤", "Fiche Client",          "Profil 360° et historique individuel par compte",     "#22c55e"),
    ("🎯", "Performance Modèle",    "Métriques ML, matrice de confusion, importances",     "#eab308"),
    ("🤖", "Assistant BIAT Risk",   "Chatbot métier basé sur les données du portefeuille", "#f97316"),
]

cols = st.columns(3)
for i, (icon, title, desc, color) in enumerate(pages):
    with cols[i % 3]:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#111827,#1a2540);
             border:1px solid #1e2d4a; border-left:3px solid {color};
             border-radius:12px; padding:18px 20px; margin-bottom:12px;
             transition:transform 0.15s;">
            <div style="font-size:1.6rem; margin-bottom:6px;">{icon}</div>
            <div style="font-weight:700; font-size:0.95rem; color:#f1f5f9;">{title}</div>
            <div style="font-size:0.78rem; color:#64748b; margin-top:4px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#1e3a5f; font-size:0.72rem; margin-top:32px; padding:16px;">
    BIAT Risk Monitor — Système de surveillance du risque de découvert — PFE 2025
</div>
""", unsafe_allow_html=True)
