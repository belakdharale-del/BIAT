"""
Page 2: Évolution du Risque
Behavioral monitoring and transition analysis.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Évolution du Risque | BIAT", page_icon="📈", layout="wide")

from app.utils.style import apply_global_style, page_header, kpi_card, section_header
from app.utils.data_loader import load_scoring_evolution
from app.utils.business_rules import ALERT_COLORS

apply_global_style()

# ── Load ──────────────────────────────────────────────────────────────────────
df_all = load_scoring_evolution()
periods = sorted(df_all["PERIODE"].unique())
period_labels = [p.strftime("%Y-%m") for p in periods]

page_header("📈", "Évolution du Risque",
            "Suivi des transitions mensuelles et tendances comportementales du portefeuille")

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filtres")
    min_p, max_p = period_labels[0], period_labels[-1]
    sel_start = st.selectbox("Début de période", period_labels, index=0)
    sel_end   = st.selectbox("Fin de période",   period_labels[::-1], index=0)
    sel_evo   = st.multiselect("Évolution",
                               ["Aggravation","Amélioration","Stable","Nouveau client"],
                               default=["Aggravation","Amélioration","Stable","Nouveau client"])
    sel_niv   = st.multiselect("Niveau d'alerte",
                               ["Faible","Moyen","Élevé","Critique"],
                               default=["Faible","Moyen","Élevé","Critique"])

start_ts = pd.Timestamp(sel_start + "-01")
end_ts   = pd.Timestamp(sel_end   + "-01")
df = df_all[
    (df_all["PERIODE"] >= start_ts) &
    (df_all["PERIODE"] <= end_ts)
].copy()
if sel_evo:  df = df[df["evolution"].isin(sel_evo)]
if sel_niv:  df = df[df["niveau_alerte"].isin(sel_niv)]

# ── KPIs (latest period) ──────────────────────────────────────────────────────
latest_period = df_all["PERIODE"].max()
cur = df_all[df_all["PERIODE"] == latest_period]

n_aggrav = int((cur["evolution"] == "Aggravation").sum())
n_amel   = int((cur["evolution"] == "Amélioration").sum())
n_stable = int((cur["evolution"] == "Stable").sum())
n_new    = int((cur["evolution"] == "Nouveau client").sum())
n_total  = len(cur)

c1,c2,c3,c4,c5 = st.columns(5)
with c1: kpi_card("Aggravation",    f"{n_aggrav:,}",  "red",    "Comportement dégradé")
with c2: kpi_card("Amélioration",   f"{n_amel:,}",   "green",  "Comportement amélioré")
with c3: kpi_card("Stable",         f"{n_stable:,}", "blue",   "Sans changement")
with c4: kpi_card("Nouveaux Clients",f"{n_new:,}",   "purple", "Première observation")
with c5: kpi_card("Total Transitions",f"{n_total:,}","yellow", latest_period.strftime("%Y-%m"))

st.markdown("<hr>", unsafe_allow_html=True)

# ── Charts row 1 ──────────────────────────────────────────────────────────────
section_header("Distribution des Évolutions")
rc1, rc2 = st.columns(2)

with rc1:
    evo_colors = {
        "Aggravation": "#ef4444", "Amélioration": "#22c55e",
        "Stable": "#3b82f6", "Nouveau client": "#a855f7"
    }
    evo_dist = cur["evolution"].value_counts().reset_index()
    evo_dist.columns = ["evolution","count"]
    colors = [evo_colors.get(e, "#94a3b8") for e in evo_dist["evolution"]]
    fig = go.Figure(go.Pie(
        labels=evo_dist["evolution"], values=evo_dist["count"],
        hole=0.55, marker_colors=colors,
        textinfo="label+percent", textfont_size=12,
    ))
    fig.update_layout(
        title="Répartition par Catégorie d'Évolution",
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font_color="#f1f5f9", showlegend=True,
        legend=dict(bgcolor="#111827"),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with rc2:
    top_trans = (df["transition"].value_counts()
                   .head(10).reset_index())
    top_trans.columns = ["transition","count"]
    fig = px.bar(top_trans, x="count", y="transition",
                 orientation="h",
                 title="Top 10 Transitions Observées",
                 color_discrete_sequence=["#3b82f6"])
    fig.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0f172a", font_color="#f1f5f9",
        xaxis=dict(gridcolor="#1e2d4a"), yaxis=dict(gridcolor="#1e2d4a", autorange="reversed"),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Charts row 2 — time series ────────────────────────────────────────────────
section_header("Tendances Temporelles")
tc1, tc2 = st.columns(2)

with tc1:
    crit_ts = (df_all[df_all["niveau_alerte"] == "Critique"]
               .groupby("PERIODE").size().reset_index(name="critiques"))
    fig = px.line(crit_ts, x="PERIODE", y="critiques",
                  title="Clients Critiques par Période", markers=True,
                  color_discrete_sequence=["#ef4444"])
    fig.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0f172a", font_color="#f1f5f9",
        xaxis=dict(gridcolor="#1e2d4a"), yaxis=dict(gridcolor="#1e2d4a"),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with tc2:
    avg_ts = df_all.groupby("PERIODE")["score_pct"].mean().reset_index()
    avg_ts.columns = ["PERIODE", "score_moyen"]
    fig = px.line(avg_ts, x="PERIODE", y="score_moyen",
                  title="Score Moyen du Portefeuille", markers=True,
                  color_discrete_sequence=["#a855f7"])
    fig.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0f172a", font_color="#f1f5f9",
        xaxis=dict(gridcolor="#1e2d4a"), yaxis=dict(gridcolor="#1e2d4a"),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Table ─────────────────────────────────────────────────────────────────────
section_header("Détail des Transitions")
show = [c for c in ["CPTE","PERIODE","niveau_precedent","niveau_alerte",
                     "transition","evolution","score_pct"] if c in df.columns]
disp = df[show].copy().sort_values("score_pct", ascending=False).head(200)
if "PERIODE" in disp.columns:
    disp["PERIODE"] = disp["PERIODE"].dt.strftime("%Y-%m")
if "score_pct" in disp.columns:
    disp["score_pct"] = disp["score_pct"].apply(lambda x: f"{x:.1f}%")
st.dataframe(disp, use_container_width=True, hide_index=True)

st.markdown("""
<div class="info-box" style="margin-top:16px;">
Cette page identifie les clients dont le comportement s'aggrave, s'améliore, reste stable
ou apparaît pour la première fois dans le portefeuille, permettant un suivi proactif ciblé.
</div>
""", unsafe_allow_html=True)
