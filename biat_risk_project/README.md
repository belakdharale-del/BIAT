# BIAT Risk Monitor

**Système de prédiction du risque de dépassement de découvert à 30 jours**

PFE 2025 — Biat Tunisie — Data Science & Business Intelligence

---

## Objectif

Ce projet prédit avec 30 jours d'avance si un client BIAT va dépasser son découvert autorisé.
Il transforme les données bancaires historiques en alertes opérationnelles pour les gestionnaires
de comptes, analystes risques et directeurs.

---

## Contexte Métier

- Analyse des données transactionnelles mensuelles
- Score de risque de 0% à 100% par client
- 4 niveaux d'alerte : Faible, Moyen, Élevé, Critique
- Actions recommandées associées à chaque niveau
- Interface Streamlit pour usage opérationnel quotidien
- Complémentaire avec Power BI pour le reporting managérial

---

## Architecture du Projet

```
biat_risk_project/
├── app/                        # Application Streamlit
│   ├── Home.py                 # Page d'accueil
│   ├── pages/
│   │   ├── 1_Dashboard_global.py
│   │   ├── 2_Evolution_risque.py
│   │   ├── 3_Clients_a_notifier.py
│   │   ├── 4_Fiche_client.py
│   │   ├── 5_Performance_modele.py
│   │   └── 6_Chatbot.py
│   └── utils/
│       ├── style.py            # Design system
│       ├── data_loader.py      # Chargement centralisé
│       └── business_rules.py   # Règles métier
├── data/
│   └── f1020232025_3.xlsx      # Données brutes (Excel)
├── src/                        # Pipeline de données
│   ├── 1_data_preparation.py
│   ├── 2_feature_engineering.py
│   ├── 3_train_models.py
│   ├── 4_scoring.py
│   └── 5_build_evolution.py
├── outputs/                    # CSV générés
├── models/                     # Modèle LightGBM sauvegardé
├── powerbi/                    # Notes intégration Power BI
└── requirements.txt
```

---

## Technologies

| Catégorie | Technologie |
|-----------|-------------|
| ML | LightGBM, Scikit-learn |
| Data | Pandas, NumPy, OpenPyXL |
| App | Streamlit, Plotly |
| Explainability | SHAP (optionnel) |
| Reporting | Power BI |

---

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows
source .venv/bin/activate      # Linux/Mac

pip install -r requirements.txt
```

---

## Exécution du Pipeline

```bash
python src/1_data_preparation.py
python src/2_feature_engineering.py
python src/3_train_models.py
python src/4_scoring.py
python src/5_build_evolution.py
```

> Si le fichier Excel `data/f1020232025_3.xlsx` est absent, le script 1 génère automatiquement
> des données synthétiques réalistes pour la démonstration.

---

## Lancement de l'Application

```bash
streamlit run app/Home.py
```

---

## Pages de l'Application

| Page | Description |
|------|-------------|
| 🏠 Accueil | KPIs globaux, présentation du projet |
| 📊 Dashboard Global | Vue managériale, distribution du risque |
| 📈 Évolution du Risque | Transitions et tendances comportementales |
| 🔔 Clients à Notifier | Liste opérationnelle priorisée + export CSV |
| 👤 Fiche Client | Profil 360° individuel + simulation suivi |
| 🎯 Performance Modèle | Métriques ML, matrice de confusion |
| 🤖 Assistant BIAT Risk | Chatbot métier sans API externe |

---

## Niveaux de Risque

| Niveau | Score | Action |
|--------|-------|--------|
| Faible | < 40% | Aucune action urgente |
| Moyen | 40–65% | Surveillance mensuelle |
| Élevé | 65–85% | Appel préventif sous 48h |
| Critique | ≥ 85% | Intervention immédiate aujourd'hui |

---

## Priorités d'Intervention

| Priorité | Critère |
|----------|---------|
| Priorité 1 | Critique et score ≥ 95% |
| Priorité 2 | Critique et score < 95% |
| Priorité 3 | Élevé et score ≥ 75% |
| Priorité 4 | Élevé |
| Priorité 5 | Moyen avec aggravation ou score ≥ 60% |
| Surveillance | Autres cas |

---

## Améliorations Futures

- [ ] Explications SHAP par client (SHAP-ready)
- [ ] Connexion base de données bancaire en direct
- [ ] Authentification par rôle (gestionnaire / analyste / directeur)
- [ ] Power BI Embedded dans le portail bancaire
- [ ] Scoring mensuel automatisé (scheduler)
- [ ] Notifications email/SMS automatiques
- [ ] API REST pour intégration core banking
