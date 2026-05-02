# -*- coding: utf-8 -*-
import http.server
import socketserver
import os

PORT = 8888
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'updates')

os.chdir(DIRECTORY)
print(f"服务目录: {os.getcwd()}")
print(f"文件列表: {os.listdir('.')}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"更新包服务器已启动: http://localhost:{PORT}/update_v1.1.0.exe")
    print(f"按 Ctrl+C 停止服务器")
    httpd.serve_forever()