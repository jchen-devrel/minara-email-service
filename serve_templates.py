#!/usr/bin/env python3
"""
简单的 HTTP 服务器，用于本地查看 templates/minara 目录下的 HTML 文件
"""
import http.server
import socketserver
import os
import sys
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent
TEMPLATES_DIR = PROJECT_ROOT / "templates" / "minara"

class TemplateHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(TEMPLATES_DIR), **kwargs)
    
    def end_headers(self):
        # 添加 CORS 头，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    port = 8000
    
    # 检查端口是否被占用
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"无效的端口号: {sys.argv[1]}")
            sys.exit(1)
    
    # 切换到模板目录
    os.chdir(TEMPLATES_DIR)
    
    with socketserver.TCPServer(("", port), TemplateHandler) as httpd:
        print(f"服务器启动在 http://localhost:{port}")
        print(f"正在服务目录: {TEMPLATES_DIR}")
        print("\n可用的 HTML 文件:")
        for html_file in sorted(TEMPLATES_DIR.glob("*.html")):
            print(f"  - http://localhost:{port}/{html_file.name}")
        print("\n按 Ctrl+C 停止服务器")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n服务器已停止")

if __name__ == "__main__":
    main()

