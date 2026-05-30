import json
from pathlib import Path

import pandas as pd


INPUT_PATH = Path("ml_outputs/anomaly_scores.csv")
OUTPUT_DIR = Path("attached_assets")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "anomaly_clients.json"


def safe_float(x, default=0.0):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def safe_int(x, default=0):
    try:
        if pd.isna(x):
            return default
        return int(float(x))
    except Exception:
        return default


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"File not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH, low_memory=False)

    df["PERIODE"] = pd.to_datetime(df["PERIODE"], errors="coerce")

    # On garde surtout les anomalies
    anomalies = df[df["IS_ANOMALY"] == 1].copy()

    # Trier par score anomalie
    anomalies = anomalies.sort_values("ANOMALY_SCORE", ascending=False)

    clients = []

    for _, row in anomalies.head(500).iterrows():
        anomaly_score = safe_float(row.get("ANOMALY_SCORE"))
        risk_score = safe_float(row.get("RISK_SCORE"))

        clients.append({
            "cpte": str(row.get("CPTE", "")),
            "periode": str(row.get("PERIODE", ""))[:10],
            "anomaly_score": round(anomaly_score, 1),
            "anomaly_level": str(row.get("ANOMALY_LEVEL", "")),
            "is_anomaly": safe_int(row.get("IS_ANOMALY")),
            "stable_but_suspicious": safe_int(row.get("STABLE_BUT_SUSPICIOUS")),
            "risk_score": round(risk_score * 100, 1),
            "nbrjdep": safe_int(row.get("NBRJDEP")),
            "risk_brut": safe_float(row.get("RISK_BRUT")),
            "net_monthly_in": safe_float(row.get("NET_MONTHLY_IN")),
            "sector": str(row.get("SECTOR", "")),
            "industry": str(row.get("INDUSTRY", "")),
            "employment_status": str(row.get("EMPLOYMENT_STATUS", "")),
            "action": str(row.get("ANOMALY_ACTION", "")),
        })

    summary = {
        "total_anomalies": int((df["IS_ANOMALY"] == 1).sum()),
        "strong_anomalies": int((df["ANOMALY_LEVEL"] == "Anomalie forte").sum()),
        "moderate_anomalies": int((df["ANOMALY_LEVEL"] == "Anomalie modérée").sum()),
        "stable_but_suspicious": int(df["STABLE_BUT_SUSPICIOUS"].sum()),
        "clients": clients,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("Saved:", OUTPUT_PATH)
    print("Total anomalies:", summary["total_anomalies"])
    print("Strong anomalies:", summary["strong_anomalies"])
    print("Stable but suspicious:", summary["stable_but_suspicious"])


if __name__ == "__main__":
    main()