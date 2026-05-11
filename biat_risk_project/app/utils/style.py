"""
Style utilities for BIAT Risk Monitor Streamlit application.
Professional banking dark theme.
"""
import streamlit as st


def apply_global_style():
    st.markdown("""
    <style>
    /* ── Global resets ── */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #f1f5f9;
    }
    .main { background-color: #0a0f1e; }
    section[data-testid="stSidebar"] {
        background-color: #0d1424;
        border-right: 1px solid #1e2d4a;
    }
    section[data-testid="stSidebar"] .css-1d391kg { padding-top: 1rem; }

    /* ── KPI Cards ── */
    .kpi-card {
        background: linear-gradient(135deg, #111827 0%, #1a2540 100%);
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 18px 22px;
        text-align: center;
        margin: 4px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.4);
        transition: transform 0.15s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-title {
        font-size: 0.72rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .kpi-subtitle {
        font-size: 0.7rem;
        color: #64748b;
        margin-top: 4px;
    }
    .kpi-card.green  { border-left: 4px solid #22c55e; }
    .kpi-card.yellow { border-left: 4px solid #eab308; }
    .kpi-card.orange { border-left: 4px solid #f97316; }
    .kpi-card.red    { border-left: 4px solid #ef4444; }
    .kpi-card.blue   { border-left: 4px solid #3b82f6; }
    .kpi-card.purple { border-left: 4px solid #a855f7; }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.05rem;
        font-weight: 600;
        color: #e2e8f0;
        border-left: 3px solid #3b82f6;
        padding-left: 10px;
        margin-bottom: 12px;
    }

    /* ── Page header ── */
    .page-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
        border: 1px solid #1e3a5f;
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
    }
    .page-header-icon { font-size: 2rem; margin-bottom: 6px; }
    .page-header-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
    }
    .page-header-subtitle {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* ── Alert badges ── */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.73rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-faible   { background: #14532d; color: #86efac; }
    .badge-moyen    { background: #422006; color: #fde68a; }
    .badge-eleve    { background: #431407; color: #fdba74; }
    .badge-critique { background: #450a0a; color: #fca5a5; }

    /* ── Chat bubbles ── */
    .chat-user {
        background: #1e3a5f;
        border-radius: 12px 12px 2px 12px;
        padding: 10px 14px;
        margin: 8px 0;
        margin-left: 20%;
        color: #e2e8f0;
        font-size: 0.9rem;
    }
    .chat-bot {
        background: #111827;
        border: 1px solid #1e2d4a;
        border-radius: 12px 12px 12px 2px;
        padding: 12px 16px;
        margin: 8px 0;
        margin-right: 10%;
        color: #f1f5f9;
        font-size: 0.88rem;
    }
    .chat-bot-header {
        font-size: 0.72rem;
        color: #3b82f6;
        font-weight: 600;
        margin-bottom: 6px;
        text-transform: uppercase;
    }

    /* ── Info box ── */
    .info-box {
        background: #0f2037;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 10px 0;
        font-size: 0.85rem;
        color: #cbd5e1;
    }
    .action-box {
        border-radius: 10px;
        padding: 14px 18px;
        margin: 10px 0;
        font-weight: 600;
        font-size: 0.92rem;
    }
    .action-faible   { background: #052e16; border: 1px solid #16a34a; color: #86efac; }
    .action-moyen    { background: #1c1402; border: 1px solid #ca8a04; color: #fde68a; }
    .action-eleve    { background: #1c0a00; border: 1px solid #ea580c; color: #fdba74; }
    .action-critique { background: #1c0000; border: 1px solid #dc2626; color: #fca5a5; }

    /* ── Dataframe overrides ── */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* ── Divider ── */
    hr { border-color: #1e2d4a; margin: 20px 0; }

    /* ── Hide default streamlit elements ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


def get_color_palette():
    return {
        "faible": "#22c55e",
        "moyen": "#eab308",
        "eleve": "#f97316",
        "critique": "#ef4444",
        "blue": "#3b82f6",
        "purple": "#a855f7",
        "bg": "#0a0f1e",
        "card": "#111827",
        "border": "#1e2d4a",
        "text": "#f1f5f9",
        "muted": "#94a3b8",
    }


def page_header(icon: str, title: str, subtitle: str):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-icon">{icon}</div>
        <div class="page-header-title">{title}</div>
        <div class="page-header-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, margin_top: str = "24px"):
    st.markdown(f"""
    <div class="section-header" style="margin-top:{margin_top}">
        {title}
    </div>
    """, unsafe_allow_html=True)


def kpi_card(title: str, value, color: str = "blue", subtitle: str = "", klass: str = ""):
    extra = klass if klass else color
    st.markdown(f"""
    <div class="kpi-card {extra}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value" style="color:{_resolve_color(color)}">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def _resolve_color(c: str) -> str:
    palette = get_color_palette()
    return palette.get(c, c)
