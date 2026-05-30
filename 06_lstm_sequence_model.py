# 06_lstm_sequence_model.py — BIAT Risk Monitor
# Module expérimental : analyse temporelle par LSTM
#
# Objectif :
#   Utiliser les séquences mensuelles d'un client pour prédire TARGET_RISK_30J.
#   Exemple : 6 mois d'historique -> risque du mois suivant.
#
# Entrée :
#   dataset_ml_clean.csv
#
# Sorties :
#   ml_outputs/lstm_metrics.csv
#   ml_outputs/lstm_predictions.csv
#   ml_outputs/lstm_model.keras

import argparse
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping


def choose_numeric_features(df):
    excluded = {
        "TARGET_RISK_30J",
        "NEXT_PERIODE",
        "NEXT_NBRJDEP",
        "NEXT_RISK_BRUT",
        "CPTE",
        "CODE_CLIENT",
        "PERIODE",
    }

    candidates = [c for c in df.columns if c not in excluded]

    numeric_cols = []
    for col in candidates:
        converted = pd.to_numeric(df[col], errors="coerce")
        # keep columns that are mostly numeric
        if converted.notna().mean() >= 0.70:
            df[col] = converted
            numeric_cols.append(col)

    return numeric_cols


def build_sequences(df, features, sequence_length):
    """
    For each client:
      rows M-5 ... M -> target at M (TARGET_RISK_30J)
    Since TARGET_RISK_30J is already created as future 30-day risk,
    the sequence ending at M predicts the next-month risk from M.
    """
    X_list = []
    y_list = []
    meta_list = []

    df = df.sort_values(["CPTE", "PERIODE"]).reset_index(drop=True)

    for cpte, group in df.groupby("CPTE", sort=False):
        group = group.sort_values("PERIODE")

        if len(group) < sequence_length:
            continue

        values = group[features].values.astype("float32")
        targets = group["TARGET_RISK_30J"].values.astype("int32")
        periodes = group["PERIODE"].values
        codes = group["CODE_CLIENT"].values if "CODE_CLIENT" in group.columns else [""] * len(group)

        for end_idx in range(sequence_length - 1, len(group)):
            start_idx = end_idx - sequence_length + 1

            X_list.append(values[start_idx:end_idx + 1])
            y_list.append(targets[end_idx])

            meta_list.append({
                "CPTE": cpte,
                "CODE_CLIENT": codes[end_idx],
                "PERIODE": periodes[end_idx],
            })

    if not X_list:
        raise ValueError("No sequences created. Try a smaller sequence length.")

    X = np.stack(X_list)
    y = np.asarray(y_list, dtype="int32")
    meta = pd.DataFrame(meta_list)

    return X, y, meta


def temporal_split(X, y, meta, train_ratio=0.80):
    meta = meta.copy()
    meta["PERIODE"] = pd.to_datetime(meta["PERIODE"], errors="coerce")

    unique_periods = sorted(meta["PERIODE"].dropna().unique())
    split_period = unique_periods[int(len(unique_periods) * train_ratio)]

    train_mask = meta["PERIODE"] < split_period
    test_mask = meta["PERIODE"] >= split_period

    return (
        X[train_mask.values],
        X[test_mask.values],
        y[train_mask.values],
        y[test_mask.values],
        meta[train_mask.values].reset_index(drop=True),
        meta[test_mask.values].reset_index(drop=True),
        split_period,
    )


def scale_3d_sequences(X_train, X_test):
    """
    StandardScaler expects 2D.
    We reshape:
      (samples, timesteps, features) -> (samples*timesteps, features)
    Then reshape back.
    """
    n_train, t, f = X_train.shape
    n_test = X_test.shape[0]

    scaler = StandardScaler()

    X_train_2d = X_train.reshape(-1, f)
    X_test_2d = X_test.reshape(-1, f)

    X_train_scaled = scaler.fit_transform(X_train_2d).reshape(n_train, t, f)
    X_test_scaled = scaler.transform(X_test_2d).reshape(n_test, t, f)

    return X_train_scaled.astype("float32"), X_test_scaled.astype("float32")


