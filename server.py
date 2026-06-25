import http.server
import socketserver
import os
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse


PORT = 5000
HOST = "0.0.0.0"
BASE_DIR = Path(__file__).resolve().parent


ROUTES = {
    "/": "login_biat_risk_monitor/code.html",
    "/login": "login_biat_risk_monitor/code.html",
    "/home": "home_biat_risk_monitor/code.html",
    "/dashboard": "global_dashboard_biat_risk_monitor/code.html",
    "/evolution": "risk_evolution_biat_risk_monitor/code.html",
    "/future": "future_prediction_biat_risk_monitor/code.html",
    "/notifications": "clients_notifier_biat_risk_monitor/code.html",
    "/client": "fiche_client_biat_risk_monitor/code.html",
    "/performance": "performance_mod_le_biat_risk_monitor/code.html",
    "/assistant": "assistant_ia_biat_risk_monitor/code.html",
}


# =========================================================
# OUTILS DE LECTURE
# =========================================================

def read_json(path, default):
    """
    Lecture sécurisée d'un fichier JSON.
    Si le fichier n'existe pas ou s'il est mal formé, on retourne default.
    """
    try:
        full_path = BASE_DIR / path

        if not full_path.exists():
            return default

        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return default


def safe_float(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(str(x).replace(",", "."))
    except Exception:
        return default


def normalize_text(value):
    return str(value or "").strip().upper()


def normalize_clients(raw):
    """
    Certains fichiers JSON contiennent directement une liste.
    D'autres contiennent un dictionnaire avec une clé clients/data/records.
    Cette fonction uniformise le format.
    """
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        for key in ["clients", "data", "records", "rows", "all_clients"]:
            value = raw.get(key)
            if isinstance(value, list):
                return value

    return []


def extract_list(raw):
    """
    Extraction générique d'une liste depuis un JSON.
    Utile pour anomalies, métriques ou prédictions.
    """
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        for key in [
            "clients",
            "data",
            "records",
            "rows",
            "anomalies",
            "all_future_predictions",
            "top_future_risk_clients",
            "predictions",
            "metrics",
            "model_metrics",
        ]:
            value = raw.get(key)
            if isinstance(value, list):
                return value

    return []


def get_client_id(client):
    return (
        client.get("cpte")
        or client.get("compte")
        or client.get("client_id")
        or client.get("id_client")
        or client.get("id")
        or "N/A"
    )


def get_score(client):
    return safe_float(
        client.get(
            "risk_score_percent",
            client.get(
                "score",
                client.get(
                    "score_risque",
                    client.get("risk_score", 0)
                )
            )
        )
    )


def get_level(client):
    return (
        client.get("alert_level")
        or client.get("niveau_risque")
        or client.get("risk_level")
        or client.get("level")
        or client.get("classe")
        or "N/A"
    )


def get_exposure(client):
    return safe_float(
        client.get(
            "risk_brut",
            client.get(
                "exposure",
                client.get(
                    "montant_exposition",
                    client.get("exposition", 0)
                )
            )
        )
    )


def format_money(value):
    try:
        return f"{float(value):,.2f} TND".replace(",", " ")
    except Exception:
        return f"{value} TND"


def is_critical(client):
    level = normalize_text(get_level(client))
    score = get_score(client)

    return (
        level in ["CRITICAL", "CRITIQUE", "CRITIQUE CLIENT", "VERY HIGH"]
        or score >= 85
    )


def is_high(client):
    level = normalize_text(get_level(client))
    score = get_score(client)

    return (
        level in ["WARNING", "HIGH", "ÉLEVÉ", "ELEVE", "ELEVÉ", "ALERTE"]
        or 65 <= score < 85
    )


def is_medium(client):
    level = normalize_text(get_level(client))
    score = get_score(client)

    return (
        level in ["MEDIUM", "MOYEN"]
        or 40 <= score < 65
    )


def is_low(client):
    level = normalize_text(get_level(client))
    score = get_score(client)

    return (
        level in ["LOW", "FAIBLE"]
        or score < 40
    )


# =========================================================
# CONTEXTE PORTEFEUILLE
# =========================================================

def build_portfolio_context(question=""):
    dashboard = read_json("attached_assets/dashboard_clients_full.json", {})
    anomalies_raw = read_json("attached_assets/anomaly_clients.json", {})
    metrics_raw = read_json("attached_assets/model_metrics.json", [])
    top_risky_raw = read_json("attached_assets/top_risky_clients.json", [])

    clients = normalize_clients(dashboard)
    anomaly_list = extract_list(anomalies_raw)
    metrics = extract_list(metrics_raw)

    if isinstance(top_risky_raw, list):
        top_risky_file = top_risky_raw
    else:
        top_risky_file = extract_list(top_risky_raw)

    total_rows = len(clients)
    unique_clients = len(
        set(str(get_client_id(c)) for c in clients if get_client_id(c) != "N/A")
    )

    critical = [c for c in clients if is_critical(c)]
    high = [c for c in clients if is_high(c)]
    medium = [c for c in clients if is_medium(c)]
    low = [c for c in clients if is_low(c)]

    if clients:
        avg_score = sum(get_score(c) for c in clients) / len(clients)
    else:
        avg_score = 0

    exposure = sum(get_exposure(c) for c in clients)

    top_clients = sorted(
        clients,
        key=lambda c: (get_score(c), get_exposure(c)),
        reverse=True,
    )[:30]

    selected_client = None
    cpte_match = re.search(r"CPTE[_-]?\d+", str(question).upper())

    if cpte_match:
        searched = cpte_match.group(0).replace("-", "_")

        for c in clients:
            if normalize_text(get_client_id(c)) == searched:
                selected_client = c
                break

    return {
        "portfolio_summary": {
            "total_rows": total_rows,
            "unique_clients": unique_clients,
            "critical_clients": len(critical),
            "high_risk_clients": len(high),
            "medium_clients": len(medium),
            "low_clients": len(low),
            "clients_to_notify": len(critical) + len(high),
            "average_score_percent": round(avg_score, 2),
            "total_exposure_tnd": round(exposure, 2),
        },
        "top_risky_clients": top_clients,
        "selected_client": selected_client,
        "anomaly_count": len(anomaly_list),
        "sample_anomalies": anomaly_list[:10],
        "model_metrics": metrics if metrics else metrics_raw,
        "top_risky_file": top_risky_file[:10] if isinstance(top_risky_file, list) else top_risky_file,
    }


# =========================================================
# CONTEXTE FUTURE PREDICTION
# =========================================================

def build_future_context():
    future = read_json("attached_assets/future_predictions.json", {})

    if isinstance(future, dict):
        summary = future.get("summary", {})

        rows = (
            future.get("all_future_predictions")
            or future.get("top_future_risk_clients")
            or future.get("predictions")
            or future.get("clients")
            or future.get("data")
            or []
        )

        top_rows = future.get("top_future_risk_clients") or rows[:200]

    elif isinstance(future, list):
        summary = {}
        rows = future
        top_rows = future[:200]

    else:
        summary = {}
        rows = []
        top_rows = []

    if not isinstance(rows, list):
        rows = []

    if not isinstance(top_rows, list):
        top_rows = []

    if not summary:
        total = len(rows)

        future_critical = []
        worsening = []

        for r in rows:
            future_level = normalize_text(
                r.get(
                    "niveau_futur_predit",
                    r.get(
                        "future_level",
                        r.get(
                            "predicted_level",
                            r.get("niveau_futur", "")
                        )
                    )
                )
            )

            current_level = normalize_text(
                r.get(
                    "niveau_actuel",
                    r.get(
                        "current_level",
                        r.get("alert_level", "")
                    )
                )
            )

            if future_level in ["CRITICAL", "CRITIQUE"]:
                future_critical.append(r)

            if current_level not in ["CRITICAL", "CRITIQUE"] and future_level in ["CRITICAL", "CRITIQUE"]:
                worsening.append(r)

        summary = {
            "total_clients": total,
            "critical_future_clients": len(future_critical),
            "new_critical_clients": len(worsening),
            "horizon_days": 30,
        }

    return {
        "summary": summary,
        "all_future_predictions": rows,
        "top_future_risk_clients": top_rows,
        "predictions": rows,
        "clients": rows,
        "data": rows,
    }


# =========================================================
# ASSISTANT LOCAL DYNAMIQUE
# =========================================================

def local_risk_answer(question, context):
    q = question.lower()

    summary = context.get("portfolio_summary", {})
    top_clients = context.get("top_risky_clients", [])
    selected_client = context.get("selected_client")
    anomaly_count = context.get("anomaly_count", 0)
    sample_anomalies = context.get("sample_anomalies", [])
    model_metrics = context.get("model_metrics", [])
    future = context.get("future_prediction", {})
    future_summary = future.get("summary", {}) if isinstance(future, dict) else {}

    # =====================================================
    # 1) Client précis
    # =====================================================
    if selected_client:
        cpte = get_client_id(selected_client)
        score = get_score(selected_client)
        level = get_level(selected_client)
        exposure = get_exposure(selected_client)

        return f"""
Analyse du client {cpte} :

- Score de risque : {score} %
- Niveau d'alerte : {level}
- Exposition / risque brut : {format_money(exposure)}

Interprétation :
Ce client doit être analysé en priorité si son niveau est CRITICAL, CRITIQUE, WARNING ou ÉLEVÉ.
Il faut vérifier son historique de dépassement, son exposition actuelle, son comportement récent et la présence éventuelle d'anomalies.

Action recommandée :
- contrôler les derniers mouvements du compte ;
- vérifier la fréquence des dépassements ;
- prioriser le contact client si le score est supérieur à 85 % ;
- suivre l'évolution du risque dans les prochains jours.
"""

    # =====================================================
    # 2) Future Prediction
    # =====================================================
    if (
        "future" in q
        or "futur" in q
        or "prédit" in q
        or "pred" in q
        or "30 jours" in q
        or "devenir critique" in q
    ):
        top_future = []
        if isinstance(future, dict):
            top_future = future.get("top_future_risk_clients", [])[:8]

        txt = f"""
Module de prédiction future :

- Clients analysés : {future_summary.get("total_clients", 0)}
- Clients prédits critiques : {future_summary.get("critical_future_clients", 0)}
- Nouveaux clients susceptibles de devenir critiques : {future_summary.get("new_critical_clients", 0)}
- Horizon de prédiction : {future_summary.get("horizon_days", 30)} jours

Interprétation :
Ce module permet d'identifier les clients qui ne sont pas encore critiques aujourd'hui, mais qui présentent un risque d'aggravation dans les prochains jours.
"""

        if top_future:
            txt += "\nClients à surveiller en priorité selon la prédiction future :\n\n"

            for i, c in enumerate(top_future, start=1):
                txt += (
                    f"{i}. {get_client_id(c)} | "
                    f"Score: {get_score(c)}% | "
                    f"Niveau: {get_level(c)} | "
                    f"Exposition: {format_money(get_exposure(c))}\n"
                )

        return txt

    # =====================================================
    # 3) Clients critiques
    # =====================================================
    if "critique" in q or "critical" in q:
        return f"""
Situation des clients critiques :

- Clients critiques : {summary.get("critical_clients", 0)}
- Clients high risk / warning : {summary.get("high_risk_clients", 0)}
- Clients à notifier : {summary.get("clients_to_notify", 0)}
- Score moyen du portefeuille : {summary.get("average_score_percent", 0)} %
- Exposition totale estimée : {format_money(summary.get("total_exposure_tnd", 0))}

Interprétation :
Les clients critiques doivent être traités en priorité, car ils présentent le niveau de risque le plus élevé.
"""

    # =====================================================
    # 4) Anomalies
    # =====================================================
    if "anomal" in q or "inhabituel" in q or "atypique" in q:
        txt = f"""
Détection d'anomalies :

- Nombre total d'anomalies détectées : {anomaly_count}

Interprétation :
Les anomalies permettent de repérer des comportements inhabituels qui ne sont pas toujours visibles uniquement avec le score ML.
Un client peut avoir un score acceptable mais présenter un comportement atypique qui mérite une analyse plus approfondie.
"""

        if sample_anomalies:
            txt += "\nExemples d'anomalies détectées :\n\n"

            for i, c in enumerate(sample_anomalies[:5], start=1):
                txt += (
                    f"{i}. {get_client_id(c)} | "
                    f"Score: {get_score(c)}% | "
                    f"Niveau: {get_level(c)} | "
                    f"Exposition: {format_money(get_exposure(c))}\n"
                )

        return txt

    # =====================================================
    # 5) Clients à notifier / priorité
    # =====================================================
    if (
        "notifier" in q
        or "priorité" in q
        or "priorite" in q
        or "top" in q
        or "traiter" in q
        or "urgent" in q
    ):
        txt = "Clients à traiter en priorité :\n\n"

        for i, c in enumerate(top_clients[:10], start=1):
            txt += (
                f"{i}. {get_client_id(c)} | "
                f"Score: {get_score(c)}% | "
                f"Niveau: {get_level(c)} | "
                f"Exposition: {format_money(get_exposure(c))}\n"
            )

        txt += """
Recommandation :
Commencer par les clients CRITICAL ou CRITIQUE avec le score le plus élevé et l'exposition la plus importante.
"""

        return txt

    # =====================================================
    # 6) Performance modèle
    # =====================================================
    if (
        "performance" in q
        or "modèle" in q
        or "modele" in q
        or "recall" in q
        or "precision" in q
        or "f1" in q
        or "auc" in q
    ):
        txt = "Performance du modèle prédictif :\n\n"

        if model_metrics:
            if isinstance(model_metrics, list):
                for i, m in enumerate(model_metrics[:10], start=1):
                    txt += f"{i}. {m}\n"
            elif isinstance(model_metrics, dict):
                for key, value in model_metrics.items():
                    txt += f"- {key} : {value}\n"
            else:
                txt += f"{model_metrics}\n"
        else:
            txt += "Aucune métrique détaillée n'a été trouvée dans les fichiers JSON.\n"

        txt += """
Interprétation :
Dans un projet de risque bancaire, le rappel est une métrique très importante, car il mesure la capacité du modèle à détecter les clients réellement risqués.
"""

        return txt

    # =====================================================
    # 7) Score moyen / exposition
    # =====================================================
    if "score moyen" in q or "exposition" in q or "montant" in q:
        return f"""
Indicateurs financiers et scoring :

- Score moyen du portefeuille : {summary.get("average_score_percent", 0)} %
- Exposition totale estimée : {format_money(summary.get("total_exposure_tnd", 0))}
- Clients uniques : {summary.get("unique_clients", 0)}
- Lignes analysées : {summary.get("total_rows", 0)}

Ces indicateurs permettent d'avoir une vision globale du niveau de risque et de l'exposition associée.
"""

    # =====================================================
    # 8) Aide / exemples de questions
    # =====================================================
    if "aide" in q or "help" in q or "question" in q or "quoi demander" in q:
        return """
Tu peux me poser par exemple ces questions :

- Combien de clients critiques avons-nous ?
- Quels sont les clients à notifier en priorité ?
- Analyse le client CPTE_001508.
- Combien d'anomalies sont détectées ?
- Quels clients risquent de devenir critiques dans 30 jours ?
- Donne-moi un résumé global du portefeuille.
- Quelles sont les performances du modèle ?
- Quelle est l'exposition totale du portefeuille ?
"""

    # =====================================================
    # 9) Résumé global par défaut
    # =====================================================
    return f"""
Résumé global du portefeuille BIAT Risk Monitor :

- Lignes analysées : {summary.get("total_rows", 0)}
- Clients uniques : {summary.get("unique_clients", 0)}
- Clients critiques : {summary.get("critical_clients", 0)}
- Clients high risk / warning : {summary.get("high_risk_clients", 0)}
- Clients moyens : {summary.get("medium_clients", 0)}
- Clients faibles : {summary.get("low_clients", 0)}
- Clients à notifier : {summary.get("clients_to_notify", 0)}
- Score moyen : {summary.get("average_score_percent", 0)} %
- Exposition totale : {format_money(summary.get("total_exposure_tnd", 0))}
- Anomalies détectées : {anomaly_count}

Interprétation :
Le portefeuille doit être suivi en priorité à travers les clients critiques, les clients à notifier et les anomalies détectées.
"""


# =========================================================
# GROQ API
# =========================================================

def call_groq(question, context):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return local_risk_answer(question, context)

    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    system_prompt = """
Tu es l'assistant IA du projet BIAT Risk Monitor.
Tu réponds comme un analyste risque bancaire.
Utilise uniquement le contexte fourni.
Réponds en français sauf si l'utilisateur écrit dans une autre langue.
Ne donne jamais d'informations inventées.
Si une donnée manque, dis clairement qu'elle n'est pas disponible dans le contexte.
"""

    compact_context = {
        "portfolio_summary": context.get("portfolio_summary", {}),
        "selected_client": context.get("selected_client"),
        "anomaly_count": context.get("anomaly_count", 0),
        "sample_anomalies": context.get("sample_anomalies", [])[:5],
        "top_risky_clients": context.get("top_risky_clients", [])[:10],
        "future_prediction": context.get("future_prediction", {}),
        "model_metrics": context.get("model_metrics", {}),
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "context": compact_context,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": 0.25,
        "max_tokens": 1000,
    }

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]

    except Exception:
        return local_risk_answer(question, context)


