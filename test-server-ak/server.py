from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os

class PUTHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        print(body, flush=True)
        try:
            data = json.loads(body)

            attestation_key = data.get('attestation_key', '')
            uuid = data.get('uuid', '')

            if not attestation_key:
                raise ValueError("attestation_key is required")
            if not uuid:
                raise ValueError("uuid is required")

            print(f"Received UUID: {uuid}", flush=True)

            if not os.path.exists('/data/test.pub'):
                os.makedirs('/data', exist_ok=True)
                open('/data/test.pub', 'a').close()
                print("Created /data/test.pub", flush=True)

            with open('/data/test.pub', 'w') as f:
                f.write(attestation_key)

            print(f"Successfully wrote attestation key to /data/test.pub for UUID: {uuid}", flush=True)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())
        except Exception as e:
            print(f"Error: {e}", flush=True)
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 5001), PUTHandler)
    print('Server running on port 5001...', flush=True)
    server.serve_forever()
