"""
proxy.py - Progress 10%
Tubes Jaringan Komputer: Client-Proxy-Server berbasis socket Python

Status:
- Sudah ada struktur dasar proxy.
- Sudah listen pada port 8080.
- Sudah forward request TCP ke web server.
- Caching, cache HIT/MISS, error 502/504, dan multithreading penuh masih TODO.
"""

import socket
import threading
import time

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8080

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8000


def forward_to_server(request_bytes):
    """Meneruskan request dari client ke web server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.settimeout(5)
        server_socket.connect((WEB_SERVER_HOST, WEB_SERVER_PORT))
        server_socket.sendall(request_bytes)

        response = b""
        while True:
            data = server_socket.recv(4096)
            if not data:
                break
            response += data
        return response


def handle_client(client_socket, client_addr):
    start = time.time()
    try:
        request = client_socket.recv(4096)
        if not request:
            return

        first_line = request.decode("utf-8", errors="replace").splitlines()[0]
        print(f"[PROXY] Request dari {client_addr}: {first_line}")

        # TODO progress berikutnya:
        # 1. Parse URL dari first_line.
        # 2. Cek file cache.
        # 3. Jika HIT, kirim langsung dari cache.
        # 4. Jika MISS, forward ke server dan simpan response ke cache.
        response = forward_to_server(request)
        client_socket.sendall(response)

        elapsed_ms = (time.time() - start) * 1000
        print(f"[PROXY] Forward selesai, waktu respons: {elapsed_ms:.2f} ms")

    except socket.timeout:
        error = (
            "HTTP/1.1 504 Gateway Timeout\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 19\r\n"
            "\r\n"
            "Gateway Timeout\n"
        )
        client_socket.sendall(error.encode("utf-8"))
    except Exception as exc:
        print(f"[PROXY] Error: {exc}")
        error = (
            "HTTP/1.1 502 Bad Gateway\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 16\r\n"
            "\r\n"
            "Bad Gateway\n"
        )
        client_socket.sendall(error.encode("utf-8"))
    finally:
        client_socket.close()


def run_proxy():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_socket.bind((PROXY_HOST, PROXY_PORT))
        proxy_socket.listen(5)
        print(f"[PROXY] Listening pada port {PROXY_PORT}")

        while True:
            client_socket, client_addr = proxy_socket.accept()

            # Struktur thread sudah ada, tetapi belum diuji untuk 5 client konkuren.
            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_addr),
                daemon=True
            )
            thread.start()


if __name__ == "__main__":
    run_proxy()
