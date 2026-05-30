import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split


def make_onehot_encoder():
    try:
        return OneHotEncoder(handle_unknown="ignore", min_frequency=50, sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", min_frequency=50, sparse=False)


def choose_feature_columns(df):
    excluded = {
        "TARGET_RISK_30J",
        "NEXT_PERIODE",
        "NEXT_NBRJDEP",
        "NEXT_RISK_BRUT",
        "CPTE",
        "CODE_CLIENT",
        "PERIODE",
    }
    return [c for c in df.columns if c not in excluded]


def build_preprocessor(X):
    categorical_features = X.select_dtypes(
        include=["object", "string", "category"]
    ).columns.tolist()

    numeric_features = [c for c in X.columns if c not in categorical_features]

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", make_onehot_encoder()),
    ])

    return ColumnTransformer([
        ("num", numeric_pipeline, numeric_features),
        ("cat", categorical_pipeline, categorical_features),
    ])


def normalize_anomaly_scores(raw_scores):
    """
    IsolationForest donne un score où plus haut = plus normal.
    Nous inversons le score pour obtenir :
    ANOMALY_SCORE élevé = comportement plus atypique.
    """
    inverted = -np.asarray(raw_scores, dtype=float)
    min_v = np.nanmin(inverted)
    max_v = np.nanmax(inverted)

    if max_v - min_v < 1e-12:
        return np.zeros_like(inverted)

    return (inverted - min_v) / (max_v - min_v) * 100


def anomaly_level(score):
    if score >= 85:
        return "Anomalie forte"
    if score >= 70:
        return "Anomalie modérée"
    if score >= 55:
        return "Surveillance"
    return "Normal"


