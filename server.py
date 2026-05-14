import http.server
import socketserver
import os
from urllib.parse import urlparse

PORT = 5000
HOST = "0.0.0.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ROUTES = {
    "/": "home_biat_risk_monitor/code.html",
    "/home": "home_biat_risk_monitor/code.html",
    "/dashboard": "global_dashboard_biat_risk_monitor/code.html",
    "/evolution": "risk_evolution_biat_risk_monitor/code.html",
    "/notifications": "clients_notifier_biat_risk_monitor/code.html",
    "/client": "fiche_client_biat_risk_monitor/code.html",
    "/performance": "performance_mod_le_biat_risk_monitor/code.html",
    "/assistant": "assistant_ia_biat_risk_monitor/code.html",
}


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path).path

        if parsed_path in ROUTES:
            self.path = "/" + ROUTES[parsed_path]

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