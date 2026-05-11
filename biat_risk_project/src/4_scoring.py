"""
Script 4: Scoring
Loads model and scores all clients. Falls back to rule-based score if model missing.
"""
import os, warnings
import pandas as pd
import numpy as np
import joblib

try:
    import lightgbm  # noqa – ensure it's importable if available
except Exception:
    pass

warnings.filterwarnings("ignore")

ROOT       = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IN_PATH    = os.path.join(ROOT, "outputs", "modeling_data.csv")
MODEL_PATH = os.path.join(ROOT, "models", "lightgbm_model.pkl")
OUT_PATH   = os.path.join(ROOT, "outputs", "scoring_clients.csv")


def get_risk_level(score_pct: float) -> str:
    if score_pct < 40:   return "Faible"
    elif score_pct < 65: return "Moyen"
    elif score_pct < 85: return "Élevé"
    else:                return "Critique"


def get_action(niveau: str) -> str:
    return {
        "Faible":   "Aucune action urgente",
        "Moyen":    "Surveillance mensuelle",
        "Élevé":    "Appel préventif sous 48h",
        "Critique": "Intervention immédiate aujourd'hui",
    }.get(niveau, "Surveillance")


def rule_based_score(df: pd.DataFrame) -> np.ndarray:
    """Fallback scoring based on business variables."""
    score = np.zeros(len(df))
    cols = df.columns.tolist()

    if "NBRJDEP"      in cols: score += df["NBRJDEP"].clip(0, 31) / 31 * 0.30
    if "RISK_BRUT"    in cols: score += (df["RISK_BRUT"] > 0).astype(float) * 0.20
    if "AVG_DEP_3M"   in cols: score += df["AVG_DEP_3M"].clip(0, 31) / 31 * 0.20
    if "DAYS_OVD_6M"  in cols: score += df["DAYS_OVD_6M"].clip(0, 186) / 186 * 0.15
    if "MOIS_CONSEC"  in cols: score += df["MOIS_CONSEC"].clip(0, 12) / 12 * 0.10
    if "DELTA_NBRJDEP"in cols: score += (df["DELTA_NBRJDEP"].clip(-5, 10) + 5) / 15 * 0.05

    return np.clip(score, 0.0, 1.0)


def main():
    print(f"📂  Chargement : {IN_PATH}")
    df = pd.read_csv(IN_PATH, parse_dates=["PERIODE"])

    # ── Scoring ───────────────────────────────────────────────────────────────
    if os.path.exists(MODEL_PATH):
        print("  ⚡ Utilisation du modèle LightGBM entraîné...")
        artifact = joblib.load(MODEL_PATH)
        model         = artifact["model"]
        feature_cols  = artifact["feature_columns"]
        threshold     = artifact["threshold"]
        cat_cols      = artifact["categorical_cols"]
        num_cols      = artifact["numeric_cols"]

        X_num = df[[c for c in num_cols if c in df.columns]].fillna(0)
        X_cat = pd.get_dummies(df[[c for c in cat_cols if c in df.columns]], drop_first=True)
        X = pd.concat([X_num, X_cat], axis=1)
        X = X.reindex(columns=feature_cols, fill_value=0)

        scores = model.predict_proba(X)[:, 1]
    else:
        print("  ⚠️  Modèle introuvable → score basé sur les règles métier")
        threshold = 0.65
        scores = rule_based_score(df)

    # ── Build output ──────────────────────────────────────────────────────────
    out = df[["PERIODE","CPTE"]].copy()
    out["score_risque"] = scores.round(4)
    out["score_pct"]    = (scores * 100).round(1)
    out["niveau_alerte"]= out["score_pct"].apply(get_risk_level)
    out["action_recommandee"] = out["niveau_alerte"].apply(get_action)

    # Keep contextual columns
    for col in ["NBRJDEP","NBRJDEB","RISK_BRUT","MVT","NET_MONTHLY","AGE",
                "AVG_DEP_3M","DAYS_OVD_6M","REV_VARIANCE",
                "NBRJDEP_LAG1","DELTA_NBRJDEP","MOIS_CONSEC",
                "GENDER","SECTOR","MARITAL_STATUS","EMPLOYMENT_STATUS","POST_CODE"]:
        if col in df.columns:
            out[col] = df[col].values

    out.sort_values(["PERIODE","score_pct"], ascending=[True, False], inplace=True)
    out.reset_index(drop=True, inplace=True)
    out.to_csv(OUT_PATH, index=False)

    # ── Diagnostics ───────────────────────────────────────────────────────────
    latest = out[out["PERIODE"] == out["PERIODE"].max()]
    print(f"\n{'='*55}")
    print(f"  ✅  SCORING TERMINÉ")
    print(f"{'='*55}")
    print(f"  Total lignes scorées   : {len(out):,}")
    print(f"  Dernière période       : {out['PERIODE'].max().date()}")
    print(f"  Clients (der. période) : {len(latest):,}")
    print(f"  Distribution alertes   :\n{latest['niveau_alerte'].value_counts()}")
    print(f"  Score moyen (der. per) : {latest['score_pct'].mean():.1f}%")
    print(f"  Fichier de sortie      : {OUT_PATH}")

if __name__ == "__main__":
    main()
