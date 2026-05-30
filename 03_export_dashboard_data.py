# 05_export_anomaly_app_data.py
# BIAT Risk Monitor — Export Anomaly Detection results to dashboard JSON
#
# Usage:
#   python 05_export_anomaly_app_data.py \
#       --input-dir ml_outputs \
#       --output-dir attached_assets
#
# Inputs (from 04_anomaly_detection.py):
#   ml_outputs/anomaly_scores.csv
#   ml_outputs/anomaly_clients_top.csv
#   ml_outputs/anomaly_summary.json
#
# Output:
#   attached_assets/anomaly_data.json   ← dashboard reads this

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def safe_str(value, default=""):
    try:
        if pd.isna(value):
            return default
        return str(value).strip()
    except Exception:
        return default


def format_exposure(value):
    v = safe_float(value)
    if v <= 0:
        return "À vérifier"
    if v >= 1_000_000:
        return f"{v/1_000_000:.2f}M TND"
    if v >= 1_000:
        return f"{v/1_000:.0f}K TND"
    return f"{v:.0f} TND"


def build_anomaly_kpis(df, summary):
    """Build KPI block from anomaly scores dataframe."""
    total_rows    = len(df)
    unique_cpte   = df["CPTE"].nunique() if "CPTE" in df.columns else total_rows

    n_anomaly     = int(df["IS_ANOMALY"].sum()) if "IS_ANOMALY" in df.columns else 0
    anomaly_rate  = round(n_anomaly / total_rows * 100, 2) if total_rows > 0 else 0

    strong    = int((df["ANOMALY_LEVEL"] == "Anomalie forte").sum())    \
                if "ANOMALY_LEVEL" in df.columns else 0
    moderate  = int((df["ANOMALY_LEVEL"] == "Anomalie modérée").sum())  \
                if "ANOMALY_LEVEL" in df.columns else 0
    watch     = int((df["ANOMALY_LEVEL"] == "Surveillance").sum())      \
                if "ANOMALY_LEVEL" in df.columns else 0
    normal    = int((df["ANOMALY_LEVEL"] == "Normal").sum())            \
                if "ANOMALY_LEVEL" in df.columns else 0

    hidden    = int(df["STABLE_BUT_SUSPICIOUS"].sum()) \
                if "STABLE_BUT_SUSPICIOUS" in df.columns else 0

    return {
        "total_rows_analyzed":    total_rows,
        "unique_clients":         unique_cpte,
        "anomalies_detected":     n_anomaly,
        "anomaly_rate_pct":       anomaly_rate,
        "strong_anomalies":       strong,
        "moderate_anomalies":     moderate,
        "watch_anomalies":        watch,
        "normal_clients":         normal,
        "hidden_risk_clients":    hidden,
        "contamination":          summary.get("contamination", 0.03),
    }


def build_level_distribution(df):
    """Donut chart data for anomaly level distribution."""
    if "ANOMALY_LEVEL" not in df.columns:
        return []

    counts = df["ANOMALY_LEVEL"].value_counts().to_dict()
    total  = len(df)

    order  = ["Anomalie forte", "Anomalie modérée", "Surveillance", "Normal"]
    colors = {
        "Anomalie forte":    "#ffb4ab",   # error red
        "Anomalie modérée":  "#fbe273",   # tertiary yellow
        "Surveillance":      "#5ffbd6",   # primary-container teal
        "Normal":            "#2a344e",   # surface-variant
    }

    return [
        {
            "label":   level,
            "count":   counts.get(level, 0),
            "pct":     round(counts.get(level, 0) / total * 100, 1),
            "color":   colors.get(level, "#bacac3"),
        }
        for level in order
    ]


def build_sector_breakdown(df):
    """Anomaly rate per sector — for bar chart."""
    if "SECTOR" not in df.columns or "IS_ANOMALY" not in df.columns:
        return []

    df_clean = df[df["SECTOR"].notna() & (df["SECTOR"] != "UNKNOWN")].copy()

    if df_clean.empty:
        return []

    sector_stats = (
        df_clean.groupby("SECTOR", as_index=False)
        .agg(
            total     = ("IS_ANOMALY", "count"),
            anomalies = ("IS_ANOMALY", "sum"),
        )
    )
    sector_stats["anomaly_rate_pct"] = (
        sector_stats["anomalies"] / sector_stats["total"] * 100
    ).round(1)

    return (
        sector_stats
        .sort_values("anomaly_rate_pct", ascending=False)
        .head(10)
        .assign(
            total     = lambda x: x["total"].apply(safe_int),
            anomalies = lambda x: x["anomalies"].apply(safe_int),
        )
        .to_dict(orient="records")
    )


