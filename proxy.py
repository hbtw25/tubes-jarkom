import argparse
import csv
import hashlib
import os
import socket
import threading
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

HOST = "0.0.0.0"
TCP_PORT = 8080
UDP_PORT = 9090
SERVER_HOST = "127.0.0.1"
SERVER_TCP_PORT = 8000
SERVER_UDP_PORT = 9000
BUFFER_SIZE = 4096
REQUEST_LIMIT = 1024 * 1024
TIMEOUT = 5.0

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
LOG_DIR = BASE_DIR / "logs"
CACHE_LOCK = threading.Lock()
LOG_LOCK = threading.Lock()


def now_text():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def log_console(message):
    print(f"[{now_text()}] {message}", flush=True)


def write_csv(filename, header, row):
    LOG_DIR.mkdir(exist_ok=True)
    path = LOG_DIR / filename
    with LOG_LOCK:
        new_file = not path.exists()
        with path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(header)
            writer.writerow(row)


def http_response(status_code, reason, body=b""):
    header = (
        f"HTTP/1.1 {status_code} {reason}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "Server: PythonSocketProxy\r\n"
        "\r\n"
    ).encode("iso-8859-1")
    return header + body


def recv_http_request(conn):
    data = b""
    while b"\r\n\r\n" not in data and len(data) < REQUEST_LIMIT:
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
    return data


def parse_request(data):
    try:
        text = data.decode("iso-8859-1")
        request_line = text.split("\r\n", 1)[0]
        parts = request_line.split()
        if len(parts) != 3:
            return None, None, None
        return parts[0], parts[1], parts[2]
    except Exception:
        return None, None, None


def normalize_target(raw_target):
    split = urlsplit(raw_target)
    path = unquote(split.path or "/")
    if path == "/":
        path = "/index.html"
    if ".." in Path(path).parts:
        return None
    if split.query:
        return path + "?" + split.query
    return path


def cache_path_for(target):
    safe_name = target.split("?", 1)[0].strip("/").replace("/", "_") or "index.html"
    digest = hashlib.sha256(target.encode("utf-8")).hexdigest()[:16]
    return CACHE_DIR / f"{digest}_{safe_name}.cache"


def response_status(response):
    try:
        line = response.split(b"\r\n", 1)[0].decode("iso-8859-1")
        parts = line.split()
        if len(parts) >= 2 and parts[0].startswith("HTTP/"):
            return int(parts[1])
    except Exception:
        pass
    return 0


def build_forward_request(target, server_host, server_port):
    split = urlsplit(target)
    path = split.path or "/"
    if split.query:
        path = path + "?" + split.query
    return (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {server_host}:{server_port}\r\n"
        "Connection: close\r\n"
        "User-Agent: PythonSocketProxy\r\n"
        "Accept: */*\r\n"
        "\r\n"
    ).encode("iso-8859-1")


def fetch_from_server(target, server_host, server_port, timeout):
    request = build_forward_request(target, server_host, server_port)
    response = b""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect((server_host, server_port))
        sock.sendall(request)
        while True:
            chunk = sock.recv(BUFFER_SIZE)
            if not chunk:
                break
            response += chunk
    return response


