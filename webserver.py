import argparse
import csv
import mimetypes
import os
import socket
import threading
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

HOST = "0.0.0.0"
TCP_PORT = 8000
UDP_PORT = 9000
BUFFER_SIZE = 4096
REQUEST_LIMIT = 1024 * 1024
SOCKET_TIMEOUT = 5.0

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_LOCK = threading.Lock()


def now_text():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def select_web_root(cli_root=None):
    if cli_root:
        return Path(cli_root).resolve()
    for name in ("HTML", "HTML for TESTING"):
        candidate = BASE_DIR / name
        if candidate.is_dir():
            return candidate.resolve()
    return BASE_DIR.resolve()


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


def log_console(message):
    print(f"[{now_text()}] {message}", flush=True)


def http_response(status_code, reason, body=b"", content_type="text/html; charset=utf-8"):
    header = (
        f"HTTP/1.1 {status_code} {reason}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "Server: PythonSocketWebServer\r\n"
        "\r\n"
    ).encode("iso-8859-1")
    return header + body


def error_body(web_root, status_code, reason):
    page = web_root / "status" / f"{status_code}.html"
    try:
        if page.is_file():
            return page.read_bytes()
    except OSError:
        pass
    return f"<html><body><h1>{status_code} {reason}</h1></body></html>".encode("utf-8")


def safe_file_path(web_root, raw_target):
    target = urlsplit(raw_target).path
    target = unquote(target)
    if target == "/":
        target = "/index.html"

    candidate = (web_root / target.lstrip("/")).resolve()
    root = web_root.resolve()

    if candidate != root and not str(candidate).startswith(str(root) + os.sep):
        return None
    if candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate


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


def recv_http_request(conn):
    data = b""
    while b"\r\n\r\n" not in data and len(data) < REQUEST_LIMIT:
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
    return data


def handle_tcp_client(conn, addr, web_root):
    start = time.perf_counter()
    status_code = 500
    target = "-"
    bytes_sent = 0

    try:
        conn.settimeout(SOCKET_TIMEOUT)
        request = recv_http_request(conn)
        method, target, version = parse_request(request)

        if method != "GET" or not target or not version:
            body = b"<html><body><h1>400 Bad Request</h1></body></html>"
            response = http_response(400, "Bad Request", body)
            status_code = 400
            conn.sendall(response)
            bytes_sent = len(response)
            return

        file_path = safe_file_path(web_root, target)
        if file_path is None or not file_path.is_file():
            body = error_body(web_root, 404, "Not Found")
            response = http_response(404, "Not Found", body)
            status_code = 404
            conn.sendall(response)
            bytes_sent = len(response)
            return

        try:
            body = file_path.read_bytes()
            content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
            if content_type.startswith("text/") or file_path.suffix.lower() in {".html", ".css", ".js"}:
                content_type += "; charset=utf-8"
            response = http_response(200, "OK", body, content_type)
            status_code = 200
            conn.sendall(response)
            bytes_sent = len(response)
        except Exception:
            body = error_body(web_root, 500, "Internal Server Error")
            response = http_response(500, "Internal Server Error", body)
            status_code = 500
            conn.sendall(response)
            bytes_sent = len(response)
    except Exception:
        try:
            body = error_body(web_root, 500, "Internal Server Error")
            response = http_response(500, "Internal Server Error", body)
            conn.sendall(response)
            status_code = 500
            bytes_sent = len(response)
        except Exception:
            pass
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        thread_name = threading.current_thread().name
        log_console(f"TCP {addr[0]}:{addr[1]} {target} status={status_code} bytes={bytes_sent} time={elapsed_ms:.2f}ms thread={thread_name}")
        write_csv(
            "webserver_tcp_log.csv",
            ["timestamp", "client_ip", "client_port", "target", "status", "bytes_sent", "response_time_ms", "thread"],
            [now_text(), addr[0], addr[1], target, status_code, bytes_sent, f"{elapsed_ms:.2f}", thread_name],
        )
        try:
            conn.close()
        except Exception:
            pass


def tcp_server(listen_host, tcp_port, web_root, multithread=True):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((listen_host, tcp_port))
    server.listen(50)
    mode = "multithread" if multithread else "single"
    log_console(f"HTTP TCP server running on {listen_host}:{tcp_port}, mode={mode}, root={web_root}")

    while True:
        conn, addr = server.accept()
        if multithread:
            thread = threading.Thread(target=handle_tcp_client, args=(conn, addr, web_root), daemon=True)
            thread.start()
        else:
            handle_tcp_client(conn, addr, web_root)


def udp_server(listen_host, udp_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((listen_host, udp_port))
    log_console(f"UDP echo server running on {listen_host}:{udp_port}")

    while True:
        data, addr = server.recvfrom(65535)
        start = time.perf_counter()
        server.sendto(data, addr)
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_console(f"UDP echo {addr[0]}:{addr[1]} bytes={len(data)} time={elapsed_ms:.2f}ms")
        write_csv(
            "webserver_udp_log.csv",
            ["timestamp", "client_ip", "client_port", "bytes", "response_time_ms"],
            [now_text(), addr[0], addr[1], len(data), f"{elapsed_ms:.2f}"],
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-host", default=HOST)
    parser.add_argument("--tcp-port", type=int, default=TCP_PORT)
    parser.add_argument("--udp-port", type=int, default=UDP_PORT)
    parser.add_argument("--web-root", default=None)
    parser.add_argument("--single", action="store_true")
    args = parser.parse_args()

    web_root = select_web_root(args.web_root)

    udp_thread = threading.Thread(target=udp_server, args=(args.listen_host, args.udp_port), daemon=True)
    udp_thread.start()
    tcp_server(args.listen_host, args.tcp_port, web_root, multithread=not args.single)


if __name__ == "__main__":
    main()
