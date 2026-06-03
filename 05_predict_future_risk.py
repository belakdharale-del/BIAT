# 05_predict_future_risk.py
# BIAT Risk Monitor — Future Risk Prediction Export
#
# Goal:
#   Build a business-oriented JSON file for the application:
#   - predicted future risk score
#   - predicted future level: Faible / Moyen / Élevé / Critique
#   - expected evolution: Stable / Aggravation / Amélioration / Nouveau client
#   - anomaly signal if anomaly_scores.csv is available
#   - priority and recommendation for banking action
#
# Usage:
#   python 05_predict_future_risk.py --input-dir ml_outputs --output-dir attached_assets
#
# Inputs expected:
#   ml_outputs/predictions_test.csv        <- produced by training/export pipeline
#   ml_outputs/anomaly_scores.csv          <- optional, produced by 04_anomaly_detection.py
#
# Outputs:
#   attached_assets/future_predictions.json
#   attached_assets/future_predictions.csv

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# Safe conversion helpers
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# Risk business rules
# ---------------------------------------------------------------------
def risk_level_from_score(score):
    """
    Convert a future risk score into a business alert level.
    score must be between 0 and 1.
    """
    score = safe_float(score)
    if score >= 0.85:
        return "Critique"
    if score >= 0.65:
        return "Élevé"
    if score >= 0.40:
        return "Moyen"
    return "Faible"


def current_level_from_observed_state(nbrjdep, risk_brut):
    """
    Estimate current level from observed banking state.
    This is not the model prediction; it is a business interpretation
    of the current account situation.
    """
    nbrjdep = safe_float(nbrjdep)
    risk_brut = safe_float(risk_brut)

    if nbrjdep >= 30 or risk_brut > 0:
        return "Critique"
    if nbrjdep >= 15:
        return "Élevé"
    if nbrjdep >= 4:
        return "Moyen"
    return "Faible"


def level_rank(level):
    ranks = {
        "Faible": 1,
        "Moyen": 2,
        "Élevé": 3,
        "Critique": 4,
    }
    return ranks.get(level, 0)


def expected_evolution(current_level, future_level, history_months):
    """
    Compare current observed level with predicted future level.
    """
    if safe_int(history_months) <= 1:
        return "Nouveau client"

    c = level_rank(current_level)
    f = level_rank(future_level)

    if f > c:
        if f - c >= 2:
            return "Aggravation forte"
        return "Aggravation"
    if f < c:
        return "Amélioration"
    return "Stable"


def prediction_reliability(history_months):
    """
    Reliability indicator for clients with limited historical data.
    """
    m = safe_int(history_months)
    if m >= 6:
        return "Bonne"
    if m >= 3:
        return "Moyenne"
    return "Faible"


def format_exposure(value):
    v = safe_float(value)
    if v <= 0:
        return "0 TND"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.2f}M TND"
    if v >= 1_000:
        return f"{v / 1_000:.0f}K TND"
    return f"{v:.0f} TND"


def normalize_anomaly_level(value, is_anomaly=0):
    value = safe_str(value)
    if value:
        return value
    return "Anomalie forte" if safe_int(is_anomaly) == 1 else "Normal"


def priority_level(future_level, anomaly_level, risk_brut, evolution):
    """
    Combine predictive risk, anomaly signal and exposure.
    """
    exposure = safe_float(risk_brut)
    anomaly_level = safe_str(anomaly_level)

    if future_level == "Critique" and ("forte" in anomaly_level.lower() or exposure > 0):
        return "Très élevée"
    if future_level == "Critique":
        return "Élevée"
    if future_level == "Élevé" and ("anom" in anomaly_level.lower() or "Aggravation" in safe_str(evolution)):
        return "Élevée"
    if future_level == "Élevé":
        return "Moyenne"
    if future_level == "Moyen" and "Aggravation" in safe_str(evolution):
        return "Moyenne"
    return "Faible"


