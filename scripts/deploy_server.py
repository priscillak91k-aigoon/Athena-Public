"""
Deploy Server — Lobotto Local Deploy Gateway
Runs on port 7338. Exposes /deploy endpoint that triggers git push.
Called by the 🚀 Deploy button on the local Life Hub / Workshop pages.
"""
import subprocess
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import pytz

PROJECT_ROOT = r"C:\Users\prisc\Documents\Athena-Public"
PORT = 7338
NZ_TZ = pytz.timezone("Pacific/Auckland")


class DeployHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # CORS preflight handling
        if self.path == "/deploy":
            self._deploy()
        elif self.path == "/status":
            self._status()
        else:
            self._send(404, {"error": "Not found"})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def _deploy(self):
        now = datetime.now(NZ_TZ).strftime("%Y-%m-%d %H:%M NZDT")
        commit_msg = f"deploy: auto-push {now}"
        try:
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=PROJECT_ROOT,
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                self._send(500, {"status": "error", "step": "git add", "output": result.stderr})
                return

            result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=PROJECT_ROOT,
                capture_output=True, text=True, timeout=30
            )
            # Exit code 1 from commit just means "nothing to commit" — not a real error
            if result.returncode not in (0, 1):
                self._send(500, {"status": "error", "step": "git commit", "output": result.stderr})
                return

            nothing_to_commit = "nothing to commit" in result.stdout or "nothing to commit" in result.stderr

            if nothing_to_commit:
                self._send(200, {
                    "status": "ok",
                    "message": "Nothing to commit — already up to date.",
                    "timestamp": now
                })
                return

            result = subprocess.run(
                ["git", "push"],
                cwd=PROJECT_ROOT,
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                self._send(500, {"status": "error", "step": "git push", "output": result.stderr})
                return

            print(f"[Deploy] ✅ Pushed: {commit_msg}")
            self._send(200, {
                "status": "ok",
                "message": f"Pushed to GitHub Pages",
                "commit": commit_msg,
                "timestamp": now
            })

        except subprocess.TimeoutExpired:
            self._send(500, {"status": "error", "message": "git command timed out"})
        except Exception as e:
            self._send(500, {"status": "error", "message": str(e)})

    def _status(self):
        self._send(200, {"status": "ok", "service": "Lobotto Deploy Server", "port": PORT})

    def _send(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, fmt, *args):
        # Suppress default handler logging, use our own
        pass


def main():
    server = HTTPServer(("localhost", PORT), DeployHandler)
    print(f"🚀 Deploy Server running on http://localhost:{PORT}")
    print(f"   /deploy → git add -A + commit + push")
    print(f"   /status → health check")
    server.serve_forever()


if __name__ == "__main__":
    main()