def build_monthly_trend(df):
    """Monthly anomaly count — for line chart."""
    if "PERIODE" not in df.columns or "IS_ANOMALY" not in df.columns:
        return []

    df_t = df.copy()
    df_t["PERIODE"] = pd.to_datetime(df_t["PERIODE"], errors="coerce")
    df_t = df_t.dropna(subset=["PERIODE"])
    df_t["month"] = df_t["PERIODE"].dt.to_period("M").astype(str)

    monthly = (
        df_t.groupby("month", as_index=False)
        .agg(
            total     = ("IS_ANOMALY", "count"),
            anomalies = ("IS_ANOMALY", "sum"),
        )
        .sort_values("month")
        .tail(12)           # last 12 months
    )
    monthly["anomaly_rate_pct"] = (
        monthly["anomalies"] / monthly["total"] * 100
    ).round(1)

    return monthly.to_dict(orient="records")


def build_top_anomaly_records(df, top_n=100):
    """Top N anomalous clients for the dashboard table."""
    cols_wanted = [
        "CPTE", "CODE_CLIENT", "PERIODE",
        "ANOMALY_SCORE", "IS_ANOMALY", "ANOMALY_LEVEL", "ANOMALY_ACTION",
        "RISK_SCORE", "PREDICTED_RISK",
        "NBRJDEP", "RISK_BRUT", "NET_MONTHLY_IN",
        "SECTOR", "INDUSTRY", "EMPLOYMENT_STATUS",
        "STABLE_BUT_SUSPICIOUS",
    ]
    cols = [c for c in cols_wanted if c in df.columns]

    top = (
        df[df["IS_ANOMALY"] == 1][cols]
        .sort_values("ANOMALY_SCORE", ascending=False)
        .head(top_n)
        .copy()
    )

    records = []
    for _, row in top.iterrows():
        risk_score = safe_float(row.get("RISK_SCORE", 0))

        records.append({
            "cpte":                   safe_str(row.get("CPTE")),
            "code_client":            safe_str(row.get("CODE_CLIENT")),
            "periode":                safe_str(row.get("PERIODE")),

            "anomaly_score":          round(safe_float(row.get("ANOMALY_SCORE")), 2),
            "is_anomaly":             safe_int(row.get("IS_ANOMALY")),
            "anomaly_level":          safe_str(row.get("ANOMALY_LEVEL", "Normal")),
            "anomaly_action":         safe_str(row.get("ANOMALY_ACTION", "")),

            "ml_risk_score":          round(risk_score, 4),
            "ml_risk_score_pct":      round(risk_score * 100, 1),
            "ml_predicted_risk":      safe_int(row.get("PREDICTED_RISK", 0)),

            "nbrjdep":                round(safe_float(row.get("NBRJDEP", 0)), 0),
            "risk_brut":              round(safe_float(row.get("RISK_BRUT", 0)), 2),
            "risk_brut_display":      format_exposure(row.get("RISK_BRUT", 0)),
            "net_monthly_in":         round(safe_float(row.get("NET_MONTHLY_IN", 0)), 2),

            "sector":                 safe_str(row.get("SECTOR", "UNKNOWN")),
            "industry":               safe_str(row.get("INDUSTRY", "UNKNOWN")),
            "employment_status":      safe_str(row.get("EMPLOYMENT_STATUS", "UNKNOWN")),

            "stable_but_suspicious":  safe_int(row.get("STABLE_BUT_SUSPICIOUS", 0)),

            # Combined risk classification
            "combined_risk": (
                "RISQUE CONFIRMÉ"   if risk_score >= 0.65 and safe_int(row.get("IS_ANOMALY")) == 1 else
                "RISQUE CACHÉ"      if risk_score <  0.65 and safe_int(row.get("IS_ANOMALY")) == 1 else
                "RISQUE CONNU"      if risk_score >= 0.65 else
                "NORMAL"
            ),
        })

    return records


def build_hidden_risk_records(df, top_n=50):
    """
    Clients flagged STABLE_BUT_SUSPICIOUS:
    ML says safe, but anomaly detected.
    These are the most interesting for banking operations.
    """
    if "STABLE_BUT_SUSPICIOUS" not in df.columns:
        return []

    hidden = df[df["STABLE_BUT_SUSPICIOUS"] == 1].copy()
    if hidden.empty:
        return []

    hidden = hidden.sort_values("ANOMALY_SCORE", ascending=False).head(top_n)

    records = []
    for _, row in hidden.iterrows():
        records.append({
            "cpte":              safe_str(row.get("CPTE")),
            "anomaly_score":     round(safe_float(row.get("ANOMALY_SCORE")), 2),
            "anomaly_level":     safe_str(row.get("ANOMALY_LEVEL", "Normal")),
            "ml_risk_score_pct": round(safe_float(row.get("RISK_SCORE", 0)) * 100, 1),
            "anomaly_action":    safe_str(row.get("ANOMALY_ACTION", "")),
            "nbrjdep":           round(safe_float(row.get("NBRJDEP", 0)), 0),
            "risk_brut_display": format_exposure(row.get("RISK_BRUT", 0)),
            "sector":            safe_str(row.get("SECTOR", "UNKNOWN")),
            "message": (
                "Ce client semble stable selon le score ML, "
                "mais son comportement est atypique. "
                "Une vérification manuelle est recommandée."
            ),
        })

    return records


