import http.server
import socketserver
import os
from pathlib import Path

PORT = 5000
HOST = "0.0.0.0"

BASE_DIR = Path(__file__).resolve().parent

ROUTES = {
    "/": "home_biat_risk_monitor/code.html",
    "/dashboard": "global_dashboard_biat_risk_monitor/code.html",
    "/evolution": "risk_evolution_biat_risk_monitor/code.html",
    "/notifications": "clients_notifier_biat_risk_monitor/code.html",
    "/client": "fiche_client_biat_risk_monitor/code.html",
    "/performance": "performance_modele_biat_risk_monitor/code.html",
    "/assistant": "assistant_ia_biat_risk_monitor/code.html",
}


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        clean_path = self.path.split("?")[0].split("#")[0]

        if clean_path in ROUTES:
            file_path = BASE_DIR / ROUTES[clean_path]

            if file_path.exists():
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()

                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        return super().do_GET()

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


os.chdir(BASE_DIR)

with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
    print(f"Serving BIAT Risk Monitor at http://localhost:{PORT}")
    print("Available pages:")
    print(f"  Home:          http://localhost:{PORT}/")
    print(f"  Dashboard:     http://localhost:{PORT}/dashboard")
    print(f"  Evolution:     http://localhost:{PORT}/evolution")
    print(f"  Notifications: http://localhost:{PORT}/notifications")
    print(f"  Client:        http://localhost:{PORT}/client")
    print(f"  Performance:   http://localhost:{PORT}/performance")
    print(f"  Assistant:     http://localhost:{PORT}/assistant")
    httpd.serve_forever()