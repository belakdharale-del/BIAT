"""
Script 5: Build Evolution
Computes month-over-month transitions and builds clients_a_notifier.csv
"""
import os
import pandas as pd
import numpy as np

ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IN_PATH   = os.path.join(ROOT, "outputs", "scoring_clients.csv")
EVO_PATH  = os.path.join(ROOT, "outputs", "scoring_evolution.csv")
NOTIF_PATH= os.path.join(ROOT, "outputs", "clients_a_notifier.csv")

RISK_RANK = {"Faible": 1, "Moyen": 2, "Élevé": 3, "Critique": 4}


def get_evolution(row) -> str:
    prev = row["niveau_precedent"]
    curr = row["niveau_alerte"]
    if pd.isna(prev) or prev == "":
        return "Nouveau client"
    r_prev = RISK_RANK.get(prev, 0)
    r_curr = RISK_RANK.get(curr, 0)
    if r_curr > r_prev:   return "Aggravation"
    elif r_curr < r_prev: return "Amélioration"
    else:                 return "Stable"


def get_priority(row) -> str:
    niveau = row.get("niveau_alerte", "")
    score  = row.get("score_pct", 0)
    evol   = row.get("evolution", "")
    if niveau == "Critique" and score >= 95:    return "Priorité 1"
    elif niveau == "Critique":                  return "Priorité 2"
    elif niveau == "Élevé" and score >= 75:     return "Priorité 3"
    elif niveau == "Élevé":                     return "Priorité 4"
    elif niveau == "Moyen" and (evol == "Aggravation" or score >= 60): return "Priorité 5"
    else:                                       return "Surveillance"


def main():
    print(f"📂  Chargement : {IN_PATH}")
    df = pd.read_csv(IN_PATH, parse_dates=["PERIODE"])
    df.sort_values(["CPTE", "PERIODE"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # ── Previous alert level ─────────────────────────────────────────────────
    df["niveau_precedent"] = df.groupby("CPTE")["niveau_alerte"].shift(1).fillna("")
    df["transition"] = df.apply(
        lambda r: f"{r['niveau_precedent']} → {r['niveau_alerte']}"
                  if r["niveau_precedent"] else f"Nouveau → {r['niveau_alerte']}",
        axis=1
    )
    df["evolution"] = df.apply(get_evolution, axis=1)

    df.to_csv(EVO_PATH, index=False)
    print(f"  💾 scoring_evolution.csv sauvegardé : {len(df):,} lignes")

    # ── Clients à notifier ────────────────────────────────────────────────────
    latest_period = df["PERIODE"].max()
    notif = df[
        (df["PERIODE"] == latest_period) &
        (df["niveau_alerte"].isin(["Moyen", "Élevé", "Critique"]))
    ].copy()

    notif["priorite_intervention"] = notif.apply(get_priority, axis=1)
    notif["statut_suivi"]          = "À contacter"

    # Sort: priority asc, score desc, NBRJDEP desc
    priority_order = {"Priorité 1": 1, "Priorité 2": 2, "Priorité 3": 3,
                      "Priorité 4": 4, "Priorité 5": 5, "Surveillance": 6}
    notif["_sort_priority"] = notif["priorite_intervention"].map(priority_order).fillna(9)
    notif.sort_values(
        ["_sort_priority", "score_pct", "NBRJDEP"],
        ascending=[True, False, False],
        inplace=True
    )
    notif.drop(columns=["_sort_priority"], inplace=True)
    notif.reset_index(drop=True, inplace=True)

    notif.to_csv(NOTIF_PATH, index=False)

    # ── Diagnostics ───────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  ✅  ÉVOLUTION & NOTIFICATION TERMINÉES")
    print(f"{'='*55}")
    print(f"  Dernière période       : {latest_period.date()}")
    print(f"  Clients à notifier     : {len(notif):,}")
    print(f"  Distribution niveaux   :\n{notif['niveau_alerte'].value_counts()}")
    print(f"  Distribution priorités :\n{notif['priorite_intervention'].value_counts()}")
    print(f"  Fichier évolution      : {EVO_PATH}")
    print(f"  Fichier notification   : {NOTIF_PATH}")

if __name__ == "__main__":
    main()
