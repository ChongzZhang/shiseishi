import http.server
import socketserver
import subprocess
import sys
import os
import time
import threading

PORT = 8766
DIR = r"C:\Users\zhangcz\Desktop\游戏\识色赋诗"

os.chdir(DIR)

# Start HTTP server in a daemon thread
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
server_thread.start()

print(f"HTTP server running at http://0.0.0.0:{PORT}")
print(f"Serving: {DIR}")
print()

# Verify it's up
for i in range(10):
    try:
        import urllib.request
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=2)
        print("Server is reachable.")
        break
    except Exception:
        time.sleep(1)
else:
    print("WARNING: Server may not be fully up, but trying anyway...")

print("Starting cloudflared tunnel...")
print()

try:
    subprocess.run(["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{PORT}"], check=True)
except KeyboardInterrupt:
    print("\nTunnel interrupted.")
except subprocess.CalledProcessError as e:
    print(f"cloudflared error: {e}")
finally:
    httpd.shutdown()
    print("Server stopped.")
