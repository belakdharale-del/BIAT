"""
Script 1: Data Preparation
Loads raw Excel, normalizes, cleans, and saves prepared_data.csv
"""
import os, sys
import pandas as pd
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(ROOT, "data", "f1020232025_3.xlsx")
OUT_PATH  = os.path.join(ROOT, "outputs", "prepared_data.csv")

FINANCIAL_COLS = ["NBRJDEP", "NBRJDEB", "RISK_BRUT", "MVT", "NET_MONTHLY"]
CAT_COLS       = ["GENDER", "SECTOR", "MARITAL_STATUS", "EMPLOYMENT_STATUS", "POST_CODE"]


def main():
    os.makedirs(os.path.join(ROOT, "outputs"), exist_ok=True)

    # ── 0. Generate synthetic data if Excel missing ─────────────────────────
    if not os.path.exists(DATA_PATH):
        print("⚠️  Fichier Excel introuvable. Génération de données synthétiques...")
        sys.path.insert(0, os.path.join(ROOT, "data"))
        from generate_synthetic import generate_synthetic_data
        generate_synthetic_data()

    # ── 1. Load ──────────────────────────────────────────────────────────────
    print(f"📂  Chargement : {DATA_PATH}")
    df = pd.read_excel(DATA_PATH, engine="openpyxl")
    print(f"    Lignes initiales : {len(df):,}")

    # ── 2. Normalize column names ────────────────────────────────────────────
    df.columns = (
        df.columns.str.strip()
                  .str.replace(r"[\s\-]+", "_", regex=True)
                  .str.upper()
    )
    print(f"    Colonnes : {list(df.columns)}")

    # ── 3. Detect essential columns ──────────────────────────────────────────
    if "PERIODE" not in df.columns:
        raise ValueError("Colonne PERIODE introuvable.")
    if "CPTE" not in df.columns:
        raise ValueError("Colonne CPTE introuvable.")
    has_dob = "DATE_OF_BIRTH" in df.columns

    # ── 4. Convert dates ─────────────────────────────────────────────────────
    df["PERIODE"] = pd.to_datetime(df["PERIODE"], errors="coerce")
    if has_dob:
        df["DATE_OF_BIRTH"] = pd.to_datetime(df["DATE_OF_BIRTH"], errors="coerce")

    # ── 5. Drop rows with missing identifiers ────────────────────────────────
    before = len(df)
    df.dropna(subset=["PERIODE", "CPTE"], inplace=True)
    print(f"    Lignes supprimées (identifiants manquants) : {before - len(df)}")

    # ── 6 & 7. Fill and convert financial columns ────────────────────────────
    for col in FINANCIAL_COLS:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ── 8. Cap NBRJDEP ───────────────────────────────────────────────────────
    df["NBRJDEP"] = df["NBRJDEP"].clip(0, 31)

    # ── 9. Age ───────────────────────────────────────────────────────────────
    if has_dob:
        df["AGE"] = ((df["PERIODE"] - df["DATE_OF_BIRTH"]).dt.days / 365.25).round(0)
        df["AGE"] = df["AGE"].clip(18, 80).fillna(40).astype(int)
    else:
        df["AGE"] = 40

    # ── 10. Fill categorical columns ─────────────────────────────────────────
    for col in CAT_COLS:
        if col not in df.columns:
            df[col] = "Unknown"
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()
        df[col] = df[col].replace("", "Unknown")

    # ── 11. Sort ─────────────────────────────────────────────────────────────
    df.sort_values(["CPTE", "PERIODE"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # ── 12. Save ─────────────────────────────────────────────────────────────
    df.to_csv(OUT_PATH, index=False)

    # ── Diagnostics ──────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  ✅  PRÉPARATION TERMINÉE")
    print(f"{'='*55}")
    print(f"  Lignes finales       : {len(df):,}")
    print(f"  Comptes uniques      : {df['CPTE'].nunique():,}")
    print(f"  Période min          : {df['PERIODE'].min().date()}")
    print(f"  Période max          : {df['PERIODE'].max().date()}")
    print(f"  Valeurs manquantes   :\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"  Fichier de sortie    : {OUT_PATH}")

if __name__ == "__main__":
    main()
