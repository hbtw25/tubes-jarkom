import argparse
import csv
import socket
import statistics
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit

BUFFER_SIZE = 4096
TCP_TIMEOUT = 5.0
UDP_TIMEOUT = 5.0
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_LOCK = threading.Lock()


def now_text():
    return time.strftime("%Y-%m-%d %H:%M:%S")


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


def make_path(path):
    if not path:
        return "/index.html"
    split = urlsplit(path)
    target = split.path or "/index.html"
    if not target.startswith("/"):
        target = "/" + target
    if split.query:
        target += "?" + split.query
    return target


def receive_all(sock):
    data = b""
    while True:
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
    return data


def tcp_request(client_id, proxy_host, proxy_port, path, timeout, print_body=True):
    target = make_path(path)
    request = (
        f"GET {target} HTTP/1.1\r\n"
        f"Host: {proxy_host}:{proxy_port}\r\n"
        "Connection: close\r\n"
        "User-Agent: PythonSocketClient\r\n"
        "Accept: */*\r\n"
        "\r\n"
    ).encode("iso-8859-1")

    start = time.perf_counter()
    status_line = "ERROR"
    size = 0
    error = ""

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((proxy_host, proxy_port))
            sock.sendall(request)
            response = receive_all(sock)
        elapsed_ms = (time.perf_counter() - start) * 1000
        size = len(response)
        header, _, body = response.partition(b"\r\n\r\n")
        status_line = header.split(b"\r\n", 1)[0].decode("iso-8859-1", errors="replace") if header else "NO RESPONSE"

        print(f"Client-{client_id} Status: {status_line}")
        print(f"Client-{client_id} Response time: {elapsed_ms:.2f} ms")
        print(f"Client-{client_id} Bytes received: {size}")

        if print_body:
            print("\n--- RESPONSE BODY ---")
            print(body.decode("utf-8", errors="replace"))
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        error = str(exc)
        print(f"Client-{client_id} ERROR: {error}")

    write_csv(
        "client_http_log.csv",
        ["timestamp", "client_id", "proxy_host", "proxy_port", "path", "status", "bytes_received", "response_time_ms", "error"],
        [now_text(), client_id, proxy_host, proxy_port, target, status_line, size, f"{elapsed_ms:.2f}", error],
    )
    return elapsed_ms, status_line, size, error


def tcp_worker(index, proxy_host, proxy_port, path, timeout):
    tcp_request(index, proxy_host, proxy_port, path, timeout, print_body=False)


def tcp_concurrent(proxy_host, proxy_port, path, count, timeout):
    threads = []
    for i in range(1, count + 1):
        thread = threading.Thread(target=tcp_worker, args=(i, proxy_host, proxy_port, path, timeout))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def udp_qos(server_host, server_port, count, timeout, interval):
    rtts = []
    sent = 0
    received = 0
    received_bytes = 0
    test_start = time.perf_counter()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)

        for seq in range(1, count + 1):
            timestamp = time.time()
            payload_text = f"Ping {seq} {timestamp}"
            payload = payload_text.encode("utf-8")
            sent += 1
            start = time.perf_counter()
            error = ""
            rtt_ms = 0.0
            status = "TIMEOUT"
            bytes_recv = 0

            sock.sendto(payload, (server_host, server_port))

            try:
                data, _ = sock.recvfrom(65535)
                end = time.perf_counter()
                rtt_ms = (end - start) * 1000
                bytes_recv = len(data)
                if data == payload:
                    status = "REPLY"
                    received += 1
                    received_bytes += len(data)
                    rtts.append(rtt_ms)
                    print(f"Reply from {server_host}:{server_port}: seq={seq} bytes={bytes_recv} RTT={rtt_ms:.2f} ms")
                else:
                    status = "INVALID"
                    error = "payload berbeda"
                    print(f"Reply from {server_host}:{server_port}: seq={seq} invalid payload")
            except socket.timeout:
                error = "timeout"
                print(f"Request timed out: seq={seq}")

            write_csv(
                "client_qos_packet_log.csv",
                ["timestamp", "seq", "destination_host", "destination_port", "payload", "status", "bytes", "rtt_ms", "error"],
                [now_text(), seq, server_host, server_port, payload_text, status, bytes_recv, f"{rtt_ms:.2f}", error],
            )

            if seq != count:
                time.sleep(interval)

    duration = time.perf_counter() - test_start
    lost = sent - received
    loss_percent = (lost / sent) * 100 if sent else 0.0

    if rtts:
        min_rtt = min(rtts)
        avg_rtt = sum(rtts) / len(rtts)
        max_rtt = max(rtts)
    else:
        min_rtt = avg_rtt = max_rtt = 0.0

    if len(rtts) >= 2:
        deltas = [abs(rtts[i] - rtts[i - 1]) for i in range(1, len(rtts))]
        jitter = statistics.pstdev(deltas) if len(deltas) > 1 else deltas[0]
    else:
        jitter = 0.0

    throughput_kbps = (received_bytes * 8 / duration / 1000) if duration > 0 else 0.0

    print("\n--- UDP QoS Statistics ---")
    print(f"Packets: sent={sent}, received={received}, lost={lost}")
    print(f"Packet loss: {loss_percent:.2f}%")
    print(f"RTT min/avg/max: {min_rtt:.2f}/{avg_rtt:.2f}/{max_rtt:.2f} ms")
    print(f"Latency: {avg_rtt:.2f} ms")
    print(f"Jitter: {jitter:.2f} ms")
    print(f"Throughput: {throughput_kbps:.2f} kbps")
    print(f"Duration: {duration:.2f} s")

    write_csv(
        "client_qos_summary_log.csv",
        ["timestamp", "destination_host", "destination_port", "sent", "received", "lost", "packet_loss_percent", "min_rtt_ms", "avg_rtt_ms", "max_rtt_ms", "latency_ms", "jitter_ms", "throughput_kbps", "duration_s"],
        [now_text(), server_host, server_port, sent, received, lost, f"{loss_percent:.2f}", f"{min_rtt:.2f}", f"{avg_rtt:.2f}", f"{max_rtt:.2f}", f"{avg_rtt:.2f}", f"{jitter:.2f}", f"{throughput_kbps:.2f}", f"{duration:.2f}"],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["http", "qos", "tcp", "udp"], required=True)
    parser.add_argument("--proxy-host", default="127.0.0.1")
    parser.add_argument("--proxy-port", type=int, default=8080)
    parser.add_argument("--udp-host", default="127.0.0.1")
    parser.add_argument("--udp-port", type=int, default=9090)
    parser.add_argument("--path", default="/index.html")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=UDP_TIMEOUT)
    parser.add_argument("--interval", type=float, default=0.2)
    parser.add_argument("--concurrent", type=int, default=1)
    args = parser.parse_args()

    if args.mode in {"http", "tcp"}:
        if args.concurrent > 1:
            tcp_concurrent(args.proxy_host, args.proxy_port, args.path, args.concurrent, TCP_TIMEOUT)
        else:
            tcp_request(1, args.proxy_host, args.proxy_port, args.path, TCP_TIMEOUT, print_body=True)
    else:
        udp_qos(args.udp_host, args.udp_port, args.count, args.timeout, args.interval)


if __name__ == "__main__":
    main()
