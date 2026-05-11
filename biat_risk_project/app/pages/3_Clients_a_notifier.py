"""
Page 3: Clients à Notifier
Operational prioritized list for account managers with CSV export.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Clients à Notifier | BIAT", page_icon="🔔", layout="wide")

from app.utils.style import apply_global_style, page_header, kpi_card, section_header
from app.utils.data_loader import load_clients_to_notify
from app.utils.business_rules import ALERT_COLORS, format_number

apply_global_style()

# ── Load ──────────────────────────────────────────────────────────────────────
df = load_clients_to_notify()

page_header("🔔", "Clients à Notifier",
            "Liste opérationnelle priorisée — Dernière période — Intervention requise")

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filtres")
    search_cpte = st.text_input("Rechercher CPTE", "")
    sel_niveaux = st.multiselect("Niveau d'alerte",
                                 ["Moyen","Élevé","Critique"],
                                 default=["Moyen","Élevé","Critique"])
    priorities = sorted(df["priorite_intervention"].unique()) if "priorite_intervention" in df.columns else []
    sel_prio = st.multiselect("Priorité", priorities, default=priorities)
    sel_score_min = st.slider("Score minimum (%)", 0, 100, 0, 5)
    statuts = sorted(df["statut_suivi"].unique()) if "statut_suivi" in df.columns else ["À contacter"]
    sel_statut = st.multiselect("Statut suivi", statuts, default=statuts)

# ── Filter ─────────────────────────────────────────────────────────────────────
dff = df.copy()
if search_cpte:
    dff = dff[dff["CPTE"].str.contains(search_cpte.upper(), na=False)]
if sel_niveaux:
    dff = dff[dff["niveau_alerte"].isin(sel_niveaux)]
if sel_prio and "priorite_intervention" in dff.columns:
    dff = dff[dff["priorite_intervention"].isin(sel_prio)]
if sel_statut and "statut_suivi" in dff.columns:
    dff = dff[dff["statut_suivi"].isin(sel_statut)]
dff = dff[dff["score_pct"] >= sel_score_min]

# ── KPIs ──────────────────────────────────────────────────────────────────────
n_crit  = int((dff["niveau_alerte"] == "Critique").sum())
n_eleve = int((dff["niveau_alerte"] == "Élevé").sum())
n_moyen = int((dff["niveau_alerte"] == "Moyen").sum())
n_prio1 = int((dff.get("priorite_intervention", pd.Series([])) == "Priorité 1").sum()) \
          if "priorite_intervention" in dff.columns else 0
n_total = len(dff)

c1,c2,c3,c4,c5 = st.columns(5)
with c1: kpi_card("Clients Critiques", f"{n_crit:,}",  "red",    "Intervention immédiate")
with c2: kpi_card("Clients Élevés",   f"{n_eleve:,}", "orange", "Appel sous 48h")
with c3: kpi_card("Clients Moyens",   f"{n_moyen:,}", "yellow", "Surveillance renforcée")
with c4: kpi_card("Priorité 1",       f"{n_prio1:,}", "red",    "Score ≥ 95%")
with c5: kpi_card("Total à Traiter",  f"{n_total:,}", "blue",   "Tous niveaux confondus")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
section_header("Analyse de la Liste de Notification")
ch1, ch2 = st.columns(2)

with ch1:
    dist = dff["niveau_alerte"].value_counts().reset_index()
    dist.columns = ["niveau","count"]
    colors = [ALERT_COLORS.get(n, "#94a3b8") for n in dist["niveau"]]
    fig = go.Figure(go.Pie(labels=dist["niveau"], values=dist["count"],
                           hole=0.55, marker_colors=colors,
                           textinfo="label+percent"))
    fig.update_layout(title="Par Niveau d'Alerte",
                      paper_bgcolor="#111827", plot_bgcolor="#111827",
                      font_color="#f1f5f9", margin=dict(t=50,b=20))
    st.plotly_chart(fig, use_container_width=True)

with ch2:
    if "priorite_intervention" in dff.columns:
        prio_dist = dff["priorite_intervention"].value_counts().reset_index()
        prio_dist.columns = ["priorite","count"]
        prio_colors = {"Priorité 1":"#ef4444","Priorité 2":"#f97316",
                       "Priorité 3":"#eab308","Priorité 4":"#22c55e",
                       "Priorité 5":"#3b82f6","Surveillance":"#64748b"}
        colors_p = [prio_colors.get(p,"#94a3b8") for p in prio_dist["priorite"]]
        fig = px.bar(prio_dist, x="priorite", y="count",
                     title="Répartition par Priorité d'Intervention",
                     color="priorite",
                     color_discrete_map=prio_colors)
        fig.update_layout(paper_bgcolor="#111827", plot_bgcolor="#0f172a",
                          font_color="#f1f5f9", showlegend=False,
                          xaxis=dict(gridcolor="#1e2d4a"),
                          yaxis=dict(gridcolor="#1e2d4a"),
                          margin=dict(t=50,b=20))
        st.plotly_chart(fig, use_container_width=True)

# ── Score histogram ───────────────────────────────────────────────────────────
ch3, ch4 = st.columns(2)
with ch3:
    fig = px.histogram(dff, x="score_pct", nbins=25,
                       title="Distribution des Scores",
                       color_discrete_sequence=["#f97316"])
    fig.update_layout(paper_bgcolor="#111827", plot_bgcolor="#0f172a",
                      font_color="#f1f5f9",
                      xaxis=dict(gridcolor="#1e2d4a"),
                      yaxis=dict(gridcolor="#1e2d4a"),
                      margin=dict(t=50,b=20))
    st.plotly_chart(fig, use_container_width=True)

with ch4:
    if "action_recommandee" in dff.columns:
        act = dff["action_recommandee"].value_counts().reset_index()
        act.columns = ["action","count"]
        fig = px.bar(act, x="count", y="action", orientation="h",
                     title="Actions Recommandées",
                     color_discrete_sequence=["#3b82f6"])
        fig.update_layout(paper_bgcolor="#111827", plot_bgcolor="#0f172a",
                          font_color="#f1f5f9",
                          xaxis=dict(gridcolor="#1e2d4a"),
                          yaxis=dict(gridcolor="#1e2d4a", autorange="reversed"),
                          margin=dict(t=50,b=20))
        st.plotly_chart(fig, use_container_width=True)

# ── Main table ─────────────────────────────────────────────────────────────────
section_header("Liste Opérationnelle Priorisée")

table_cols = [c for c in ["CPTE","PERIODE","score_pct","niveau_alerte","evolution",
                           "NBRJDEP","RISK_BRUT","priorite_intervention",
                           "action_recommandee","statut_suivi"] if c in dff.columns]
disp = dff[table_cols].copy()
if "PERIODE" in disp.columns:
    disp["PERIODE"] = disp["PERIODE"].dt.strftime("%Y-%m")
if "score_pct" in disp.columns:
    disp["score_pct"] = disp["score_pct"].apply(lambda x: f"{x:.1f}%")
if "RISK_BRUT" in disp.columns:
    disp["RISK_BRUT"] = disp["RISK_BRUT"].apply(lambda x: f"{x:,.0f} DT")

st.dataframe(disp, use_container_width=True, hide_index=True, height=400)

# ── Download ──────────────────────────────────────────────────────────────────
csv_data = dff[table_cols].to_csv(index=False)
st.download_button(
    label="⬇️  Télécharger clients_a_notifier_priorises.csv",
    data=csv_data,
    file_name="clients_a_notifier_priorises.csv",
    mime="text/csv",
)
