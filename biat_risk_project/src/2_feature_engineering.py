"""
Script 2: Feature Engineering
Creates target variable and behavioral features from prepared_data.csv
"""
import os
import pandas as pd
import numpy as np

ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IN_PATH = os.path.join(ROOT, "outputs", "prepared_data.csv")
OUT_PATH= os.path.join(ROOT, "outputs", "modeling_data.csv")


def consec_months_in_overdraft(series: pd.Series) -> pd.Series:
    """Number of consecutive months with NBRJDEP > 0 (rolling)."""
    result = []
    count = 0
    for val in series:
        if val > 0:
            count += 1
        else:
            count = 0
        result.append(count)
    return pd.Series(result, index=series.index)


def main():
    print(f"📂  Chargement : {IN_PATH}")
    df = pd.read_csv(IN_PATH, parse_dates=["PERIODE"])
    df.sort_values(["CPTE", "PERIODE"], inplace=True)

    g = df.groupby("CPTE")

    # ── Target variable ──────────────────────────────────────────────────────
    df["NBRJDEP_NEXT"]   = g["NBRJDEP"].shift(-1)
    df["RISK_BRUT_NEXT"] = g["RISK_BRUT"].shift(-1)

    df["target"] = (
        (df["NBRJDEP_NEXT"] > 3) | (df["RISK_BRUT_NEXT"] > 0)
    ).astype(int)

    # Remove last observation per client (no next month)
    last_idx = g["PERIODE"].transform("max")
    df = df[df["PERIODE"] != last_idx].copy()
    df.drop(columns=["NBRJDEP_NEXT", "RISK_BRUT_NEXT"], inplace=True)

    # Re-group after filtering
    g = df.groupby("CPTE")

    # ── Feature engineering ──────────────────────────────────────────────────
    # 1. AVG_DEP_3M
    df["AVG_DEP_3M"] = (
        g["NBRJDEP"].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    ).round(2)

    # 2. DAYS_OVD_6M
    df["DAYS_OVD_6M"] = (
        g["NBRJDEP"].transform(lambda x: x.shift(1).rolling(6, min_periods=1).sum())
    ).round(2)

    # 3. REV_VARIANCE
    df["REV_VARIANCE"] = (
        g["MVT"].transform(lambda x: x.shift(1).rolling(3, min_periods=1).std())
    ).round(2)

    # 4. NBRJDEP_LAG1
    df["NBRJDEP_LAG1"] = g["NBRJDEP"].shift(1).fillna(0)

    # 5. DELTA_NBRJDEP
    df["DELTA_NBRJDEP"] = (df["NBRJDEP"] - df["NBRJDEP_LAG1"]).round(2)

    # 6. MOIS_CONSEC
    df["MOIS_CONSEC"] = g["NBRJDEP"].transform(consec_months_in_overdraft)

    # Fill NaN in engineered features
    for col in ["AVG_DEP_3M", "DAYS_OVD_6M", "REV_VARIANCE"]:
        df[col] = df[col].fillna(0)

    # ── Final column selection ────────────────────────────────────────────────
    id_cols   = ["PERIODE", "CPTE"]
    target    = ["target"]
    raw_feats = ["NBRJDEP", "NBRJDEB", "RISK_BRUT", "MVT", "NET_MONTHLY", "AGE"]
    eng_feats = ["AVG_DEP_3M", "DAYS_OVD_6M", "REV_VARIANCE",
                 "NBRJDEP_LAG1", "DELTA_NBRJDEP", "MOIS_CONSEC"]
    cat_feats = ["GENDER", "SECTOR", "MARITAL_STATUS", "EMPLOYMENT_STATUS", "POST_CODE"]

    keep = id_cols + target + raw_feats + eng_feats + cat_feats
    keep = [c for c in keep if c in df.columns]
    df = df[keep]

    df.to_csv(OUT_PATH, index=False)

    # ── Diagnostics ──────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  ✅  FEATURE ENGINEERING TERMINÉ")
    print(f"{'='*55}")
    print(f"  Distribution cible :\n{df['target'].value_counts()}")
    print(f"  Proportion risqué   : {df['target'].mean()*100:.1f}%")
    print(f"  Colonnes finales    : {list(df.columns)}")
    print(f"  Valeurs manquantes  :\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"  Fichier de sortie   : {OUT_PATH}")

if __name__ == "__main__":
    main()
