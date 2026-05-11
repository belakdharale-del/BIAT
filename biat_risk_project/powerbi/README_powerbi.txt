========================================================
BIAT Risk Monitor — Power BI Integration Notes
========================================================

Power BI dashboards are complementary to the Streamlit application.

COMPLEMENTARITY:
----------------

Power BI is used for:
- Managerial decision dashboards (C-level, direction)
- Global risk portfolio reporting (monthly/quarterly)
- Trend analysis across multiple years
- Automatic scheduled refresh from CSV exports
- Embedded dashboards in banking portals (Power BI Embedded)
- Cross-filter visuals for ad-hoc exploration

Streamlit is used for:
- Operational client-level exploration
- Real-time clients to notify list
- Individual client profile (Fiche Client 360°)
- Action prioritization and follow-up simulation
- Rule-based chatbot assistant (Assistant BIAT Risk)
- Daily operational use by account managers

INTEGRATION:
------------

The following CSV outputs can be connected directly to Power BI Desktop:

1. outputs/scoring_clients.csv
   → Risk score per client per period
   → Use for: score distribution, alert level trends

2. outputs/scoring_evolution.csv
   → Month-over-month transitions
   → Use for: Sankey diagram, evolution KPIs

3. outputs/clients_a_notifier.csv
   → Prioritized contact list
   → Use for: operational manager dashboards

4. outputs/model_comparison.csv
   → Model performance metrics
   → Use for: technical validation slides

SETUP IN POWER BI:
------------------
1. Open Power BI Desktop
2. Get Data → Text/CSV → Select outputs/*.csv
3. Transform Data → Set correct types for PERIODE column (Date)
4. Create relationships between tables on CPTE + PERIODE
5. Build visuals using the BIAT color palette:
   - Critique: #ef4444
   - Élevé: #f97316
   - Moyen: #eab308
   - Faible: #22c55e

FUTURE IMPROVEMENTS:
--------------------
- Direct SQL connection to bank database
- Scheduled daily refresh via Power BI Service
- Row-level security (RLS) per portfolio manager
- Mobile layout for field agents
- Power BI Embedded in banking portal
