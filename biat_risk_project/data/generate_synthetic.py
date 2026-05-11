"""
Synthetic data generator for BIAT Risk Monitor.
Generates realistic banking data when real Excel file is unavailable.
"""
import numpy as np
import pandas as pd
import os

def generate_synthetic_data(n_clients=800, n_months=24, seed=42):
    np.random.seed(seed)

    periods = pd.date_range("2023-01-01", periods=n_months, freq="MS")
    cpte_ids = [f"CPTE_{str(i).zfill(6)}" for i in range(1, n_clients + 1)]

    genders = ["M", "F"]
    sectors = ["Commerce", "Agriculture", "Industrie", "Services", "Administration", "Artisanat"]
    marital = ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf/Veuve"]
    employment = ["Salarié", "Indépendant", "Fonctionnaire", "Retraité", "Sans emploi"]
    post_codes = [str(i) for i in range(1000, 9999, 500)]

    rows = []
    for cpte in cpte_ids:
        dob = pd.Timestamp("1960-01-01") + pd.Timedelta(days=int(np.random.uniform(0, 365 * 45)))
        gender = np.random.choice(genders)
        sector = np.random.choice(sectors)
        ms = np.random.choice(marital)
        emp = np.random.choice(employment)
        pc = np.random.choice(post_codes)

        risk_profile = np.random.choice(["low", "medium", "high"], p=[0.55, 0.30, 0.15])
        base_nbrjdep = {"low": 1, "medium": 8, "high": 18}[risk_profile]
        base_risk_brut = {"low": 0, "medium": 200, "high": 800}[risk_profile]
        base_mvt = np.random.uniform(2000, 20000)
        base_net = np.random.uniform(500, 5000)

        for periode in periods:
            noise = np.random.normal(0, 1)
            nbrjdep = max(0, min(31, int(base_nbrjdep + noise * 3)))
            risk_brut = max(0, base_risk_brut + np.random.uniform(-100, 200))
            mvt = max(0, base_mvt + np.random.normal(0, base_mvt * 0.2))
            net_monthly = max(0, base_net + np.random.normal(0, base_net * 0.1))
            nbrjdeb = max(0, nbrjdep - np.random.randint(0, 3))

            rows.append({
                "PERIODE": periode,
                "CPTE": cpte,
                "NBRJDEP": nbrjdep,
                "NBRJDEB": nbrjdeb,
                "RISK_BRUT": round(risk_brut, 2),
                "MVT": round(mvt, 2),
                "NET_MONTHLY": round(net_monthly, 2),
                "DATE_OF_BIRTH": dob,
                "GENDER": gender,
                "SECTOR": sector,
                "MARITAL_STATUS": ms,
                "EMPLOYMENT_STATUS": emp,
                "POST_CODE": pc,
            })

    df = pd.DataFrame(rows)
    os.makedirs(os.path.join(os.path.dirname(__file__), "..","data"), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), "f1020232025_3.xlsx")
    df.to_excel(out_path, index=False)
    print(f"Synthetic data generated: {len(df)} rows → {out_path}")
    return df

if __name__ == "__main__":
    generate_synthetic_data()