# =========================================================
# SERVEUR HTTP
# =========================================================

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path).path

        if parsed_path == "/api/groq-status":
            self.send_json({
                "groq_configured": bool(os.environ.get("GROQ_API_KEY")),
                "model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
                "fallback_local": not bool(os.environ.get("GROQ_API_KEY")),
            })
            return

        if parsed_path == "/api/portfolio":
            context = build_portfolio_context("")
            summary = context.get("portfolio_summary", {})

            self.send_json({
                "ok": True,
                "clients_rows": summary.get("total_rows", 0),
                "unique_clients": summary.get("unique_clients", 0),
                "summary": summary,
                "top_risky_clients": context.get("top_risky_clients", []),
                "anomaly_count": context.get("anomaly_count", 0),
                "model_metrics": context.get("model_metrics", []),
            })
            return

        if parsed_path == "/api/future-predictions":
            self.send_json(build_future_context())
            return

        if parsed_path in ROUTES:
            self.path = "/" + ROUTES[parsed_path]
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path).path

        if parsed_path == "/api/chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)

                question = str(
                    data.get("message")
                    or data.get("question")
                    or data.get("prompt")
                    or ""
                ).strip()

                if not question:
                    self.send_json({
                        "answer": "Écris une question pour que je puisse répondre.",
                        "context_used": False,
                    })
                    return

                context = build_portfolio_context(question)

                q = question.lower()
                if (
                    "future" in q
                    or "futur" in q
                    or "prédit" in q
                    or "pred" in q
                    or "30 jours" in q
                    or "devenir critique" in q
                ):
                    context["future_prediction"] = build_future_context()

                answer = call_groq(question, context)

                self.send_json({
                    "answer": answer,
                    "context_used": True,
                    "groq_used": bool(os.environ.get("GROQ_API_KEY")),
                })

            except Exception as e:
                self.send_json({
                    "answer": f"Erreur serveur assistant: {str(e)}",
                    "context_used": False,
                }, status=500)

            return

        self.send_error(404, "API route not found")

    def send_json(self, payload, status=200):
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        try:
            print(f"{self.address_string()} - {format % args}")
        except Exception:
            pass


class ThreadingReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    os.chdir(BASE_DIR)

    with ThreadingReusableTCPServer((HOST, PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print(f"Login:          http://localhost:{PORT}/login")
        print(f"Dashboard:      http://localhost:{PORT}/dashboard")
        print(f"Evolution:      http://localhost:{PORT}/evolution")
        print(f"Future:         http://localhost:{PORT}/future")
        print(f"Notifications:  http://localhost:{PORT}/notifications")
        print(f"Client:         http://localhost:{PORT}/client")
        print(f"Performance:    http://localhost:{PORT}/performance")
        print(f"Assistant:      http://localhost:{PORT}/assistant")
        print(f"API Chat:       http://localhost:{PORT}/api/chat")
        print(f"API Portfolio:  http://localhost:{PORT}/api/portfolio")
        print(f"API Future:     http://localhost:{PORT}/api/future-predictions")
        print(f"Groq configured: {bool(os.environ.get('GROQ_API_KEY'))}")
        httpd.serve_forever()