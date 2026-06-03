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


def read_json(path, default):
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


def normalize_clients(raw):
    if isinstance(raw, dict):
        clients = raw.get("clients", [])
        if isinstance(clients, list):
            return clients

    if isinstance(raw, list):
        return raw

    return []


def build_portfolio_context(question=""):
    dashboard = read_json("attached_assets/dashboard_clients_full.json", {})
    anomalies = read_json("attached_assets/anomaly_clients.json", {})
    metrics = read_json("attached_assets/model_metrics.json", [])
    top_risky = read_json("attached_assets/top_risky_clients.json", [])

    clients = normalize_clients(dashboard)

    total_rows = len(clients)
    unique_clients = len(
        set(str(c.get("cpte", "")) for c in clients if c.get("cpte"))
    )

    critical = [
        c for c in clients
        if str(c.get("alert_level", "")).upper() in ["CRITICAL", "CRITIQUE"]
    ]

    warning = [
        c for c in clients
        if str(c.get("alert_level", "")).upper() in ["WARNING", "HIGH", "ÉLEVÉ", "ELEVE"]
    ]

    medium = [
        c for c in clients
        if str(c.get("alert_level", "")).upper() in ["MEDIUM", "MOYEN"]
    ]

    low = [
        c for c in clients
        if str(c.get("alert_level", "")).upper() in ["LOW", "FAIBLE"]
    ]

    if clients:
        avg_score = sum(
            safe_float(c.get("risk_score_percent", c.get("score", 0)))
            for c in clients
        ) / len(clients)
    else:
        avg_score = 0

    exposure = sum(
        safe_float(c.get("risk_brut", c.get("exposure", 0)))
        for c in clients
    )

    top_clients = sorted(
        clients,
        key=lambda c: (
            safe_float(c.get("risk_score_percent", c.get("score", 0))),
            safe_float(c.get("risk_brut", c.get("exposure", 0))),
        ),
        reverse=True,
    )[:20]

    selected_client = None
    cpte_match = re.search(r"CPTE[_-]?\d+", str(question).upper())

    if cpte_match:
        searched = cpte_match.group(0).replace("-", "_")

        for c in clients:
            if str(c.get("cpte", "")).upper() == searched:
                selected_client = c
                break

    if isinstance(anomalies, dict):
        anomaly_list = (
            anomalies.get("clients", [])
            or anomalies.get("anomalies", [])
            or []
        )
    elif isinstance(anomalies, list):
        anomaly_list = anomalies
    else:
        anomaly_list = []

    return {
        "portfolio_summary": {
            "total_rows": total_rows,
            "unique_clients": unique_clients,
            "critical_clients": len(critical),
            "high_risk_clients": len(warning),
            "medium_clients": len(medium),
            "low_clients": len(low),
            "clients_to_notify": len(critical) + len(warning),
            "average_score_percent": round(avg_score, 2),
            "total_exposure_tnd": round(exposure, 2),
        },
        "top_risky_clients": top_clients,
        "selected_client": selected_client,
        "anomaly_count": len(anomaly_list),
        "sample_anomalies": anomaly_list[:5],
        "model_metrics": metrics,
        "top_risky_file": top_risky[:5] if isinstance(top_risky, list) else top_risky,
    }


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

        top_rows = (
            future.get("top_future_risk_clients")
            or rows[:200]
            if isinstance(rows, list)
            else []
        )

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

        future_critical = [
            r for r in rows
            if str(
                r.get(
                    "niveau_futur_predit",
                    r.get(
                        "future_level",
                        r.get("predicted_level", r.get("niveau_futur", ""))
                    )
                )
            ).upper() in ["CRITICAL", "CRITIQUE"]
        ]

        summary = {
            "total_clients": total,
            "critical_future_clients": len(future_critical),
        }

    return {
        "summary": summary,

        # Pour compatibilité avec la page HTML actuelle
        "all_future_predictions": rows,
        "top_future_risk_clients": top_rows,

        # Pour compatibilité API générale
        "predictions": rows,
        "clients": rows,
        "data": rows,
    }