def anomaly_action(level, risk_score):
    risk_score = 0 if pd.isna(risk_score) else float(risk_score)

    if level == "Anomalie forte":
        if risk_score >= 0.70:
            return "Contrôle prioritaire : risque élevé et comportement atypique"
        return "Contrôle manuel du comportement client"

    if level == "Anomalie modérée":
        return "Analyse complémentaire du dossier"

    if level == "Surveillance":
        return "Surveillance renforcée"

    return "Aucune action spécifique"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="dataset_ml_clean.csv")
    parser.add_argument("--predictions", default="ml_outputs/predictions_test.csv")
    parser.add_argument("--output-dir", default="ml_outputs")
    parser.add_argument("--contamination", type=float, default=0.03)
    parser.add_argument("--sample", type=int, default=200000)
    args = parser.parse_args()

    input_path = Path(args.input)
    pred_path = Path(args.predictions)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    print("[1/6] Loading dataset")
    df = pd.read_csv(input_path, low_memory=False)
    df["PERIODE"] = pd.to_datetime(df["PERIODE"], errors="coerce")
    df = df.dropna(subset=["PERIODE"]).copy()

    if args.sample and args.sample > 0 and args.sample < len(df):
        print(f"Sampling {args.sample:,} rows")
        if "TARGET_RISK_30J" in df.columns:
            _, df = train_test_split(
                df,
                test_size=args.sample,
                stratify=df["TARGET_RISK_30J"],
                random_state=42,
            )
        else:
            df = df.sample(args.sample, random_state=42)

        df = df.sort_values("PERIODE").reset_index(drop=True)

    print("Dataset shape:", df.shape)

    print("[2/6] Time split")
    unique_periods = sorted(df["PERIODE"].dropna().unique())
    split_period = unique_periods[int(len(unique_periods) * 0.80)]

    train_df = df[df["PERIODE"] < split_period].copy()
    test_df = df[df["PERIODE"] >= split_period].copy()

    print("Train shape:", train_df.shape)
    print("Test shape :", test_df.shape)

    feature_columns = choose_feature_columns(df)

    X_train = train_df[feature_columns]
    X_test = test_df[feature_columns]

    print("[3/6] Building model")
    preprocessor = build_preprocessor(X_train)

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("isolation_forest", IsolationForest(
            n_estimators=250,
            contamination=args.contamination,
            random_state=42,
            n_jobs=-1,
        )),
    ])

    print("[4/6] Training Isolation Forest")
    model.fit(X_train)

    raw_scores = model.decision_function(X_test)
    predictions = model.predict(X_test)

    anomaly_scores = normalize_anomaly_scores(raw_scores)

    print("[5/6] Creating outputs")
    base_cols = ["PERIODE", "CPTE", "CODE_CLIENT"]
    base_cols = [c for c in base_cols if c in test_df.columns]

    result = test_df[base_cols].copy()
    result["ANOMALY_SCORE"] = np.round(anomaly_scores, 2)
    result["IS_ANOMALY"] = (predictions == -1).astype(int)
    result["ANOMALY_LEVEL"] = result["ANOMALY_SCORE"].apply(anomaly_level)

    for col in [
        "NBRJDEP",
        "RISK_BRUT",
        "NET_MONTHLY_IN",
        "SECTOR",
        "INDUSTRY",
        "EMPLOYMENT_STATUS",
    ]:
        if col in test_df.columns:
            result[col] = test_df[col].values

    if pred_path.exists():
        pred = pd.read_csv(pred_path, low_memory=False)
        pred["PERIODE"] = pd.to_datetime(pred["PERIODE"], errors="coerce")

        merge_cols = ["PERIODE", "CPTE"]
        keep_cols = merge_cols + [
            c for c in ["RISK_SCORE", "PREDICTED_RISK"] if c in pred.columns
        ]

        result = result.merge(
            pred[keep_cols].drop_duplicates(subset=merge_cols),
            on=merge_cols,
            how="left",
        )
    else:
        result["RISK_SCORE"] = np.nan
        result["PREDICTED_RISK"] = np.nan

    result["ANOMALY_ACTION"] = [
        anomaly_action(level, risk)
        for level, risk in zip(result["ANOMALY_LEVEL"], result["RISK_SCORE"])
    ]

    result["STABLE_BUT_SUSPICIOUS"] = (
        (result["IS_ANOMALY"] == 1)
        & (result["RISK_SCORE"].fillna(0) < 0.65)
    ).astype(int)

    result = result.sort_values(
        by=["IS_ANOMALY", "ANOMALY_SCORE"],
        ascending=[False, False],
    )

    anomaly_scores_path = output_dir / "anomaly_scores.csv"
    anomaly_top_path = output_dir / "anomaly_clients_top.csv"
    summary_path = output_dir / "anomaly_summary.json"

    result.to_csv(anomaly_scores_path, index=False)
    result.head(500).to_csv(anomaly_top_path, index=False)

    summary = {
        "module": "Isolation Forest Anomaly Detection",
        "contamination": args.contamination,
        "rows_analyzed": int(len(result)),
        "unique_clients_analyzed": int(result["CPTE"].nunique()) if "CPTE" in result.columns else None,
        "anomaly_rows": int(result["IS_ANOMALY"].sum()),
        "anomaly_rate_percent": round(float(result["IS_ANOMALY"].mean() * 100), 2),
        "strong_anomalies": int((result["ANOMALY_LEVEL"] == "Anomalie forte").sum()),
        "moderate_anomalies": int((result["ANOMALY_LEVEL"] == "Anomalie modérée").sum()),
        "stable_but_suspicious": int(result["STABLE_BUT_SUSPICIOUS"].sum()),
        "explanation": (
            "Isolation Forest detects atypical banking behavior without using the target label. "
            "It complements the supervised scoring model."
        ),
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("[6/6] Done")
    print("Saved:", anomaly_scores_path)
    print("Saved:", anomaly_top_path)
    print("Saved:", summary_path)

    print()
    print("Summary:")
    print("Rows analyzed         :", summary["rows_analyzed"])
    print("Anomaly rows          :", summary["anomaly_rows"])
    print("Anomaly rate %        :", summary["anomaly_rate_percent"])
    print("Strong anomalies      :", summary["strong_anomalies"])
    print("Stable but suspicious :", summary["stable_but_suspicious"])

    print()
    print("Top anomalies:")
    display_cols = [
        c for c in [
            "CPTE",
            "PERIODE",
            "ANOMALY_SCORE",
            "ANOMALY_LEVEL",
            "RISK_SCORE",
            "NBRJDEP",
            "RISK_BRUT",
            "ANOMALY_ACTION",
        ] if c in result.columns
    ]
    print(result[display_cols].head(10).to_string(index=False))


if __name__ == "__main__":
    main()