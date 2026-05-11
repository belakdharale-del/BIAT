"""
Centralized business rules for BIAT Risk Monitor.
All risk thresholds and business logic lives here.
"""

RISK_THRESHOLDS = {
    "faible": (0, 40),
    "moyen": (40, 65),
    "eleve": (65, 85),
    "critique": (85, 101),
}

RISK_RANK = {
    "Faible": 1,
    "Moyen": 2,
    "Élevé": 3,
    "Critique": 4,
}

ACTIONS = {
    "Faible": "Aucune action urgente",
    "Moyen": "Surveillance mensuelle",
    "Élevé": "Appel préventif sous 48h",
    "Critique": "Intervention immédiate aujourd'hui",
}

ALERT_COLORS = {
    "Faible": "#22c55e",
    "Moyen": "#eab308",
    "Élevé": "#f97316",
    "Critique": "#ef4444",
}

ALERT_CSS = {
    "Faible": "faible",
    "Moyen": "moyen",
    "Élevé": "eleve",
    "Critique": "critique",
}


def get_risk_level(score_pct: float) -> str:
    if score_pct < 40:
        return "Faible"
    elif score_pct < 65:
        return "Moyen"
    elif score_pct < 85:
        return "Élevé"
    else:
        return "Critique"


def get_recommended_action(score_pct: float, evolution: str = None) -> str:
    level = get_risk_level(score_pct)
    action = ACTIONS.get(level, "Surveillance")
    if evolution == "Aggravation" and level in ("Moyen",):
        action = "Appel préventif sous 48h"
    return action


def get_priority(row) -> str:
    niveau = row.get("niveau_alerte", "")
    score = row.get("score_pct", 0)
    evolution = row.get("evolution", "")
    if niveau == "Critique" and score >= 95:
        return "Priorité 1"
    elif niveau == "Critique":
        return "Priorité 2"
    elif niveau == "Élevé" and score >= 75:
        return "Priorité 3"
    elif niveau == "Élevé":
        return "Priorité 4"
    elif niveau == "Moyen" and (evolution == "Aggravation" or score >= 60):
        return "Priorité 5"
    else:
        return "Surveillance"


def explain_risk(row) -> list:
    reasons = []
    nbrjdep = row.get("NBRJDEP", 0) or 0
    risk_brut = row.get("RISK_BRUT", 0) or 0
    avg_dep = row.get("AVG_DEP_3M", 0) or 0
    days_ovd = row.get("DAYS_OVD_6M", 0) or 0
    delta = row.get("DELTA_NBRJDEP", 0) or 0
    mois_consec = row.get("MOIS_CONSEC", 0) or 0

    if nbrjdep > 10:
        reasons.append("🔴 Nombre de jours à découvert élevé")
    elif nbrjdep > 5:
        reasons.append("🟠 Nombre de jours à découvert modéré")

    if risk_brut > 0:
        reasons.append(f"🔴 Montant de risque brut positif ({format_number(risk_brut)} DT)")

    if avg_dep > 8:
        reasons.append("🔴 Historique récent de découvert (moy. 3 mois élevée)")
    elif avg_dep > 4:
        reasons.append("🟡 Historique récent de découvert modéré")

    if days_ovd > 30:
        reasons.append("🔴 Exposition cumulée élevée sur 6 mois")

    if delta > 3:
        reasons.append("🔴 Aggravation récente du découvert")
    elif delta > 0:
        reasons.append("🟡 Légère augmentation du découvert ce mois")

    if mois_consec >= 4:
        reasons.append("🔴 Découvert persistant sur plusieurs mois consécutifs")
    elif mois_consec >= 2:
        reasons.append("🟡 Découvert observé plusieurs mois consécutifs")

    if not reasons:
        reasons.append("✅ Comportement financier globalement sain")

    return reasons


def format_number(value, decimals: int = 0) -> str:
    try:
        v = float(value)
        if decimals == 0:
            return f"{int(v):,}".replace(",", " ")
        return f"{v:,.{decimals}f}".replace(",", " ")
    except Exception:
        return str(value)
