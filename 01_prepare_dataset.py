# 01_prepare_dataset.py
# BIAT Risk Monitor - Dataset preparation for ML
# Goal: create a clean monthly client dataset and TARGET_RISK_30J.
#
# Usage from your project root:
#   python 01_prepare_dataset.py --input f1020232025_3.csv --output dataset_ml_clean.csv
#
# If your CSV is in another folder:
#   python 01_prepare_dataset.py --input data/f1020232025_3.csv --output data/dataset_ml_clean.csv

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def month_diff(current_date: pd.Series, next_date: pd.Series) -> pd.Series:
    """Return month difference between two datetime series."""
    return (
        (next_date.dt.year - current_date.dt.year) * 12
        + (next_date.dt.month - current_date.dt.month)
    )


def safe_to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Convert selected columns to numeric, keeping invalid values as NaN."""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and rename the blank account column to CPTE."""
    df = df.copy()

    # Strip column names but preserve mapping first
    original_columns = list(df.columns)

    # In this dataset, the account column is named exactly "  " / blank spaces.
    blank_like_columns = [col for col in original_columns if str(col).strip() == ""]
    if blank_like_columns:
        df = df.rename(columns={blank_like_columns[0]: "CPTE"})

    # Normalize all column names after the blank-column correction
    df.columns = [str(c).strip().upper().replace(" ", "_") for c in df.columns]

    # Safety fallback if CPTE was not detected
    if "CPTE" not in df.columns:
        raise ValueError(
            "Account column CPTE was not found. "
            "Check the CSV columns and rename the account column to CPTE."
        )

    return df


