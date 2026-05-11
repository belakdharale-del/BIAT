"""
Centralized data loading for BIAT Risk Monitor.
All file I/O and current-period filtering is handled here.
"""
import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs"))

FILE_PATHS = {
    "scoring_clients":   os.path.join(BASE_DIR, "scoring_clients.csv"),
    "scoring_evolution": os.path.join(BASE_DIR, "scoring_evolution.csv"),
    "clients_a_notifier": os.path.join(BASE_DIR, "clients_a_notifier.csv"),
    "model_comparison":  os.path.join(BASE_DIR, "model_comparison.csv"),
}

SCRIPT_HINTS = {
    "scoring_clients":    "python src/4_scoring.py",
    "scoring_evolution":  "python src/5_build_evolution.py",
    "clients_a_notifier": "python src/5_build_evolution.py",
    "model_comparison":   "python src/3_train_models.py",
}


def require_file(path: str, script_hint: str):
    if not os.path.exists(path):
        st.warning(f"⚠️ Fichier introuvable : `{os.path.basename(path)}`  \n👉 Lancez : `{script_hint}`")
        st.stop()


@st.cache_data(ttl=300)
def load_scoring_clients() -> pd.DataFrame:
    path = FILE_PATHS["scoring_clients"]
    require_file(path, SCRIPT_HINTS["scoring_clients"])
    df = pd.read_csv(path, parse_dates=["PERIODE"])
    return df


@st.cache_data(ttl=300)
def load_scoring_evolution() -> pd.DataFrame:
    path = FILE_PATHS["scoring_evolution"]
    require_file(path, SCRIPT_HINTS["scoring_evolution"])
    df = pd.read_csv(path, parse_dates=["PERIODE"])
    return df


@st.cache_data(ttl=300)
def load_clients_to_notify() -> pd.DataFrame:
    path = FILE_PATHS["clients_a_notifier"]
    require_file(path, SCRIPT_HINTS["clients_a_notifier"])
    df = pd.read_csv(path, parse_dates=["PERIODE"])
    return df


@st.cache_data(ttl=300)
def load_model_comparison() -> pd.DataFrame:
    path = FILE_PATHS["model_comparison"]
    if not os.path.exists(path):
        return pd.DataFrame({
            "Modèle": ["LightGBM", "Random Forest", "Régression Logistique"],
            "Accuracy": [0.9736, 0.9759, 0.9750],
            "Recall": [0.9372, 0.9314, 0.9072],
            "Precision": [0.9530, 0.9676, 0.9851],
            "F1-score": [0.9450, 0.9493, 0.9461],
            "ROC-AUC": [0.9889, 0.9903, 0.9684],
        })
    df = pd.read_csv(path)
    return df


def get_current_period_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    max_period = df["PERIODE"].max()
    return df[df["PERIODE"] == max_period].copy()


def detect_client_column(df: pd.DataFrame) -> str:
    for col in ["CPTE", "cpte", "client_id", "CLIENT_ID", "ID"]:
        if col in df.columns:
            return col
    return df.columns[0]
