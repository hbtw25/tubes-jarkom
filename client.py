"""
client.py - Progress 10%
Tubes Jaringan Komputer: Client-Proxy-Server berbasis socket Python

Status:
- Sudah ada struktur dasar client.
- Sudah bisa membuat HTTP GET request sederhana ke proxy.
- UDP pinger dan perhitungan QoS masih TODO.
"""

import socket
import argparse
import time

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8080
UDP_SERVER_HOST = "127.0.0.1"
UDP_SERVER_PORT = 9000


def http_get(path="/index.html", host=PROXY_HOST, port=PROXY_PORT):
    """Mengirim HTTP GET sederhana ke proxy."""
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.settimeout(5)
        client_socket.connect((host, port))
        client_socket.sendall(request.encode("utf-8"))

        response = b""
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            response += data

    print(response.decode("utf-8", errors="replace"))


def udp_ping(count=10, host=UDP_SERVER_HOST, port=UDP_SERVER_PORT):
    """
    TODO Progress berikutnya:
    - Kirim minimal 10 paket UDP.
    - Payload: Ping <seq> <timestamp>
    - Hitung RTT, packet loss, jitter, dan throughput.
    """
    print("[TODO] Modul UDP pinger belum diimplementasikan pada progress 10%.")
    print(f"Target rencana: {host}:{port}, jumlah paket: {count}")


def main():
    parser = argparse.ArgumentParser(description="Client progress 10%")
    parser.add_argument("--mode", choices=["tcp", "udp"], default="tcp")
    parser.add_argument("--path", default="/index.html")
    args = parser.parse_args()

    if args.mode == "tcp":
        http_get(args.path)
    else:
        udp_ping()


if __name__ == "__main__":
    main()
