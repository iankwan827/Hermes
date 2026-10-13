#!/usr/bin/env python3
"""Feishu OAuth - server only, waits for callback."""
import json, urllib.request, os, sys, http.server, threading, urllib.parse, time

APP_ID = os.environ["FEISHU_APP_ID"]
APP_SECRET = os.environ["FEISHU_APP_SECRET"]
TOKEN_FILE = os.path.expanduser("~/.hermes/profiles/main/feishu_user_token.json")
auth_code = None

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("OK".encode())
            print(f"GOT CODE: {auth_code[:8]}...", flush=True)
        else:
            self.send_response(400)
            self.end_headers()
    def log_message(self, fmt, *args): pass

server = http.server.HTTPServer(("localhost", 8765), Handler)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()
print("SERVER_READY", flush=True)

for i in range(120):
    if auth_code:
        break
    time.sleep(1)
else:
    print("TIMEOUT", flush=True)
    server.shutdown()
    sys.exit(1)

# Get tenant token
req_t = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"}
)
tenant = json.loads(urllib.request.urlopen(req_t).read())["tenant_access_token"]

# Exchange code
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token",
    data=json.dumps({"grant_type": "authorization_code", "code": auth_code}).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {tenant}"}
)
result = json.loads(urllib.request.urlopen(req).read())

if result["code"] == 0:
    token_data = {
        "access_token": result["data"]["access_token"],
        "refresh_token": result["data"]["refresh_token"],
        "token_type": result["data"].get("token_type", "Bearer"),
        "expires_in": result["data"].get("expires_in", 7200),
        "refresh_expires_in": result["data"].get("refresh_expires_in", 2592000),
        "scope": result["data"].get("scope", ""),
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"SUCCESS token saved", flush=True)
else:
    print(f"FAILED: code={result['code']} msg={result.get('message','')}", flush=True)

server.shutdown()
