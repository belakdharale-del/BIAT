"""
Page 6: Assistant BIAT Risk
Rule-based chatbot using portfolio CSV data — no external API.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Assistant BIAT Risk | BIAT", page_icon="🤖", layout="wide")

from app.utils.style import apply_global_style, page_header, section_header
from app.utils.data_loader import (load_scoring_clients, load_scoring_evolution,
                                    load_clients_to_notify, get_current_period_data)
from app.utils.business_rules import explain_risk, format_number

apply_global_style()

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_all_data():
    sc  = load_scoring_clients()
    evo = load_scoring_evolution()
    try:
        notif = load_clients_to_notify()
    except Exception:
        notif = pd.DataFrame()
    return sc, evo, notif

df_sc, df_evo, df_notif = get_all_data()
cur = get_current_period_data(df_sc)
latest_period = df_sc["PERIODE"].max()
prev_period   = df_sc["PERIODE"].unique()
prev_period   = sorted(prev_period)[-2] if len(prev_period) >= 2 else latest_period
prev          = df_sc[df_sc["PERIODE"] == prev_period]

page_header("🤖", "Assistant BIAT Risk",
            "Assistant métier basé sur les données du portefeuille — Aucune API externe")

# ── Layout ────────────────────────────────────────────────────────────────────
main_col, sidebar_col = st.columns([3, 1])

# ── Sidebar: priority actions ─────────────────────────────────────────────────
with sidebar_col:
    section_header("⚡ Actions Prioritaires")
    n_p1 = int((df_notif.get("priorite_intervention", pd.Series([])) == "Priorité 1").sum()) \
           if "priorite_intervention" in df_notif.columns else 0
    n_crit = int((cur["niveau_alerte"] == "Critique").sum())
    n_eleve= int((cur["niveau_alerte"] == "Élevé").sum())
    avg_sc = cur["score_pct"].mean()

    st.markdown(f"""
    <div class="info-box">
        <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; margin-bottom:8px;">
            Période : {latest_period.strftime("%B %Y")}
        </div>
        <div style="margin:6px 0;"><span style="color:#ef4444;font-weight:700;">🔴 Critique :</span> {n_crit}</div>
        <div style="margin:6px 0;"><span style="color:#f97316;font-weight:700;">🟠 Élevé :</span> {n_eleve}</div>
        <div style="margin:6px 0;"><span style="color:#ef4444;font-weight:700;">⚡ Priorité 1 :</span> {n_p1}</div>
        <div style="margin:6px 0;"><span style="color:#94a3b8;">📊 Score moyen :</span> {avg_sc:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    section_header("💡 Questions Suggérées", margin_top="20px")
    suggestions = [
        "Comment évolue le risque global ?",
        "Quels sont les clients prioritaires ?",
        "Que dois-je faire cette semaine ?",
        "Les nouveaux clients sont-ils plus risqués ?",
        "Si j'abaisse le seuil critique à 80% ?",
    ]
    for s in suggestions:
        if st.button(s, key=f"btn_{s[:20]}", use_container_width=True):
            st.session_state.setdefault("chat_history", [])
            st.session_state["pending_question"] = s

    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()

# ── Chat logic ─────────────────────────────────────────────────────────────────
def generate_response(question: str) -> str:
    q = question.lower()

    # 1. Portfolio evolution
    if any(w in q for w in ["évolution","evolution","global","portefeuille","risque global"]):
        cur_crit  = int((cur["niveau_alerte"] == "Critique").sum())
        prev_crit = int((prev["niveau_alerte"] == "Critique").sum())
        delta     = cur_crit - prev_crit
        trend     = "📈 En hausse" if delta > 0 else ("📉 En baisse" if delta < 0 else "➡️ Stable")
        interp    = "situation en dégradation" if delta > 0 else ("amélioration observée" if delta < 0 else "situation stable")
        return (
            f"**📊 Évolution du portefeuille — {latest_period.strftime('%B %Y')}**\n\n"
            f"- Clients scorés : **{len(cur):,}**\n"
            f"- Score moyen : **{cur['score_pct'].mean():.1f}%**\n"
            f"- Clients critiques : **{cur_crit}** ({trend} vs période précédente : {prev_crit})\n"
            f"- Variation : **{'+' if delta>=0 else ''}{delta}** clients critiques\n\n"
            f"🔍 Interprétation : {interp.capitalize()}. "
            f"{'Des actions immédiates sont recommandées.' if delta > 0 else 'Continuez le suivi régulier.'}"
        )

    # 2. Priority clients / action plan
    if any(w in q for w in ["prioritaire","action","faire","semaine","contacter","appeler","urgence"]):
        n_p1   = int((df_notif.get("priorite_intervention","") == "Priorité 1").sum()) \
                 if "priorite_intervention" in df_notif.columns else n_crit
        n_crit_= int((cur["niveau_alerte"] == "Critique").sum())
        n_eleve_= int((cur["niveau_alerte"] == "Élevé").sum())
        return (
            f"**⚡ Plan d'action recommandé — Cette semaine**\n\n"
            f"1. 🔴 **Priorité 1** ({n_p1} clients) — Intervention immédiate aujourd'hui\n"
            f"2. 🔴 **Clients Critiques** ({n_crit_} total) — Appel dans les 24h\n"
            f"3. 🟠 **Clients Élevés** ({n_eleve_}) — Appel préventif sous 48h\n\n"
            f"💡 Commencez par les clients Priorité 1 (score ≥ 95%), "
            f"puis traitez les autres critiques par score décroissant."
        )

    # 3. Specific client lookup
    cpte_match = re.search(r"cpte[_\s]?(\d{5,6})", q)
    if cpte_match:
        cpte_id = f"CPTE_{cpte_match.group(1).zfill(6)}"
        client_data = cur[cur["CPTE"] == cpte_id]
        if client_data.empty:
            client_data = df_sc[df_sc["CPTE"] == cpte_id].sort_values("PERIODE")
            if client_data.empty:
                return f"❌ Aucun client trouvé pour **{cpte_id}**. Vérifiez l'identifiant."
        row = client_data.iloc[-1]
        evo_row = df_evo[df_evo["CPTE"] == cpte_id].sort_values("PERIODE")
        evol = evo_row.iloc[-1].get("evolution","—") if not evo_row.empty else "—"
        reasons = explain_risk(row.to_dict())
        reasons_text = "\n".join([f"   - {r}" for r in reasons])
        return (
            f"**👤 Fiche Client : {cpte_id}**\n\n"
            f"- Score de risque : **{row.get('score_pct',0):.1f}%**\n"
            f"- Niveau d'alerte : **{row.get('niveau_alerte','—')}**\n"
            f"- Jours découvert : **{int(row.get('NBRJDEP',0))}**\n"
            f"- Risque brut : **{format_number(row.get('RISK_BRUT',0))} DT**\n"
            f"- Évolution : **{evol}**\n"
            f"- Action : **{row.get('action_recommandee','—')}**\n\n"
            f"📋 Facteurs de risque :\n{reasons_text}"
        )

    # 4. New clients
    if any(w in q for w in ["nouveau","nouveaux","new"]):
        new_clients = cur_evo = df_evo[
            (df_evo["PERIODE"] == latest_period) & (df_evo["evolution"] == "Nouveau client")
        ] if not df_evo.empty else pd.DataFrame()
        n_new   = len(new_clients)
        n_new_c = int((new_clients["niveau_alerte"] == "Critique").sum()) if not new_clients.empty else 0
        pct = (n_new_c / n_new * 100) if n_new > 0 else 0
        return (
            f"**🆕 Nouveaux Clients — {latest_period.strftime('%B %Y')}**\n\n"
            f"- Nombre de nouveaux clients : **{n_new}**\n"
            f"- Dont critiques : **{n_new_c}** ({pct:.1f}%)\n\n"
            f"{'⚠️ Vigilance requise : proportion de critiques élevée parmi les nouveaux clients.' if pct > 20 else '✅ Profil risque des nouveaux clients dans les limites normales.'}"
        )

    # 5. Threshold simulation
    if any(w in q for w in ["seuil","80","80%"]):
        cur_crit_85 = int((cur["score_pct"] >= 85).sum())
        sim_crit_80 = int((cur["score_pct"] >= 80).sum())
        additional  = sim_crit_80 - cur_crit_85
        return (
            f"**⚙️ Simulation — Seuil Critique à 80%**\n\n"
            f"- Clients critiques actuels (seuil 85%) : **{cur_crit_85}**\n"
            f"- Clients critiques simulés (seuil 80%) : **{sim_crit_80}**\n"
            f"- Clients supplémentaires : **+{additional}**\n\n"
            f"💡 Abaisser le seuil à 80% augmenterait la charge de travail de "
            f"**{additional / max(cur_crit_85,1)*100:.0f}%** mais permettrait de capturer "
            f"des clients au comportement dégradé avant qu'ils n'atteignent 85%."
        )

    # Default
    return (
        f"**🤖 Assistant BIAT Risk**\n\n"
        f"Je peux répondre aux questions suivantes :\n\n"
        f"- 📊 *Comment évolue le risque global ?*\n"
        f"- ⚡ *Quels sont les clients prioritaires ?*\n"
        f"- 📅 *Que dois-je faire cette semaine ?*\n"
        f"- 👤 *Analyse le client CPTE_000362*\n"
        f"- 🆕 *Les nouveaux clients sont-ils plus risqués ?*\n"
        f"- ⚙️ *Si j'abaisse le seuil critique à 80% ?*\n\n"
        f"Posez votre question ou cliquez sur une suggestion."
    )

# ── Chat interface ────────────────────────────────────────────────────────────
with main_col:
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Render history
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-bot">
                <div class="chat-bot-header">🤖 Assistant BIAT Risk</div>
                {msg["content"].replace(chr(10), "<br>")}
            </div>
            """, unsafe_allow_html=True)

    # Handle pending question from suggestion button
    pending = st.session_state.pop("pending_question", None)

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Posez votre question...",
            value=pending or "",
            placeholder="Ex: Quels sont les clients prioritaires ?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Envoyer ➤", use_container_width=False)

    if submitted and user_input.strip():
        question = user_input.strip()
        response = generate_response(question)
        st.session_state["chat_history"].append({"role": "user", "content": question})
        st.session_state["chat_history"].append({"role": "bot",  "content": response})
        st.rerun()

    if not st.session_state["chat_history"]:
        st.markdown("""
        <div class="info-box" style="text-align:center; padding:30px;">
            <div style="font-size:2rem; margin-bottom:10px;">🤖</div>
            <div style="font-weight:600; font-size:1rem;">Bienvenue dans l'Assistant BIAT Risk</div>
            <div style="color:#64748b; font-size:0.85rem; margin-top:6px;">
                Posez une question ou cliquez sur une suggestion dans le panneau de droite.
            </div>
        </div>
        """, unsafe_allow_html=True)