def recommendation(future_level, anomaly_level, evolution, reliability):
    """
    Human-readable business recommendation.
    """
    anomaly = "anom" in safe_str(anomaly_level).lower() and safe_str(anomaly_level).lower() != "normal"

    if future_level == "Critique" and anomaly:
        return "Intervention immédiate : risque futur critique et comportement atypique détecté."
    if future_level == "Critique":
        return "Intervention immédiate et revue du dossier client."
    if future_level == "Élevé" and "Aggravation" in safe_str(evolution):
        return "Contacter le client et suivre l'évolution avant passage au niveau critique."
    if future_level == "Élevé":
        return "Surveillance rapprochée et notification préventive."
    if future_level == "Moyen":
        return "Suivi mensuel renforcé."
    if reliability == "Faible":
        return "Surveillance automatique : historique limité, score à interpréter avec prudence."
    return "Aucune action urgente."


# ---------------------------------------------------------------------
# Data loading and preparation
# ---------------------------------------------------------------------
def load_predictions(input_dir):
    path = Path(input_dir) / "predictions_test.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing: {path}\n"
            "Run the training/export script first so predictions_test.csv exists."
        )

    df = pd.read_csv(path, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]

    required = ["CPTE", "RISK_SCORE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"predictions_test.csv is missing required columns: {missing}")

    if "PERIODE" in df.columns:
        df["PERIODE"] = pd.to_datetime(df["PERIODE"], errors="coerce")
    else:
        df["PERIODE"] = pd.NaT

    df["RISK_SCORE"] = pd.to_numeric(df["RISK_SCORE"], errors="coerce").fillna(0)

    for col in ["NBRJDEP", "RISK_BRUT", "MVT", "NET_MONTHLY_IN"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0

    return df


def load_anomaly_scores(input_dir):
    path = Path(input_dir) / "anomaly_scores.csv"
    if not path.exists():
        return None

    anom = pd.read_csv(path, low_memory=False)
    anom.columns = [str(c).strip() for c in anom.columns]

    if "PERIODE" in anom.columns:
        anom["PERIODE"] = pd.to_datetime(anom["PERIODE"], errors="coerce")
    else:
        anom["PERIODE"] = pd.NaT

    keep = [
        "CPTE", "PERIODE", "ANOMALY_SCORE", "IS_ANOMALY",
        "ANOMALY_LEVEL", "ANOMALY_ACTION", "STABLE_BUT_SUSPICIOUS"
    ]
    keep = [c for c in keep if c in anom.columns]

    return anom[keep].copy()


def merge_anomaly(pred_latest, anomaly):
    if anomaly is None or anomaly.empty:
        pred_latest["ANOMALY_SCORE"] = 0
        pred_latest["IS_ANOMALY"] = 0
        pred_latest["ANOMALY_LEVEL"] = "Normal"
        pred_latest["ANOMALY_ACTION"] = ""
        pred_latest["STABLE_BUT_SUSPICIOUS"] = 0
        return pred_latest

    # Prefer exact CPTE + PERIODE merge when possible.
    if "PERIODE" in pred_latest.columns and "PERIODE" in anomaly.columns:
        merged = pred_latest.merge(
            anomaly,
            on=["CPTE", "PERIODE"],
            how="left",
            suffixes=("", "_anom")
        )
    else:
        # Fallback: latest anomaly per CPTE
        anomaly_latest = anomaly.sort_values("PERIODE").groupby("CPTE", as_index=False).tail(1)
        merged = pred_latest.merge(
            anomaly_latest.drop(columns=["PERIODE"], errors="ignore"),
            on="CPTE",
            how="left"
        )

    for col, default in [
        ("ANOMALY_SCORE", 0),
        ("IS_ANOMALY", 0),
        ("ANOMALY_LEVEL", "Normal"),
        ("ANOMALY_ACTION", ""),
        ("STABLE_BUT_SUSPICIOUS", 0),
    ]:
        if col not in merged.columns:
            merged[col] = default
        merged[col] = merged[col].fillna(default)

    return merged


# ---------------------------------------------------------------------
# Main export logic
# ---------------------------------------------------------------------
def build_future_predictions(df, anomaly=None, top_n=1000):
    """
    Use latest available observation per client.
    RISK_SCORE is interpreted as the model's predicted future risk score
    at horizon 30 days, because the target was built using t+1.
    """
    df = df.copy()

    # Number of observations available per account in predictions file.
    # In a complete dataset, this can be replaced by full history count.
    history = df.groupby("CPTE").size().rename("history_months")
    df = df.merge(history, on="CPTE", how="left")

    # Keep latest row per client.
    if "PERIODE" in df.columns:
        df_latest = (
            df.sort_values(["CPTE", "PERIODE"])
              .groupby("CPTE", as_index=False)
              .tail(1)
              .copy()
        )
    else:
        df_latest = df.drop_duplicates("CPTE", keep="last").copy()

    df_latest = merge_anomaly(df_latest, anomaly)

    records = []
    for _, row in df_latest.iterrows():
        cpte = safe_str(row.get("CPTE"))
        periode = row.get("PERIODE")
        periode_str = "" if pd.isna(periode) else str(pd.to_datetime(periode).date())

        risk_score = safe_float(row.get("RISK_SCORE"))
        risk_score_pct = round(risk_score * 100, 2)

        current_level = current_level_from_observed_state(
            row.get("NBRJDEP", 0),
            row.get("RISK_BRUT", 0)
        )
        future_level = risk_level_from_score(risk_score)

        hist_months = safe_int(row.get("history_months", 1))
        evolution = expected_evolution(current_level, future_level, hist_months)
        reliability = prediction_reliability(hist_months)

        anomaly_level = normalize_anomaly_level(
            row.get("ANOMALY_LEVEL", "Normal"),
            row.get("IS_ANOMALY", 0)
        )

        prio = priority_level(
            future_level=future_level,
            anomaly_level=anomaly_level,
            risk_brut=row.get("RISK_BRUT", 0),
            evolution=evolution
        )

        rec = recommendation(
            future_level=future_level,
            anomaly_level=anomaly_level,
            evolution=evolution,
            reliability=reliability
        )

        records.append({
            "cpte": cpte,
            "code_client": safe_str(row.get("CODE_CLIENT", "")),
            "periode_actuelle": periode_str,

            # Current observed state
            "nbrjdep_actuel": round(safe_float(row.get("NBRJDEP", 0)), 2),
            "risk_brut_actuel": round(safe_float(row.get("RISK_BRUT", 0)), 2),
            "risk_brut_display": format_exposure(row.get("RISK_BRUT", 0)),
            "niveau_actuel": current_level,

            # Future prediction
            "score_futur_predit": round(risk_score, 4),
            "score_futur_predit_pct": risk_score_pct,
            "niveau_futur_predit": future_level,
            "evolution_prevue": evolution,
            "fiabilite_prediction": reliability,
            "history_months": hist_months,

            # Anomaly signal
            "anomaly_score": round(safe_float(row.get("ANOMALY_SCORE", 0)), 2),
            "is_anomaly": safe_int(row.get("IS_ANOMALY", 0)),
            "niveau_anomalie": anomaly_level,
            "stable_but_suspicious": safe_int(row.get("STABLE_BUT_SUSPICIOUS", 0)),
            "anomaly_action": safe_str(row.get("ANOMALY_ACTION", "")),

            # Business decision
            "priorite": prio,
            "recommandation": rec,

            # Context
            "sector": safe_str(row.get("SECTOR", "UNKNOWN")),
            "industry": safe_str(row.get("INDUSTRY", "UNKNOWN")),
            "employment_status": safe_str(row.get("EMPLOYMENT_STATUS", "UNKNOWN")),
            "net_monthly_in": round(safe_float(row.get("NET_MONTHLY_IN", 0)), 2),
        })

    # Priority sorting for operational dashboard
    priority_order = {"Très élevée": 4, "Élevée": 3, "Moyenne": 2, "Faible": 1}
    level_order = {"Critique": 4, "Élevé": 3, "Moyen": 2, "Faible": 1}

    records = sorted(
        records,
        key=lambda x: (
            priority_order.get(x["priorite"], 0),
            level_order.get(x["niveau_futur_predit"], 0),
            x["score_futur_predit_pct"],
            x["anomaly_score"]
        ),
        reverse=True
    )

    return records[:top_n], records


def build_summary(all_records):
    total = len(all_records)
    by_future = {}
    by_evolution = {}
    by_priority = {}

    for r in all_records:
        by_future[r["niveau_futur_predit"]] = by_future.get(r["niveau_futur_predit"], 0) + 1
        by_evolution[r["evolution_prevue"]] = by_evolution.get(r["evolution_prevue"], 0) + 1
        by_priority[r["priorite"]] = by_priority.get(r["priorite"], 0) + 1

    return {
        "total_clients": total,
        "future_level_distribution": by_future,
        "expected_evolution_distribution": by_evolution,
        "priority_distribution": by_priority,
        "critical_future_clients": by_future.get("Critique", 0),
        "high_future_clients": by_future.get("Élevé", 0),
        "medium_future_clients": by_future.get("Moyen", 0),
        "low_future_clients": by_future.get("Faible", 0),
        "aggravation_clients": (
            by_evolution.get("Aggravation", 0) +
            by_evolution.get("Aggravation forte", 0)
        ),
        "anomalous_clients": sum(1 for r in all_records if r["is_anomaly"] == 1),
        "new_clients": by_evolution.get("Nouveau client", 0),
    }


def main():
    parser = argparse.ArgumentParser(description="Export future risk predictions for BIAT Risk Monitor.")
    parser.add_argument("--input-dir", default="ml_outputs")
    parser.add_argument("--output-dir", default="attached_assets")
    parser.add_argument("--top-n", type=int, default=1000)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[1/5] Loading predictions_test.csv")
    predictions = load_predictions(input_dir)
    print(f"      Rows loaded: {len(predictions):,}")
    print(f"      Unique clients: {predictions['CPTE'].nunique():,}")

    print("[2/5] Loading anomaly scores if available")
    anomaly = load_anomaly_scores(input_dir)
    if anomaly is None:
        print("      No anomaly_scores.csv found. Continuing without anomaly signal.")
    else:
        print(f"      Anomaly rows loaded: {len(anomaly):,}")

    print("[3/5] Building future prediction records")
    top_records, all_records = build_future_predictions(
        predictions,
        anomaly=anomaly,
        top_n=args.top_n
    )

    print("[4/5] Building summary")
    summary = build_summary(all_records)

    future_json = {
        "module": "Future Risk Prediction",
        "description": (
            "Prédit le niveau futur de risque client à horizon 30 jours "
            "à partir du score LightGBM, puis compare le niveau actuel "
            "au niveau futur prédit afin de qualifier l'évolution prévue."
        ),
        "model_logic": {
            "main_model": "LightGBM",
            "prediction_target": "Risque futur à horizon 30 jours",
            "future_levels": {
                "Faible": "score < 40%",
                "Moyen": "40% <= score < 65%",
                "Élevé": "65% <= score < 85%",
                "Critique": "score >= 85%",
            },
            "evolution_logic": (
                "Comparaison entre niveau actuel observé et niveau futur prédit : "
                "Stable, Aggravation, Aggravation forte, Amélioration ou Nouveau client."
            ),
            "anomaly_complement": "Isolation Forest si anomaly_scores.csv est disponible.",
        },
        "summary": summary,
        "top_future_risk_clients": top_records,
        "all_future_predictions": all_records,
        "jury_summary": (
            f"Le module de prédiction future analyse {summary['total_clients']:,} clients. "
            f"{summary['critical_future_clients']:,} clients sont prédits critiques, "
            f"{summary['high_future_clients']:,} élevés et "
            f"{summary['aggravation_clients']:,} présentent une aggravation prévue. "
            f"Le module d'anomalie signale {summary['anomalous_clients']:,} comportements atypiques."
        ),
    }

    print("[5/5] Saving outputs")
    json_path = output_dir / "future_predictions.json"
    csv_path = output_dir / "future_predictions.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(future_json, f, ensure_ascii=False, indent=2)

    pd.DataFrame(all_records).to_csv(csv_path, index=False, encoding="utf-8-sig")

    print("\n" + "═" * 60)
    print("✅ Future risk prediction export completed")
    print("═" * 60)
    print(f"Total clients           : {summary['total_clients']:,}")
    print(f"Future critical clients : {summary['critical_future_clients']:,}")
    print(f"Future high clients     : {summary['high_future_clients']:,}")
    print(f"Aggravation clients     : {summary['aggravation_clients']:,}")
    print(f"Anomalous clients       : {summary['anomalous_clients']:,}")
    print(f"\nJSON output: {json_path}")
    print(f"CSV output : {csv_path}")
    print(f"\nJury summary:\n{future_json['jury_summary']}")


if __name__ == "__main__":
    main()
