"""
Page 4: Fiche Client
360° client profile with history, gauge, and risk explanation.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Fiche Client | BIAT", page_icon="👤", layout="wide")

from app.utils.style import apply_global_style, page_header, kpi_card, section_header
from app.utils.data_loader import load_scoring_clients, load_scoring_evolution
from app.utils.business_rules import ALERT_COLORS, ALERT_CSS, explain_risk, format_number

apply_global_style()

# ── Load ──────────────────────────────────────────────────────────────────────
df_score = load_scoring_clients()
df_evo   = load_scoring_evolution()

all_cptes = sorted(df_score["CPTE"].unique())

page_header("👤", "Fiche Client",
            "Profil 360° individuel — Historique, score, évolution et action recommandée")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Sélectionner un Client")
    search = st.text_input("Recherche CPTE", "")
    filtered_cptes = [c for c in all_cptes if search.upper() in c] if search else all_cptes
    if not filtered_cptes:
        st.warning("Aucun compte trouvé.")
        st.stop()
    sel_cpte = st.selectbox("Compte", filtered_cptes)

# ── Client data ───────────────────────────────────────────────────────────────
client_hist = df_score[df_score["CPTE"] == sel_cpte].sort_values("PERIODE")
if client_hist.empty:
    st.warning("Données introuvables pour ce client.")
    st.stop()

latest = client_hist.iloc[-1]
evo_row = df_evo[(df_evo["CPTE"] == sel_cpte)].sort_values("PERIODE")
latest_evo = evo_row.iloc[-1] if not evo_row.empty else {}

niveau     = latest.get("niveau_alerte", "Faible")
score_pct  = float(latest.get("score_pct", 0))
action     = latest.get("action_recommandee", "—")
css_class  = ALERT_CSS.get(niveau, "faible")
color      = ALERT_COLORS.get(niveau, "#22c55e")
evolution  = latest_evo.get("evolution", "—") if isinstance(latest_evo, dict) else latest_evo.get("evolution", "—")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0f172a,#1a2540);
     border:1px solid {color}55; border-left:4px solid {color};
     border-radius:14px; padding:20px 28px; margin-bottom:20px;
     display:flex; justify-content:space-between; flex-wrap:wrap; gap:16px;">
    <div>
        <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase;">Compte client</div>
        <div style="font-size:1.8rem; font-weight:800; color:#f1f5f9;">{sel_cpte}</div>
        <div style="margin-top:6px;">
            <span class="badge badge-{css_class}">{niveau}</span>
        </div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:0.75rem; color:#64748b;">Dernière observation</div>
        <div style="font-size:1rem; color:#94a3b8; font-weight:600;">
            {latest.get("PERIODE", "").strftime("%B %Y") if hasattr(latest.get("PERIODE",""), "strftime") else str(latest.get("PERIODE",""))}
        </div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">
            Évolution : <span style="color:{color}; font-weight:600;">{evolution}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: kpi_card("Score Actuel",     f"{score_pct:.1f}%",  css_class, "Risque estimé")
with c2: kpi_card("Niveau d'Alerte",  niveau,               css_class, "Classification")
with c3: kpi_card("Jours Découvert",  f"{int(latest.get('NBRJDEP',0))}", "orange", "Ce mois")
with c4: kpi_card("Risque Brut",      f"{format_number(latest.get('RISK_BRUT',0))} DT", "red", "Exposition")
with c5: kpi_card("Évolution",        evolution,            "blue",    "vs mois précédent")
with c6: kpi_card("Mois Consécutifs", f"{int(latest.get('MOIS_CONSEC',0))}", "yellow", "Découvert")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Gauge + charts ────────────────────────────────────────────────────────────
section_header("Indicateurs Visuels")
col_g, col_h = st.columns([1, 2])

with col_g:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score_pct,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Score de Risque (%)", "font": {"color": "#f1f5f9", "size": 14}},
        number={"font": {"color": color, "size": 42}, "suffix": "%"},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#64748b", "tickfont": {"color": "#64748b"}},
            "bar": {"color": color},
            "steps": [
                {"range": [0,  40], "color": "#052e16"},
                {"range": [40, 65], "color": "#1c1402"},
                {"range": [65, 85], "color": "#1c0a00"},
                {"range": [85,100], "color": "#1c0000"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": score_pct},
        },
    ))
    fig_gauge.update_layout(
        paper_bgcolor="#111827", font_color="#f1f5f9",
        margin=dict(t=40, b=20, l=20, r=20), height=280,
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_h:
    fig_score = px.line(
        client_hist, x="PERIODE", y="score_pct",
        title="Évolution du Score de Risque",
        markers=True, color_discrete_sequence=[color],
    )
    fig_score.add_hline(y=40, line_dash="dot", line_color="#22c55e", annotation_text="Moyen")
    fig_score.add_hline(y=65, line_dash="dot", line_color="#eab308", annotation_text="Élevé")
    fig_score.add_hline(y=85, line_dash="dot", line_color="#ef4444", annotation_text="Critique")
    fig_score.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0f172a", font_color="#f1f5f9",
        xaxis=dict(gridcolor="#1e2d4a"), yaxis=dict(gridcolor="#1e2d4a", range=[0, 105]),
        margin=dict(t=50, b=20), height=280,
    )
    st.plotly_chart(fig_score, use_container_width=True)

# ── NBRJDEP and RISK_BRUT charts ──────────────────────────────────────────────
section_header("Historique des Indicateurs Clés")
hc1, hc2 = st.columns(2)

with hc1:
    fig_dep = px.bar(client_hist, x="PERIODE", y="NBRJDEP",
                     title="Jours à Découvert par Mois",
                     color_discrete_sequence=["#f97316"])
    fig_dep.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0f172a", font_color="#f1f5f9",
        xaxis=dict(gridcolor="#1e2d4a"), yaxis=dict(gridcolor="#1e2d4a"),
        margin=dict(t=50,b=20),
    )
    st.plotly_chart(fig_dep, use_container_width=True)

with hc2:
    if "RISK_BRUT" in client_hist.columns:
        fig_risk = px.bar(client_hist, x="PERIODE", y="RISK_BRUT",
                          title="Risque Brut par Mois (DT)",
                          color_discrete_sequence=["#ef4444"])
        fig_risk.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#0f172a", font_color="#f1f5f9",
            xaxis=dict(gridcolor="#1e2d4a"), yaxis=dict(gridcolor="#1e2d4a"),
            margin=dict(t=50,b=20),
        )
        st.plotly_chart(fig_risk, use_container_width=True)

# ── Risk explanation ──────────────────────────────────────────────────────────
section_header("Pourquoi ce Client est Risqué ?")
explanations = explain_risk(latest.to_dict())
exp_html = "".join([f"<li style='margin:4px 0;'>{e}</li>" for e in explanations])
st.markdown(f"""
<div class="info-box">
    <ul style="margin:0; padding-left:18px; list-style:none;">{exp_html}</ul>
</div>
""", unsafe_allow_html=True)

# ── Action box ────────────────────────────────────────────────────────────────
section_header("Action Recommandée")
st.markdown(f"""
<div class="action-box action-{css_class}">
    ⚡ {action}
</div>
""", unsafe_allow_html=True)

# ── Suivi form ────────────────────────────────────────────────────────────────
section_header("Simulation de Suivi")
with st.form(key=f"suivi_{sel_cpte}"):
    statut = st.selectbox("Statut du suivi",
                           ["À contacter","Contacté","En suivi","Régularisé","Escaladé"])
    commentaire = st.text_area("Commentaire", placeholder="Saisir vos observations...")
    submitted = st.form_submit_button("💾 Enregistrer le suivi")
    if submitted:
        st.success(f"✅ Suivi enregistré pour {sel_cpte} — Statut : **{statut}**")
        if commentaire:
            st.info(f"📝 Commentaire : {commentaire}")
