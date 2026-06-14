# Panduan Pengujian

Dokumen ini berisi langkah pengujian sistem Client–Proxy–Server.

---

## 1. Persiapan

Pastikan struktur folder pada Laptop A seperti berikut:

```text
.
├── webserver.py
├── proxy.py
└── HTML/
    ├── index.html
    ├── implementation.html
    ├── osi.html
    ├── qos.html
    ├── tcpip.html
    ├── css/
    ├── assets/
    └── status/
```

Pastikan Laptop A dan Laptop B berada dalam jaringan lokal yang sama.

Cek IP Laptop A:

Windows:

```bash
ipconfig
```

Linux/macOS:

```bash
ifconfig
```

atau:

```bash
ip addr
```

---

## 2. Menjalankan Sistem

### Terminal 1, Laptop A

```bash
python webserver.py
```

Output yang diharapkan:

```text
HTTP TCP server running on 0.0.0.0:8000
UDP echo server running on 0.0.0.0:9000
```

### Terminal 2, Laptop A

```bash
python proxy.py --server-host 127.0.0.1
```

Output yang diharapkan:

```text
TCP proxy listening on 0.0.0.0:8080
UDP proxy listening on 0.0.0.0:9090
```

### Terminal Laptop B

Ganti `<IP_LAPTOP_A>` dengan IP sebenarnya.

```bash
python client.py --mode http --proxy-host <IP_LAPTOP_A> --path /index.html
```

---

## 3. Pengujian HTTP 200 OK

```bash
python client.py --mode http --proxy-host <IP_LAPTOP_A> --path /index.html
```

Output yang diharapkan:

```text
Client-1 Status: HTTP/1.1 200 OK
Client-1 Response time: ... ms
Client-1 Bytes received: ...
```

Validasi pada log:

- `proxy_tcp_log.csv` mencatat status `200`.
- `webserver_tcp_log.csv` mencatat request dari IP proxy.

---

## 4. Pengujian 404 Not Found

```bash
python client.py --mode http --proxy-host <IP_LAPTOP_A> --path /missing.html
```

Output yang diharapkan:

```text
Client-1 Status: HTTP/1.1 404 Not Found
```

---

## 5. Pengujian Cache MISS dan HIT

Hapus cache sebelum pengujian awal jika perlu:

Windows:

```bash
rmdir /s /q cache
```

Linux/macOS:

```bash
rm -rf cache
```

Request pertama:

```bash
python client.py --mode http --proxy-host <IP_LAPTOP_A> --path /index.html
```

Log proxy harus berisi:

```text
cache=MISS
```

Request kedua dengan path yang sama:

```bash
python client.py --mode http --proxy-host <IP_LAPTOP_A> --path /index.html
```

Log proxy harus berisi:

```text
cache=HIT
```

Pada Wireshark, saat HIT tidak perlu ada request baru dari proxy ke web server untuk resource yang sama.

---

## 6. Pengujian QoS UDP

Client mengirim UDP ke proxy port `9090`. Proxy meneruskan ke web server port `9000`.

```bash
python client.py --mode qos --udp-host <IP_LAPTOP_A> --udp-port 9090 --count 10
```

Output yang diharapkan:

```text
Reply from <IP_LAPTOP_A>:9090: seq=1 bytes=... RTT=... ms
...
--- UDP QoS Statistics ---
Packets: sent=10, received=..., lost=...
Packet loss: ...%
RTT min/avg/max: .../.../... ms
Latency: ... ms
Jitter: ... ms
Throughput: ... kbps
```

Log yang dicek:

- `client_qos_packet_log.csv`
- `client_qos_summary_log.csv`
- `proxy_udp_log.csv`
- `webserver_udp_log.csv`

---

## 7. Pengujian Multi-client 5 Client

```bash
python client.py --mode http --proxy-host <IP_LAPTOP_A> --path /index.html --concurrent 5
```

Output yang diharapkan:

```text
Client-1 Status: HTTP/1.1 200 OK
Client-2 Status: HTTP/1.1 200 OK
Client-3 Status: HTTP/1.1 200 OK
Client-4 Status: HTTP/1.1 200 OK
Client-5 Status: HTTP/1.1 200 OK
```

Validasi:

- Log proxy menunjukkan thread berbeda.
- Log webserver menunjukkan request ditangani tanpa crash.
- Cache tetap konsisten.

---

## 8. Pengujian Browser

Buka browser dari Laptop B:

```text
http://<IP_LAPTOP_A>:8080/
```

Output yang diharapkan:

- Halaman `index.html` tampil.
- Log proxy mencatat request dari browser.
- Web server hanya menerima request dari proxy.

---

## 9. Pengujian Timeout Proxy

Matikan `webserver.py`, lalu jalankan client:

```bash
python client.py --mode http --proxy-host <IP_LAPTOP_A> --path /index.html
```

Output yang diharapkan:

```text
HTTP/1.1 504 Gateway Timeout
```

Jalankan kembali `webserver.py` setelah selesai.

---

## 10. Filter Wireshark

Gunakan filter:

```text
tcp.port==8000 || tcp.port==8080 || udp.port==9000 || udp.port==9090
```

Yang perlu dicapture:

1. TCP handshake client ke proxy port `8080`.
2. TCP handshake proxy ke webserver port `8000`.
3. UDP client ke proxy port `9090`.
4. UDP proxy ke webserver port `9000`.
5. Cache HIT tidak menghasilkan forward HTTP baru ke webserver untuk file yang sama.
