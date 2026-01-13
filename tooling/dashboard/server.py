import http.server
import socketserver
import json
import os
import sys
import subprocess
from urllib.parse import urlparse, parse_qs

# KONFIG
PORT = 8000
HISTORY_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/synapse/status/status_window_history.json"))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class statusHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/api/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = f.read()
                    self.wfile.write(data.encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

        elif parsed_url.path == '/api/search':
            query_params = parse_qs(parsed_url.query)
            query = query_params.get('q', [''])[0]
            
            if not query:
                self.send_response(400)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers() # Send headers immediately

            # Buffer response
            response_data = []

            # --- 1. FAISS Retrieval (Old Memory) ---
            faiss_results = []
            
            # ENV Setup for UTF-8
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.join(PROJECT_ROOT, "app")
            env["PYTHONIOENCODING"] = "utf-8"  # FORCE UTF-8 OUTPUT
            
            cmd = [
                sys.executable,
                os.path.join(PROJECT_ROOT, "app/temple/automation/search_chatverlauf.py"),
                "--query", query,
                "--top-k", "5",
                "--include-text"
            ]

            print(f"🔍 Searching FAISS for: {query}")
            try:
                # Capture stderr for debugging
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    env=env,
                    encoding='utf-8',
                    errors='replace' 
                )
                
                if result.returncode == 0:
                    try:
                        faiss_results = json.loads(result.stdout)
                        for item in faiss_results:
                            item['source_type'] = 'FAISS (Archive)'
                    except json.JSONDecodeError as je:
                        print(f"JSON Parse Error: {je}")
                        faiss_results = [{
                            "chunk_id": "ERROR-JSON",
                            "score": 0,
                            "preview": "Failed to parse search results.",
                            "text": f"Raw Output: {result.stdout[:200]}... Error: {str(je)}"
                        }]
                else:
                    print(f"FAISS Subprocess Error: {result.stderr}")
                    faiss_results = [{
                        "chunk_id": "ERROR-SUBPROCESS",
                        "score": 0,
                        "preview": "Search script failed.",
                        "text": f"Stderr: {result.stderr}"
                    }]
            except Exception as e:
                print(f"Execution Error: {e}")
                faiss_results = [{
                    "chunk_id": "ERROR-EXEC",
                    "score": 0,
                    "preview": "Server executon error.",
                    "text": str(e)
                }]

            # --- 2. Live History Search (New Memory) ---
            live_results = []
            try:
                if os.path.exists(HISTORY_FILE):
                    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            entries = data.get("entries", [])
                        elif isinstance(data, list):
                            entries = data
                        else:
                            entries = []
                        
                        recent_entries = entries[-200:]
                        
                        for idx, entry in enumerate(recent_entries):
                            sw = entry.get("status_window", {})
                            entry_idx = entry.get("entry_index", "?")
                            
                            corpus = (
                                str(sw.get("goal", "")) + " " + 
                                str(sw.get("inputs", {})) + " " +
                                str(sw.get("actions", [])) + " " + 
                                str(sw.get("reflection_curve", {}))
                            ).lower()
                            
                            if query.lower() in corpus:
                                live_results.append({
                                    "chunk_id": f"LIVE-STEP-{entry_idx}",
                                    "score": 2.0, 
                                    "preview": f"GOAL: {sw.get('goal')} | ACTIONS: {sw.get('actions')}",
                                    "text": json.dumps(sw, indent=2, ensure_ascii=False),
                                    "source_type": "LIVE HISTORY (Recent)"
                                })
            except Exception as e:
                 print(f"Live Search Error: {e}")

            # --- 3. Merge & Send ---
            combined = live_results + faiss_results
            try:
                self.wfile.write(json.dumps(combined).encode('utf-8'))
            except BrokenPipeError:
                pass # Client disconnected
        
        elif parsed_url.path == '/' or parsed_url.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                with open(os.path.join(os.path.dirname(__file__), 'templates/index.html'), 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b"Template not found")
        
        else:
            self.send_error(404)

print(f"🌍 Status Dashboard läuft auf http://localhost:{PORT}")
print(f"📖 Lese History von: {HISTORY_FILE}")

ThreadingTCPServer.allow_reuse_address = True
with ThreadingTCPServer(("", PORT), statusHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
