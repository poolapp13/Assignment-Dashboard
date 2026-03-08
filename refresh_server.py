from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import json
import threading

scraper_running = False


class RefreshHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global scraper_running

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if self.path == "/refresh":
            if not scraper_running:
                scraper_running = True

                def run():
                    global scraper_running
                    subprocess.run(["python", "scraper.py"])
                    scraper_running = False
                threading.Thread(target=run).start()
            self.wfile.write(json.dumps({"status": "started"}).encode())

        elif self.path == "/status":
            self.wfile.write(json.dumps({"running": scraper_running}).encode())

    def log_message(self, format, *args):
        pass


HTTPServer(("localhost", 8001), RefreshHandler).serve_forever()
