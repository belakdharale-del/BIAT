"""
Page 1: Dashboard Global
Managerial KPI overview, charts, and top-risk client table.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Dashboard Global | BIAT", page_icon="📊", layout="wide")

from app.utils.style import apply_global_style, page_header, kpi_card, section_header
from app.utils.data_loader import load_scoring_clients, get_current_period_data
from app.utils.business_rules import ALERT_COLORS, format_number

apply_global_style()
PALETTE = ALERT_COLORS

# ── Load data ─────────────────────────────────────────────────────────────────
df_all = load_scoring_clients()
periods = sorted(df_all["PERIODE"].unique())
period_labels = [p.strftime("%Y-%m") for p in periods]

page_header("📊", "Dashboard Global", "Vue d'ensemble du portefeuille de risque — Dernière période disponible")

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filtres")
    sel_period_label = st.selectbox("Période", period_labels[::-1], index=0)
    sel_period = pd.Timestamp(sel_period_label + "-01")
    sel_niveaux = st.multiselect("Niveau d'alerte", ["Faible","Moyen","Élevé","Critique"],
                                 default=["Faible","Moyen","Élevé","Critique"])
    sel_score_min = st.slider("Score minimum (%)", 0, 100, 0, 5)

df = df_all[df_all["PERIODE"] == sel_period].copy()
if sel_niveaux:
    df = df[df["niveau_alerte"].isin(sel_niveaux)]
df = df[df["score_pct"] >= sel_score_min]

# ── KPIs ──────────────────────────────────────────────────────────────────────
total   = len(df_all[df_all["PERIODE"] == sel_period])
crit    = int((df["niveau_alerte"] == "Critique").sum())
eleve   = int((df["niveau_alerte"] == "Élevé").sum())
to_notif= int(df["niveau_alerte"].isin(["Moyen","Élevé","Critique"]).sum())
avg_sc  = df["score_pct"].mean() if len(df) else 0
risk_amt= df["RISK_BRUT"].sum() if "RISK_BRUT" in df.columns else 0

c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: kpi_card("Clients Scorés",    f"{total:,}",           "blue",   sel_period_label)
with c2: kpi_card("Clients Critiques", f"{crit:,}",            "red",    "Intervention immédiate")
with c3: kpi_card("Clients Élevés",   f"{eleve:,}",           "orange", "Appel sous 48h")
with c4: kpi_card("À Notifier",       f"{to_notif:,}",        "yellow", "Moyen + Élevé + Critique")
with c5: kpi_card("Score Moyen",      f"{avg_sc:.1f}%",       "purple", "Risque portefeuille")
with c6: kpi_card("Risque Brut Total",f"{format_number(risk_amt)} DT","red","Exposition financière")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Charts row 1 ──────────────────────────────────────────────────────────────
section_header("Distribution du Risque")
cc1, cc2 = st.columns(2)

with cc1:
    dist = df["niveau_alerte"].value_counts().reset_index()
    dist.columns = ["niveau_alerte", "count"]
    order = ["Faible","Moyen","Élevé","Critique"]
    dist["niveau_alerte"] = pd.Categorical(dist["niveau_alerte"], categories=order, ordered=True)
    dist.sort_values("niveau_alerte", inplace=True)
    colors = [PALETTE.get(n, "#94a3b8") for n in dist["niveau_alerte"]]
    fig = go.Figure(go.Pie(
        labels=dist["niveau_alerte"], values=dist["count"],
        hole=0.55, marker_colors=colors,
        textinfo="label+percent", textfont_size=12,
    ))
    fig.update_layout(
        title="Distribution par Niveau d'Alerte",
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font_color="#f1f5f9", showlegend=True,
        legend=dict(bgcolor="#111827"),
        margin=dict(t=50, b=20, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True)

with cc2:
    fig = px.histogram(
        df, x="score_pct", nbins=30,
        title="Distribution des Scores de Risque (%)",
        color_discrete_sequence=["#3b82f6"],
        labels={"score_pct": "Score de Risque (%)"},
    )
    fig.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0f172a",
        font_color="#f1f5f9",
        xaxis=dict(gridcolor="#1e2d4a"),
        yaxis=dict(gridcolor="#1e2d4a"),
        bargap=0.05, margin=dict(t=50, b=20),
    )
    fig.add_vline(x=40, line_dash="dot", line_color="#22c55e", annotation_text="Moyen 40%")
    fig.add_vline(x=65, line_dash="dot", line_color="#eab308", annotation_text="Élevé 65%")
    fig.add_vline(x=85, line_dash="dot", line_color="#ef4444", annotation_text="Critique 85%")
    st.plotly_chart(fig, use_container_width=True)

# ── Charts row 2 — time series ───────────────────────────────────────────────
section_header("Évolution Temporelle")
tc1, tc2 = st.columns(2)

with tc1:
    ts = df_all.groupby("PERIODE")["score_pct"].mean().reset_index()
    ts.columns = ["PERIODE", "score_moyen"]
    fig = px.line(ts, x="PERIODE", y="score_moyen",
                  title="Score Moyen du Portefeuille (historique)",
                  markers=True, color_discrete_sequence=["#3b82f6"])
    fig.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0f172a", font_color="#f1f5f9",
        xaxis=dict(gridcolor="#1e2d4a"), yaxis=dict(gridcolor="#1e2d4a"),
        margin=dict(t=50, b=20),
    )
    fig.update_traces(line_width=2)
    st.plotly_chart(fig, use_container_width=True)

with tc2:
    crit_ts = (df_all[df_all["niveau_alerte"] == "Critique"]
               .groupby("PERIODE").size().reset_index(name="critiques"))
    fig = px.bar(crit_ts, x="PERIODE", y="critiques",
                 title="Clients Critiques par Période",
                 color_discrete_sequence=["#ef4444"])
    fig.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0f172a", font_color="#f1f5f9",
        xaxis=dict(gridcolor="#1e2d4a"), yaxis=dict(gridcolor="#1e2d4a"),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Top 20 risky clients table ────────────────────────────────────────────────
section_header("Top 20 Clients les Plus Risqués")
top20 = df.sort_values("score_pct", ascending=False).head(20)
show_cols = [c for c in ["CPTE","PERIODE","score_pct","niveau_alerte",
                          "NBRJDEP","RISK_BRUT","action_recommandee"] if c in top20.columns]
top20_disp = top20[show_cols].copy()
top20_disp["PERIODE"] = top20_disp["PERIODE"].dt.strftime("%Y-%m")
if "score_pct" in top20_disp.columns:
    top20_disp["score_pct"] = top20_disp["score_pct"].apply(lambda x: f"{x:.1f}%")
if "RISK_BRUT" in top20_disp.columns:
    top20_disp["RISK_BRUT"] = top20_disp["RISK_BRUT"].apply(lambda x: f"{x:,.0f} DT")

st.dataframe(top20_disp, use_container_width=True, hide_index=True)
