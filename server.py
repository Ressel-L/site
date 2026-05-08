import http.server
import socketserver
import os

os.chdir(r'D:\trae\site')

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    print(f"Open http://localhost:{PORT} in your browser")
    httpd.serve_forever()