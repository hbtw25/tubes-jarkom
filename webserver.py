"""
webserver.py - Progress 10%
Tubes Jaringan Komputer: Client-Proxy-Server berbasis socket Python

Status:
- Sudah ada struktur dasar web server TCP.
- Sudah listen pada port 8000.
- Sudah mengembalikan HTML sederhana untuk / dan /index.html.
- Static file lengkap, UDP echo server, logging lengkap, dan error handling lanjutan masih TODO.
"""

import socket
import threading
import time

WEB_HOST = "0.0.0.0"
WEB_PORT = 8000
UDP_PORT = 9000


def build_response(status_code, status_text, body, content_type="text/html; charset=utf-8"):
    body_bytes = body.encode("utf-8")
    header = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return header.encode("utf-8") + body_bytes


def handle_http_client(client_socket, client_addr):
    try:
        request = client_socket.recv(4096)
        if not request:
            return

        text = request.decode("utf-8", errors="replace")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        print(f"[WEB] Request dari {client_addr}: {first_line}")

        parts = first_line.split()
        if len(parts) < 2 or parts[0] != "GET":
            body = "<h1>400 Bad Request</h1>"
            response = build_response(400, "Bad Request", body)
        else:
            path = parts[1]
            if path in ["/", "/index.html"]:
                body = """
                <html>
                    <head><title>Progress 10%</title></head>
                    <body>
                        <h1>Client-Proxy-Server</h1>
                        <p>Web server dasar berhasil berjalan.</p>
                        <p>Status: progress 10%.</p>
                    </body>
                </html>
                """
                response = build_response(200, "OK", body)
            else:
                body = "<h1>404 Not Found</h1><p>File belum tersedia pada progress 10%.</p>"
                response = build_response(404, "Not Found", body)

        client_socket.sendall(response)

    except Exception as exc:
        print(f"[WEB] Error: {exc}")
        body = "<h1>500 Internal Server Error</h1>"
        client_socket.sendall(build_response(500, "Internal Server Error", body))
    finally:
        client_socket.close()


def run_http_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((WEB_HOST, WEB_PORT))
        server_socket.listen(5)
        print(f"[WEB] HTTP server running pada port {WEB_PORT}")

        while True:
            client_socket, client_addr = server_socket.accept()
            thread = threading.Thread(
                target=handle_http_client,
                args=(client_socket, client_addr),
                daemon=True
            )
            thread.start()


def run_udp_echo_server():
    """
    TODO progress berikutnya:
    - Jalankan UDP echo server pada port 9000.
    - Echo payload tanpa perubahan.
    - Integrasikan dengan thread terpisah dari HTTP server.
    """
    print(f"[TODO] UDP echo server port {UDP_PORT} belum aktif pada progress 10%.")


if __name__ == "__main__":
    # Progress 10%: baru HTTP server dasar.
    # Progress berikutnya: jalankan UDP echo di thread paralel.
    run_http_server()