def main():
    parser = argparse.ArgumentParser(
        description="Export anomaly detection results to dashboard JSON."
    )
    parser.add_argument("--input-dir",  default="ml_outputs")
    parser.add_argument("--output-dir", default="attached_assets")
    args = parser.parse_args()

    input_dir  = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load anomaly outputs ──────────────────────────────────
    print("[1/5] Loading anomaly outputs")

    scores_path  = input_dir / "anomaly_scores.csv"
    top_path     = input_dir / "anomaly_clients_top.csv"
    summary_path = input_dir / "anomaly_summary.json"

    if not scores_path.exists():
        raise FileNotFoundError(
            f"Missing: {scores_path}\n"
            "Run 04_anomaly_detection.py first."
        )

    df = pd.read_csv(scores_path, low_memory=False)
    print(f"      Rows loaded  : {len(df):,}")
    print(f"      Columns      : {list(df.columns)}")

    summary = {}
    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        print(f"      Summary loaded from {summary_path}")
    else:
        print(f"      ⚠️  Summary not found, using computed values")

    # ── Build JSON sections ───────────────────────────────────
    print("[2/5] Building KPIs")
    kpis = build_anomaly_kpis(df, summary)

    print("[3/5] Building distributions")
    level_dist    = build_level_distribution(df)
    sector_dist   = build_sector_breakdown(df)
    monthly_trend = build_monthly_trend(df)

    print("[4/5] Building client records")
    top_anomalies  = build_top_anomaly_records(df, top_n=100)
    hidden_risk    = build_hidden_risk_records(df, top_n=50)

    # ── Assemble final JSON ───────────────────────────────────
    print("[5/5] Saving anomaly_data.json")

    anomaly_json = {
        "module":      "Anomaly Detection — Isolation Forest",
        "description": (
            "Détecte les comportements clients atypiques "
            "indépendamment du score ML supervisé. "
            "Identifie les clients à RISQUE CACHÉ : "
            "score faible mais comportement inhabituel."
        ),

        "kpis": kpis,

        "level_distribution": level_dist,
        "sector_breakdown":   sector_dist,
        "monthly_trend":      monthly_trend,

        "top_anomalies":  top_anomalies,
        "hidden_risk":    hidden_risk,

        "jury_summary": {
            "total_analyzed":   kpis["unique_clients"],
            "anomalies_found":  kpis["anomalies_detected"],
            "anomaly_rate":     f"{kpis['anomaly_rate_pct']}%",
            "hidden_risk":      kpis["hidden_risk_clients"],
            "key_insight": (
                f"Sur {kpis['unique_clients']:,} clients analysés, "
                f"{kpis['anomalies_detected']:,} présentent un comportement atypique "
                f"({kpis['anomaly_rate_pct']}%). "
                f"Parmi eux, {kpis['hidden_risk_clients']:,} sont classés "
                f"'stables' par le modèle ML mais anormaux selon Isolation Forest. "
                f"Ce sont les cas les plus importants à investiguer."
            ),
        },
    }

    out_path = output_dir / "anomaly_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(anomaly_json, f, ensure_ascii=False, indent=2)

    print(f"      Saved: {out_path}")

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "═"*55)
    print("✅  Anomaly export completed")
    print("═"*55)
    print(f"  Total clients analyzed : {kpis['unique_clients']:,}")
    print(f"  Anomalies detected     : {kpis['anomalies_detected']:,} "
          f"({kpis['anomaly_rate_pct']}%)")
    print(f"  Strong anomalies       : {kpis['strong_anomalies']:,}")
    print(f"  Moderate anomalies     : {kpis['moderate_anomalies']:,}")
    print(f"  Hidden risk clients    : {kpis['hidden_risk_clients']:,} ⚠️")
    print(f"\n  Output: {out_path}")
    print(f"\n  Key insight:")
    print(f"  {anomaly_json['jury_summary']['key_insight']}")


if __name__ == "__main__":
    main()