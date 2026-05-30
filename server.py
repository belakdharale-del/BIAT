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
        return float(x)
    except Exception:
        return default


def build_portfolio_context(question):
    dashboard = read_json("attached_assets/dashboard_clients_full.json", {})
    anomalies = read_json("attached_assets/anomaly_clients.json", {})
    metrics = read_json("attached_assets/model_metrics.json", [])
    top_risky = read_json("attached_assets/top_risky_clients.json", [])

    clients = dashboard.get("clients", []) if isinstance(dashboard, dict) else []

    total_rows = len(clients)
    unique_clients = len(set(str(c.get("cpte", "")) for c in clients if c.get("cpte")))

    critical = [c for c in clients if str(c.get("alert_level", "")).upper() == "CRITICAL"]
    warning = [c for c in clients if str(c.get("alert_level", "")).upper() == "WARNING"]
    medium = [c for c in clients if str(c.get("alert_level", "")).upper() == "MEDIUM"]
    low = [c for c in clients if str(c.get("alert_level", "")).upper() == "LOW"]

    avg_score = 0
    if clients:
        avg_score = sum(safe_float(c.get("risk_score_percent", 0)) for c in clients) / len(clients)

    exposure = sum(safe_float(c.get("risk_brut", 0)) for c in clients)

    top_clients = sorted(
        clients,
        key=lambda c: (
            safe_float(c.get("risk_score_percent", 0)),
            safe_float(c.get("risk_brut", 0))
        ),
        reverse=True
    )[:8]

    cpte_match = re.search(r"CPTE[_-]?\d+", question.upper())
    selected_client = None

    if cpte_match:
        searched = cpte_match.group(0).replace("-", "_")
        for c in clients:
            if str(c.get("cpte", "")).upper() == searched:
                selected_client = c
                break

    anomaly_list = []
    if isinstance(anomalies, dict):
        anomaly_list = anomalies.get("clients", []) or anomalies.get("anomalies", []) or []
    elif isinstance(anomalies, list):
        anomaly_list = anomalies

    context = {
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

    return context


def local_risk_answer(question, context):
    q = question.lower()
    summary = context.get("portfolio_summary", {})
    top_clients = context.get("top_risky_clients", [])
    selected_client = context.get("selected_client")
    anomaly_count = context.get("anomaly_count", 0)
    sample_anomalies = context.get("sample_anomalies", [])

    if selected_client:
        cpte = selected_client.get("cpte", "client inconnu")
        score = selected_client.get("risk_score_percent", 0)
        level = selected_client.get("alert_level", "non défini")
        risk_brut = selected_client.get("risk_brut", 0)

        return f"""
Analyse du client {cpte} :

- Score de risque : {score} %
- Niveau d'alerte : {level}
- Exposition / risque brut : {risk_brut} TND

Ce client doit être analysé en priorité si son niveau est CRITICAL ou WARNING.
La décision recommandée est de vérifier son comportement récent, ses dépassements, son exposition et la présence éventuelle d'anomalies détectées.
"""

    if "critique" in q or "critical" in q:
        return f"""
Le portefeuille contient actuellement {summary.get("critical_clients", 0)} clients critiques.

Nombre total de lignes analysées : {summary.get("total_rows", 0)}
Nombre de clients uniques : {summary.get("unique_clients", 0)}
Clients à notifier : {summary.get("clients_to_notify", 0)}

Les clients critiques doivent être traités en priorité car ils présentent le niveau de risque le plus élevé.
"""

    if "anomal" in q:
        txt = f"""
Le module de détection d'anomalies a identifié {anomaly_count} cas/anomalies.

Ces anomalies permettent de repérer des comportements inhabituels qui ne sont pas toujours visibles uniquement avec le score ML.
Elles doivent être utilisées comme signal complémentaire au scoring de risque.
"""
        if sample_anomalies:
            txt += "\nExemples d'anomalies détectées :\n"
            for a in sample_anomalies[:5]:
                txt += f"- {a}\n"
        return txt

    if "top" in q or "priorité" in q or "priorite" in q or "notifier" in q:
        txt = "Clients à traiter en priorité :\n\n"

        for i, c in enumerate(top_clients[:8], start=1):
            txt += (
                f"{i}. {c.get('cpte', 'N/A')} | "
                f"Score: {c.get('risk_score_percent', 0)}% | "
                f"Niveau: {c.get('alert_level', 'N/A')} | "
                f"Risque brut: {c.get('risk_brut', 0)} TND\n"
            )

        txt += "\nRecommandation : commencer par les clients CRITICAL avec le score le plus élevé."
        return txt

    if "performance" in q or "modèle" in q or "model" in q or "lstm" in q or "lightgbm" in q:
        return f"""
Le projet utilise principalement un modèle de scoring ML pour prédire les clients risqués.

Résumé disponible :
- Lignes analysées : {summary.get("total_rows", 0)}
- Clients uniques : {summary.get("unique_clients", 0)}
- Score moyen : {summary.get("average_score_percent", 0)} %
- Clients critiques : {summary.get("critical_clients", 0)}
- Clients à notifier : {summary.get("clients_to_notify", 0)}

Le modèle principal reste LightGBM pour le scoring.
Le LSTM peut être présenté comme un module expérimental temporel qui analyse l'évolution séquentielle des clients.
"""

    # Questions sur l'évolution des clients critiques
    if (
        ("evolue" in q or "évolue" in q or "evolution" in q or "évolution" in q or "évoluent" in q or "evoluent" in q)
        and ("critique" in q or "critical" in q)
    ):
        return f"""
Évolution des clients critiques :

Le portefeuille contient actuellement {summary.get("critical_clients", 0)} clients critiques sur {summary.get("unique_clients", 0)} clients uniques.

Lecture risque :
- Ces clients représentent le segment le plus sensible du portefeuille.
- Ils doivent être suivis en priorité car leur score dépasse le seuil critique.
- Une évolution défavorable signifie généralement une hausse du score de risque, une aggravation comportementale ou une exposition plus importante.
- Les clients critiques doivent être croisés avec les anomalies détectées pour repérer les cas les plus urgents.

Indicateurs actuels :
- Lignes analysées : {summary.get("total_rows", 0)}
- Clients critiques : {summary.get("critical_clients", 0)}
- Clients à notifier : {summary.get("clients_to_notify", 0)}
- Score moyen du portefeuille : {summary.get("average_score_percent", 0)} %
- Anomalies détectées : {anomaly_count}

Recommandation :
Prioriser les clients qui combinent trois signaux : niveau CRITICAL, anomalie détectée et exposition financière élevée.
"""

    # Questions sur l'évolution des clients avec anomalies
    if (
        "évoluent" in q or "evoluent" in q or "évolue" in q or "evolue" in q
        or "évolution" in q or "evolution" in q or "nouveaux clients" in q
        or ("client" in q and "anomal" in q)
    ):
        return f"""
Pour analyser l'évolution des clients avec anomalies, il faut croiser deux signaux :

1. Le score de risque ML
2. Les anomalies détectées par Isolation Forest

Dans les données actuelles :
- Clients uniques : {summary.get("unique_clients", 0)}
- Clients critiques : {summary.get("critical_clients", 0)}
- Anomalies détectées : {anomaly_count}

Interprétation :
Les clients qui présentent des anomalies doivent être suivis avec prudence, surtout si leur score ML augmente ou s'ils passent vers un niveau WARNING ou CRITICAL.
La priorité doit être donnée aux clients qui combinent anomalie + score élevé + exposition financière importante.
"""

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

Pose une question plus précise, par exemple :
- Quels clients notifier en priorité ?
- Analyse le client CPTE_001508
- Combien de clients critiques ?
- Comment évoluent les clients avec anomalies ?
"""


def call_groq(question, context):
    api_key = os.environ.get("GROQ_API_KEY")

    # Important:
    # Si la clé Groq n'existe pas, on répond avec les vraies données locales.
    # Donc l'assistant continue à fonctionner.
    if not api_key:
        return local_risk_answer(question, context)

    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    system_prompt = """
Tu es l'assistant IA du projet BIAT Risk Monitor.
Tu réponds comme un analyste risque bancaire.
Tu dois utiliser le contexte fourni par le système quand il contient des données.
Tu dois être clair, professionnel et utile pour un risk officer.
Ne prétends jamais avoir accès à des données qui ne sont pas dans le contexte.
Si le client ou la donnée demandée n'existe pas, dis-le clairement.
Réponds en français sauf si l'utilisateur écrit en arabe tunisien ou en anglais.
"""

    user_content = {
        "question": question,
        "context": context
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(user_content, ensure_ascii=False)
            }
        ],
        "temperature": 0.3,
        "max_tokens": 900
    }

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]

    # Si Groq refuse 401/403/429/etc., on ne bloque pas l'application.
    # On répond avec le fallback local.
    except urllib.error.HTTPError:
        return local_risk_answer(question, context)

    except Exception:
        return local_risk_answer(question, context)


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path).path

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
                    self.send_json({"answer": "Écris une question pour que je puisse répondre."})
                    return

                context = build_portfolio_context(question)
                answer = call_groq(question, context)

                self.send_json({
                    "answer": answer,
                    "context_used": True
                })

            except Exception as e:
                self.send_json({
                    "answer": f"Erreur serveur assistant: {str(e)}",
                    "context_used": False
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


if __name__ == "__main__":
    os.chdir(BASE_DIR)

    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print(f"Login:       http://localhost:{PORT}/login")
        print(f"Dashboard:   http://localhost:{PORT}/dashboard")
        print(f"Evolution:   http://localhost:{PORT}/evolution")
        print(f"Notifications: http://localhost:{PORT}/notifications")
        print(f"Client:      http://localhost:{PORT}/client")
        print(f"Performance: http://localhost:{PORT}/performance")
        print(f"Assistant:   http://localhost:{PORT}/assistant")
        print(f"API Chat:    http://localhost:{PORT}/api/chat")
        httpd.serve_forever()