def prepare_dataset(input_path: str, output_path: str) -> pd.DataFrame:
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"[1/9] Loading CSV: {input_path}")
    df = pd.read_csv(input_path, low_memory=False)
    print(f"      Raw shape: {df.shape}")

    print("[2/9] Cleaning column names")
    df = clean_column_names(df)

    print("[3/9] Parsing dates")
    df["PERIODE"] = pd.to_datetime(df["PERIODE"], errors="coerce")

    if "DATE_OF_BIRTH" in df.columns:
        df["DATE_OF_BIRTH"] = pd.to_datetime(df["DATE_OF_BIRTH"], errors="coerce")
    else:
        df["DATE_OF_BIRTH"] = pd.NaT

    df = df.dropna(subset=["PERIODE", "CPTE"])
    df["CPTE"] = df["CPTE"].astype(str).str.strip()

    print("[4/9] Converting numeric columns")
    numeric_columns = [
        "NBRJDEP",
        "NBRJDEB",
        "MVT",
        "RISK_BRUT",
        "SALARY",
        "NET_MONTHLY_IN",
        "POST_CODE",
        "JOB_TITLE",
        "CODE_CLIENT",
    ]
    df = safe_to_numeric(df, numeric_columns)

    # Missing-value flags: useful for ML because missing values can carry signal
    for col in ["RISK_BRUT", "SALARY", "NET_MONTHLY_IN", "DATE_OF_BIRTH"]:
        if col in df.columns:
            df[f"{col}_MISSING"] = df[col].isna().astype(int)

    print("[5/9] Feature engineering")
    # Basic imputations
    for col in ["NBRJDEP", "NBRJDEB", "MVT", "RISK_BRUT", "SALARY", "NET_MONTHLY_IN"]:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Age at the observation month
    df["AGE_CLIENT"] = np.where(
        df["DATE_OF_BIRTH"].notna(),
        (df["PERIODE"] - df["DATE_OF_BIRTH"]).dt.days / 365.25,
        np.nan,
    )
    df["AGE_CLIENT"] = df["AGE_CLIENT"].clip(lower=18, upper=100)
    df["AGE_CLIENT"] = df["AGE_CLIENT"].fillna(df["AGE_CLIENT"].median())

    # Account seniority inside the available dataset
    df = df.sort_values(["CPTE", "PERIODE"]).reset_index(drop=True)
    df["OBSERVATION_NUMBER"] = df.groupby("CPTE").cumcount() + 1

    # Ratios and transformed features
    df["HAS_OVERDRAFT_DAYS"] = (df["NBRJDEP"] > 0).astype(int)
    df["HAS_RISK_BRUT"] = (df["RISK_BRUT"] > 0).astype(int)

    df["MVT_ABS"] = df["MVT"].abs()
    df["LOG_MVT_ABS"] = np.log1p(df["MVT_ABS"])
    df["LOG_RISK_BRUT"] = np.log1p(df["RISK_BRUT"].clip(lower=0))
    df["LOG_SALARY"] = np.log1p(df["SALARY"].clip(lower=0))
    df["LOG_NET_MONTHLY_IN"] = np.log1p(df["NET_MONTHLY_IN"].clip(lower=0))

    df["RISK_TO_INCOME_RATIO"] = df["RISK_BRUT"] / (df["NET_MONTHLY_IN"].replace(0, np.nan))
    df["RISK_TO_INCOME_RATIO"] = df["RISK_TO_INCOME_RATIO"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["RISK_TO_INCOME_RATIO"] = df["RISK_TO_INCOME_RATIO"].clip(upper=50)

    df["DEP_TO_DEB_RATIO"] = df["NBRJDEP"] / (df["NBRJDEB"].replace(0, np.nan))
    df["DEP_TO_DEB_RATIO"] = df["DEP_TO_DEB_RATIO"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["DEP_TO_DEB_RATIO"] = df["DEP_TO_DEB_RATIO"].clip(upper=10)

    # Lag features: only past/current information, no future leakage
    grouped = df.groupby("CPTE", group_keys=False)

    for col in ["NBRJDEP", "NBRJDEB", "MVT", "RISK_BRUT"]:
        df[f"{col}_LAG1"] = grouped[col].shift(1).fillna(0)
        df[f"{col}_LAG2"] = grouped[col].shift(2).fillna(0)
        df[f"{col}_ROLL3_MEAN"] = (
            grouped[col]
            .shift(1)
            .rolling(window=3, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
            .fillna(0)
        )

    df["NBRJDEP_TREND"] = df["NBRJDEP"] - df["NBRJDEP_LAG1"]
    df["RISK_BRUT_TREND"] = df["RISK_BRUT"] - df["RISK_BRUT_LAG1"]

    print("[6/9] Creating TARGET_RISK_30J")
    # Future values for the next observed monthly period
    df["NEXT_PERIODE"] = grouped["PERIODE"].shift(-1)
    df["NEXT_NBRJDEP"] = grouped["NBRJDEP"].shift(-1)
    df["NEXT_RISK_BRUT"] = grouped["RISK_BRUT"].shift(-1)

    df["MONTH_GAP_TO_NEXT"] = month_diff(df["PERIODE"], df["NEXT_PERIODE"])

    # Keep only rows where the next row is truly the next month.
    # This avoids labeling March with June if intermediate months are missing.
    df = df[df["MONTH_GAP_TO_NEXT"] == 1].copy()

    # Target definition:
    # 1 = client will show overdraft/risk signal next month
    # 0 = no overdraft/risk signal next month
    df["TARGET_RISK_30J"] = (
        (df["NEXT_NBRJDEP"].fillna(0) > 0)
        | (df["NEXT_RISK_BRUT"].fillna(0) > 0)
    ).astype(int)

    print("[7/9] Cleaning categorical columns")
    categorical_columns = [
        "SECTOR",
        "MARITAL_STATUS",
        "GENDER",
        "INDUSTRY",
        "EMPLOYMENT_STATUS",
        "MKT",
    ]

    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype("string").fillna("UNKNOWN").str.strip()
            df[col] = df[col].replace({"": "UNKNOWN", "nan": "UNKNOWN", "None": "UNKNOWN"})

    print("[8/9] Selecting final columns")
    id_columns = [
        "PERIODE",
        "CPTE",
        "CODE_CLIENT",
    ]

    base_features = [
        "NBRJDEP",
        "NBRJDEB",
        "MVT",
        "RISK_BRUT",
        "SALARY",
        "NET_MONTHLY_IN",
        "POST_CODE",
        "JOB_TITLE",
        "AGE_CLIENT",
        "OBSERVATION_NUMBER",
        "HAS_OVERDRAFT_DAYS",
        "HAS_RISK_BRUT",
        "MVT_ABS",
        "LOG_MVT_ABS",
        "LOG_RISK_BRUT",
        "LOG_SALARY",
        "LOG_NET_MONTHLY_IN",
        "RISK_TO_INCOME_RATIO",
        "DEP_TO_DEB_RATIO",
        "NBRJDEP_LAG1",
        "NBRJDEP_LAG2",
        "NBRJDEP_ROLL3_MEAN",
        "NBRJDEB_LAG1",
        "NBRJDEB_LAG2",
        "NBRJDEB_ROLL3_MEAN",
        "MVT_LAG1",
        "MVT_LAG2",
        "MVT_ROLL3_MEAN",
        "RISK_BRUT_LAG1",
        "RISK_BRUT_LAG2",
        "RISK_BRUT_ROLL3_MEAN",
        "NBRJDEP_TREND",
        "RISK_BRUT_TREND",
        "RISK_BRUT_MISSING",
        "SALARY_MISSING",
        "NET_MONTHLY_IN_MISSING",
        "DATE_OF_BIRTH_MISSING",
    ]

    final_categorical = [col for col in categorical_columns if col in df.columns]

    target_and_audit = [
        "NEXT_PERIODE",
        "NEXT_NBRJDEP",
        "NEXT_RISK_BRUT",
        "TARGET_RISK_30J",
    ]

    final_columns = [
        col for col in (id_columns + final_categorical + base_features + target_and_audit)
        if col in df.columns
    ]

    final_df = df[final_columns].copy()

    # Final safety cleaning for numeric values
    numeric_final = final_df.select_dtypes(include=[np.number]).columns
    final_df[numeric_final] = final_df[numeric_final].replace([np.inf, -np.inf], np.nan)
    final_df[numeric_final] = final_df[numeric_final].fillna(0)

    print("[9/9] Saving clean dataset")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False, encoding="utf-8")

    print("\n✅ Dataset preparation completed")
    print(f"   Output file: {output_path}")
    print(f"   Clean shape: {final_df.shape}")
    print(f"   Clients: {final_df['CPTE'].nunique():,}")
    print(f"   Period min: {final_df['PERIODE'].min()}")
    print(f"   Period max: {final_df['PERIODE'].max()}")
    print(f"   Target distribution:")
    print(final_df["TARGET_RISK_30J"].value_counts(normalize=True).rename("ratio").round(4))
    print(final_df["TARGET_RISK_30J"].value_counts().rename("count"))

    return final_df


def main():
    parser = argparse.ArgumentParser(description="Prepare BIAT Risk Monitor ML dataset.")
    parser.add_argument(
        "--input",
        default="f1020232025_3.csv",
        help="Path to raw CSV file.",
    )
    parser.add_argument(
        "--output",
        default="dataset_ml_clean.csv",
        help="Path to output clean CSV file.",
    )

    args = parser.parse_args()
    prepare_dataset(args.input, args.output)


if __name__ == "__main__":
    main()