def handle_tcp_client(conn, addr, server_host, server_port, timeout):
    start = time.perf_counter()
    target = "-"
    cache_status = "-"
    status = 0
    bytes_sent = 0

    try:
        conn.settimeout(timeout)
        request = recv_http_request(conn)
        method, raw_target, version = parse_request(request)

        if method != "GET" or not raw_target or not version:
            body = b"<html><body><h1>400 Bad Request</h1></body></html>"
            response = http_response(400, "Bad Request", body)
            status = 400
            conn.sendall(response)
            bytes_sent = len(response)
            return

        target = normalize_target(raw_target)
        if target is None:
            body = b"<html><body><h1>400 Bad Request</h1></body></html>"
            response = http_response(400, "Bad Request", body)
            status = 400
            conn.sendall(response)
            bytes_sent = len(response)
            return

        CACHE_DIR.mkdir(exist_ok=True)
        cpath = cache_path_for(target)

        with CACHE_LOCK:
            if cpath.is_file():
                response = cpath.read_bytes()
                cache_status = "HIT"
                status = response_status(response)
                conn.sendall(response)
                bytes_sent = len(response)
                return

        cache_status = "MISS"
        try:
            response = fetch_from_server(target, server_host, server_port, timeout)
        except socket.timeout:
            body = b"<html><body><h1>504 Gateway Timeout</h1></body></html>"
            response = http_response(504, "Gateway Timeout", body)
            status = 504
            conn.sendall(response)
            bytes_sent = len(response)
            return
        except OSError:
            body = b"<html><body><h1>504 Gateway Timeout</h1></body></html>"
            response = http_response(504, "Gateway Timeout", body)
            status = 504
            conn.sendall(response)
            bytes_sent = len(response)
            return

        status = response_status(response)
        if status == 0:
            body = b"<html><body><h1>502 Bad Gateway</h1></body></html>"
            response = http_response(502, "Bad Gateway", body)
            status = 502
            conn.sendall(response)
            bytes_sent = len(response)
            return

        if status == 200:
            with CACHE_LOCK:
                tmp = cpath.with_suffix(".tmp")
                tmp.write_bytes(response)
                os.replace(tmp, cpath)

        conn.sendall(response)
        bytes_sent = len(response)
    except Exception:
        try:
            body = b"<html><body><h1>502 Bad Gateway</h1></body></html>"
            response = http_response(502, "Bad Gateway", body)
            conn.sendall(response)
            status = 502
            bytes_sent = len(response)
        except Exception:
            pass
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        thread_name = threading.current_thread().name
        log_console(f"TCP client={addr[0]}:{addr[1]} url={target} cache={cache_status} status={status} bytes={bytes_sent} time={elapsed_ms:.2f}ms thread={thread_name}")
        write_csv(
            "proxy_tcp_log.csv",
            ["timestamp", "client_ip", "client_port", "target", "cache", "status", "bytes_sent", "response_time_ms", "thread"],
            [now_text(), addr[0], addr[1], target, cache_status, status, bytes_sent, f"{elapsed_ms:.2f}", thread_name],
        )
        try:
            conn.close()
        except Exception:
            pass


def tcp_server(listen_host, tcp_port, server_host, server_port, timeout):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((listen_host, tcp_port))
    server.listen(50)
    log_console(f"TCP proxy listening on {listen_host}:{tcp_port}, upstream={server_host}:{server_port}, timeout={timeout}s")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(
            target=handle_tcp_client,
            args=(conn, addr, server_host, server_port, timeout),
            daemon=True,
        )
        thread.start()


def handle_udp_datagram(proxy_sock, data, client_addr, server_host, server_udp_port, timeout):
    start = time.perf_counter()
    status = "OK"
    bytes_back = 0

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as upstream:
            upstream.settimeout(timeout)
            upstream.sendto(data, (server_host, server_udp_port))
            response, _ = upstream.recvfrom(65535)
        proxy_sock.sendto(response, client_addr)
        bytes_back = len(response)
    except socket.timeout:
        status = "TIMEOUT"
    except OSError:
        status = "ERROR"
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        thread_name = threading.current_thread().name
        log_console(f"UDP client={client_addr[0]}:{client_addr[1]} status={status} bytes_in={len(data)} bytes_out={bytes_back} time={elapsed_ms:.2f}ms thread={thread_name}")
        write_csv(
            "proxy_udp_log.csv",
            ["timestamp", "client_ip", "client_port", "upstream_host", "upstream_port", "status", "bytes_in", "bytes_out", "response_time_ms", "thread"],
            [now_text(), client_addr[0], client_addr[1], server_host, server_udp_port, status, len(data), bytes_back, f"{elapsed_ms:.2f}", thread_name],
        )


def udp_server(listen_host, udp_port, server_host, server_udp_port, timeout):
    proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_sock.bind((listen_host, udp_port))
    log_console(f"UDP proxy listening on {listen_host}:{udp_port}, upstream={server_host}:{server_udp_port}, timeout={timeout}s")

    while True:
        data, client_addr = proxy_sock.recvfrom(65535)
        thread = threading.Thread(
            target=handle_udp_datagram,
            args=(proxy_sock, data, client_addr, server_host, server_udp_port, timeout),
            daemon=True,
        )
        thread.start()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-host", default=HOST)
    parser.add_argument("--tcp-port", type=int, default=TCP_PORT)
    parser.add_argument("--udp-port", type=int, default=UDP_PORT)
    parser.add_argument("--server-host", default=SERVER_HOST)
    parser.add_argument("--server-tcp-port", type=int, default=SERVER_TCP_PORT)
    parser.add_argument("--server-udp-port", type=int, default=SERVER_UDP_PORT)
    parser.add_argument("--timeout", type=float, default=TIMEOUT)
    args = parser.parse_args()

    udp_thread = threading.Thread(
        target=udp_server,
        args=(args.listen_host, args.udp_port, args.server_host, args.server_udp_port, args.timeout),
        daemon=True,
    )
    udp_thread.start()
    tcp_server(args.listen_host, args.tcp_port, args.server_host, args.server_tcp_port, args.timeout)


if __name__ == "__main__":
    main()
