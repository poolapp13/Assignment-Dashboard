from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import json


class RefreshHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/refresh":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            subprocess.run(["python", "scraper.py"])
            self.wfile.write(json.dumps({"status": "done"}).encode())

    def log_message(self, format, *args):
        pass  # suppress logs


HTTPServer(("localhost", 8001), RefreshHandler).serve_forever()