def local_risk_answer(question, context):
    q = question.lower()
    summary = context.get("portfolio_summary", {})
    top_clients = context.get("top_risky_clients", [])
    selected_client = context.get("selected_client")
    anomaly_count = context.get("anomaly_count", 0)

    if selected_client:
        cpte = selected_client.get("cpte", "client inconnu")
        score = selected_client.get(
            "risk_score_percent",
            selected_client.get("score", 0),
        )
        level = selected_client.get("alert_level", "non défini")
        risk_brut = selected_client.get(
            "risk_brut",
            selected_client.get("exposure", 0),
        )

        return f"""
Analyse du client {cpte} :

- Score de risque : {score} %
- Niveau d'alerte : {level}
- Exposition / risque brut : {risk_brut} TND

Ce client doit être analysé en priorité si son niveau est CRITICAL ou WARNING.
La décision recommandée est de vérifier son comportement récent, ses dépassements, son exposition et la présence éventuelle d'anomalies détectées.
"""

    if "future" in q or "futur" in q or "prédit" in q or "pred" in q:
        future = context.get("future_prediction", {})
        fs = future.get("summary", {})

        return f"""
Module Future Prediction :

- Clients analysés : {fs.get("total_clients", 0)}
- Clients prédits critiques : {fs.get("critical_future_clients", 0)}
- Horizon : 30 jours

Ce module sert à identifier les clients qui risquent de devenir critiques avant le passage réel en situation critique.
"""

    if "critique" in q or "critical" in q:
        return f"""
Le portefeuille contient actuellement {summary.get("critical_clients", 0)} clients critiques.

Nombre total de lignes analysées : {summary.get("total_rows", 0)}
Nombre de clients uniques : {summary.get("unique_clients", 0)}
Clients à notifier : {summary.get("clients_to_notify", 0)}
"""

    if "anomal" in q:
        return f"""
Le module de détection d'anomalies a identifié {anomaly_count} cas/anomalies.

Ces anomalies permettent de repérer des comportements inhabituels qui ne sont pas toujours visibles uniquement avec le score ML.
"""

    if "top" in q or "priorité" in q or "priorite" in q or "notifier" in q:
        txt = "Clients à traiter en priorité :\n\n"

        for i, c in enumerate(top_clients[:8], start=1):
            txt += (
                f"{i}. {c.get('cpte', 'N/A')} | "
                f"Score: {c.get('risk_score_percent', c.get('score', 0))}% | "
                f"Niveau: {c.get('alert_level', 'N/A')} | "
                f"Risque brut: {c.get('risk_brut', c.get('exposure', 0))} TND\n"
            )

        txt += "\nRecommandation : commencer par les clients CRITICAL avec le score le plus élevé."
        return txt

    return f"""
Résumé du portefeuille BIAT Risk Monitor :

- Lignes analysées : {summary.get("total_rows", 0)}
- Clients uniques : {summary.get("unique_clients", 0)}
- Clients critiques : {summary.get("critical_clients", 0)}
- Clients high risk / warning : {summary.get("high_risk_clients", 0)}
- Clients à notifier : {summary.get("clients_to_notify", 0)}
- Score moyen : {summary.get("average_score_percent", 0)} %
- Exposition totale : {summary.get("total_exposure_tnd", 0)} TND
- Anomalies détectées : {anomaly_count}
"""


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
"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "context": context,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": 0.3,
        "max_tokens": 900,
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

                question = str(data.get("message", "")).strip()

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
                ):
                    context["future_prediction"] = build_future_context()

                answer = call_groq(question, context)

                self.send_json({
                    "answer": answer,
                    "context_used": True,
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
        print(f"{self.address_string()} - {format % args}")


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
        httpd.serve_forever()