def create_lstm_model(sequence_length, n_features):
    model = Sequential([
        Input(shape=(sequence_length, n_features)),
        LSTM(64, return_sequences=True),
        Dropout(0.25),
        LSTM(32),
        Dropout(0.25),
        Dense(16, activation="relu"),
        Dense(1, activation="sigmoid"),
    ])

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.Precision(name="precision"),
        ],
    )

    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="dataset_ml_clean.csv")
    parser.add_argument("--output-dir", default="ml_outputs")
    parser.add_argument("--sequence-length", type=int, default=6)
    parser.add_argument("--threshold", type=float, default=0.70)
    parser.add_argument("--max-sequences", type=int, default=200000)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=256)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    print("[1/7] Loading dataset")
    df = pd.read_csv(input_path, low_memory=False)
    df["PERIODE"] = pd.to_datetime(df["PERIODE"], errors="coerce")
    df = df.dropna(subset=["PERIODE", "CPTE", "TARGET_RISK_30J"]).copy()

    print("      Rows:", len(df))
    print("      Clients:", df["CPTE"].nunique())
    print("      Periods:", df["PERIODE"].nunique())

    print("[2/7] Selecting numeric sequence features")
    features = choose_numeric_features(df)

    # Fill missing values after numeric conversion
    df[features] = df[features].replace([np.inf, -np.inf], np.nan)
    df[features] = df[features].fillna(df[features].median(numeric_only=True))

    print("      Number of features:", len(features))
    print("      First features:", features[:10])

    print("[3/7] Building sequences")
    X, y, meta = build_sequences(df, features, args.sequence_length)

    print("      Sequence shape:", X.shape)
    print("      Target distribution:")
    print(pd.Series(y).value_counts(normalize=True).round(4))

    if args.max_sequences and args.max_sequences > 0 and args.max_sequences < len(y):
        print(f"      Sampling max sequences: {args.max_sequences:,}")
        rng = np.random.default_rng(42)

        # stratified-like sampling by class
        idx0 = np.where(y == 0)[0]
        idx1 = np.where(y == 1)[0]
        n1 = min(len(idx1), int(args.max_sequences * (len(idx1) / len(y))))
        n0 = args.max_sequences - n1

        sampled_idx = np.concatenate([
            rng.choice(idx0, size=min(n0, len(idx0)), replace=False),
            rng.choice(idx1, size=min(n1, len(idx1)), replace=False),
        ])
        sampled_idx = np.sort(sampled_idx)

        X = X[sampled_idx]
        y = y[sampled_idx]
        meta = meta.iloc[sampled_idx].reset_index(drop=True)

        print("      Sampled sequence shape:", X.shape)

    print("[4/7] Temporal split")
    X_train, X_test, y_train, y_test, meta_train, meta_test, split_period = temporal_split(X, y, meta)

    print("      Split period:", pd.to_datetime(split_period).date())
    print("      Train:", X_train.shape)
    print("      Test :", X_test.shape)

    print("[5/7] Scaling sequences")
    X_train, X_test = scale_3d_sequences(X_train, X_test)

    print("[6/7] Training LSTM")
    model = create_lstm_model(args.sequence_length, X_train.shape[2])

    callbacks = [
        EarlyStopping(
            monitor="val_auc",
            patience=3,
            mode="max",
            restore_best_weights=True,
        )
    ]

    history = model.fit(
        X_train,
        y_train,
        validation_split=0.15,
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks,
        verbose=1,
    )

    print("[7/7] Evaluating and saving outputs")
    y_score = model.predict(X_test, batch_size=args.batch_size).ravel()
    y_score = np.clip(y_score, 0.0, 0.95)  # avoid 100% display
    y_pred = (y_score >= args.threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    metrics = {
        "model": "LSTM_Sequence_Model",
        "sequence_length": args.sequence_length,
        "threshold": args.threshold,
        "roc_auc": roc_auc_score(y_test, y_score),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "accuracy": accuracy_score(y_test, y_pred),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "train_sequences": int(len(y_train)),
        "test_sequences": int(len(y_test)),
    }

    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(output_dir / "lstm_metrics.csv", index=False)

    predictions = meta_test.copy()
    predictions["LSTM_RISK_SCORE"] = y_score
    predictions["LSTM_RISK_SCORE_PERCENT"] = np.round(y_score * 100, 1)
    predictions["LSTM_PREDICTED_RISK"] = y_pred
    predictions["TARGET_RISK_30J"] = y_test

    predictions.to_csv(output_dir / "lstm_predictions.csv", index=False)

    model.save(output_dir / "lstm_model.keras")

    print("\n✅ LSTM training completed")
    print(f"ROC-AUC  : {metrics['roc_auc']:.4f}")
    print(f"Recall   : {metrics['recall']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"F1-score : {metrics['f1_score']:.4f}")
    print(f"Accuracy : {metrics['accuracy']:.4f}")
    print(f"Confusion: TN={tn} FP={fp} FN={fn} TP={tp}")

    print("\nSaved:")
    print("  ml_outputs/lstm_metrics.csv")
    print("  ml_outputs/lstm_predictions.csv")
    print("  ml_outputs/lstm_model.keras")


if __name__ == "__main__":
    main()
