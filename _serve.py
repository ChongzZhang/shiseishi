import http.server
import socketserver
import os

PORT = 8766
DIR = r"C:\Users\zhangcz\Desktop\游戏\识色赋诗"

os.chdir(DIR)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving at http://0.0.0.0:{PORT}")
    print(f"Directory: {DIR}")
    httpd.serve_forever()
