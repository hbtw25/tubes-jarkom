# Tugas Besar Jaringan Komputer

## Implementasi dan Analisis Kinerja Sistem Client–Proxy–Server Berbasis Socket Python

Project ini mengimplementasikan sistem **Client–Proxy–Server** berbasis socket Python untuk pengujian komunikasi **TCP HTTP**, **UDP QoS**, **proxy forwarding**, **cache HIT/MISS**, dan **multithreading**.

Program dibuat sesuai ketentuan tugas besar:

- `webserver.py` menjalankan HTTP server berbasis TCP pada port `8000`.
- `webserver.py` menjalankan UDP echo server pada port `9000`.
- `proxy.py` menjalankan TCP proxy pada port `8080`.
- `proxy.py` menjalankan UDP proxy pada port `9090`.
- `client.py` memiliki mode HTTP/TCP dan mode QoS/UDP.
- Proxy mendukung cache `HIT` dan `MISS`.
- Web server dan proxy mendukung multithreading.
- Client, proxy, dan server menyimpan log ke file CSV.
- Implementasi hanya menggunakan socket manual Python, tanpa framework web dan tanpa library HTTP tingkat tinggi.

---

## 1. Struktur Project

```text
.
├── client.py
├── proxy.py
├── webserver.py
├── README.md
├── .gitignore
├── docs/
│   ├── CATATAN_IMPLEMENTASI.md
│   ├── FORMAT_LOG.md
│   ├── PANDUAN_PENGUJIAN.md
│   └── TROUBLESHOOTING.md
├── HTML/                 # folder aset HTML dari dosen, letakkan manual di sini
├── cache/                # dibuat otomatis oleh proxy.py
└── logs/                 # dibuat otomatis oleh semua program
```

Catatan: folder `HTML/` berasal dari aset yang diberikan dosen. Struktur dan isi aset HTML tidak perlu diubah.

---

## 2. Kebutuhan Sistem

- Python 3.x
- Sistem operasi Windows, Linux, atau macOS
- Satu jaringan lokal yang sama untuk semua perangkat
- Wireshark untuk capture dan analisis paket
- Browser untuk validasi HTTP melalui proxy

Tidak menggunakan:

- Flask
- Django
- FastAPI
- requests
- http.server
- library HTTP tingkat tinggi lainnya

---

## 3. Topologi Kelompok 2 Orang

Pada kelompok 2 orang, `webserver.py` dan `proxy.py` dijalankan pada laptop yang sama, tetapi tetap sebagai dua proses berbeda.

```text
Laptop A:
- webserver.py
- proxy.py
- Wireshark

Laptop B:
- client.py
- Browser
```

Contoh konfigurasi:

| Komponen | Host | Port | Protokol |
|---|---|---:|---|
| Web Server HTTP | Laptop A | 8000 | TCP |
| Web Server UDP Echo | Laptop A | 9000 | UDP |
| Proxy HTTP | Laptop A | 8080 | TCP |
| Proxy UDP QoS | Laptop A | 9090 | UDP |
| Client | Laptop B | ephemeral | TCP/UDP |

Alur HTTP:

```text
Client -> Proxy TCP 8080 -> Web Server TCP 8000
```

Alur QoS UDP:

```text
Client -> Proxy UDP 9090 -> Web Server UDP 9000
```

---

## 4. Cara Menjalankan

### 4.1. Persiapan Folder HTML

Letakkan folder `HTML` dari dosen dalam folder yang sama dengan `webserver.py`.

```text
.
├── webserver.py
├── proxy.py
├── client.py
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

### 4.2. Menjalankan Web Server

Di Laptop A:

```bash
python webserver.py
```

Default:

- TCP HTTP: `0.0.0.0:8000`
- UDP Echo: `0.0.0.0:9000`
- Mode HTTP server: multithread

Menjalankan web server mode single-thread:

```bash
python webserver.py --single
```

Menentukan folder web root manual:

```bash
python webserver.py --web-root HTML
```

### 4.3. Menjalankan Proxy Server

Di Laptop A, buka terminal kedua:

```bash
python proxy.py --server-host 127.0.0.1
```

Default:

- TCP Proxy: `0.0.0.0:8080`
- UDP Proxy: `0.0.0.0:9090`
- Upstream TCP Web Server: `127.0.0.1:8000`
- Upstream UDP Web Server: `127.0.0.1:9000`
- Timeout: `5` detik

Jika web server berada di IP lain:

```bash
python proxy.py --server-host <IP_WEB_SERVER>
```

Mengubah timeout menjadi 10 detik:

```bash
python proxy.py --server-host 127.0.0.1 --timeout 10
```

### 4.4. Menjalankan Client HTTP

Di Laptop B:

```bash
python client.py --mode http --proxy-host <IP_LAPTOP_A> --path /index.html
```

Contoh:

```bash
python client.py --mode http --proxy-host 192.168.1.10 --path /index.html
```

Alias mode HTTP/TCP juga tersedia:

```bash
python client.py --mode tcp --proxy-host 192.168.1.10 --path /index.html
```

### 4.5. Menjalankan Client QoS UDP

QoS UDP diarahkan ke proxy UDP port `9090`.

```bash
python client.py --mode qos --udp-host <IP_LAPTOP_A> --udp-port 9090 --count 10
```

Contoh:

```bash
python client.py --mode qos --udp-host 192.168.1.10 --udp-port 9090 --count 10
```

Alias mode QoS/UDP juga tersedia:

```bash
python client.py --mode udp --udp-host 192.168.1.10 --udp-port 9090 --count 10
```

### 4.6. Menjalankan 5 Client HTTP Konkuren

```bash
python client.py --mode http --proxy-host <IP_LAPTOP_A> --path /index.html --concurrent 5
```

Contoh:

```bash
python client.py --mode http --proxy-host 192.168.1.10 --path /index.html --concurrent 5
```

### 4.7. Menguji dengan Browser

Buka browser dari Laptop B:

```text
http://<IP_LAPTOP_A>:8080/
```

Contoh:

```text
http://192.168.1.10:8080/
```

Browser harus mengakses proxy port `8080`, bukan langsung ke web server port `8000`.

---

## 5. Argumen Program

### 5.1. Argumen `webserver.py`

| Argumen | Default | Keterangan |
|---|---:|---|
| `--listen-host` | `0.0.0.0` | alamat bind server |
| `--tcp-port` | `8000` | port HTTP TCP |
| `--udp-port` | `9000` | port UDP echo |
| `--web-root` | otomatis `HTML/` | folder aset HTML |
| `--single` | false | menjalankan TCP HTTP mode single-thread |

### 5.2. Argumen `proxy.py`

| Argumen | Default | Keterangan |
|---|---:|---|
| `--listen-host` | `0.0.0.0` | alamat bind proxy |
| `--tcp-port` | `8080` | port TCP proxy HTTP |
| `--udp-port` | `9090` | port UDP proxy QoS |
| `--server-host` | `127.0.0.1` | alamat upstream web server |
| `--server-tcp-port` | `8000` | port upstream HTTP web server |
| `--server-udp-port` | `9000` | port upstream UDP echo server |
| `--timeout` | `5.0` | timeout koneksi ke server dalam detik |

### 5.3. Argumen `client.py`

| Argumen | Default | Keterangan |
|---|---:|---|
| `--mode` | wajib | `http`, `tcp`, `qos`, atau `udp` |
| `--proxy-host` | `127.0.0.1` | alamat proxy untuk HTTP |
| `--proxy-port` | `8080` | port TCP proxy |
| `--udp-host` | `127.0.0.1` | alamat proxy UDP untuk QoS |
| `--udp-port` | `9090` | port UDP proxy |
| `--path` | `/index.html` | path resource HTML |
| `--count` | `10` | jumlah paket UDP QoS |
| `--timeout` | `5.0` | timeout UDP per paket |
| `--interval` | `0.2` | jeda antar paket UDP |
| `--concurrent` | `1` | jumlah client HTTP konkuren |

---

## 6. Mekanisme Sistem

### 6.1. HTTP melalui Proxy

1. Client mengirim request HTTP GET ke proxy port `8080`.
2. Proxy memeriksa cache berdasarkan path URL.
3. Jika cache tersedia, proxy mengirim response langsung ke client dan mencatat `HIT`.
4. Jika cache tidak tersedia, proxy meneruskan request ke web server port `8000` dan mencatat `MISS`.
5. Web server membaca file dari folder `HTML/` dan mengirim response HTTP.
6. Proxy menyimpan response `200 OK` ke folder `cache/`.
7. Proxy mengirim response ke client.

### 6.2. UDP QoS melalui Proxy

1. Client mengirim payload UDP `Ping <seq> <timestamp>` ke proxy UDP port `9090`.
2. Proxy meneruskan payload ke web server UDP port `9000`.
3. Web server mengirim echo payload yang sama ke proxy.
4. Proxy mengirim echo tersebut kembali ke client.
5. Client menghitung RTT, latency, jitter, packet loss, dan throughput.

### 6.3. Multithreading

- Web server TCP membuat thread baru untuk setiap koneksi HTTP jika tidak memakai opsi `--single`.
- Web server UDP berjalan pada thread terpisah dari TCP server.
- Proxy TCP membuat thread baru untuk setiap koneksi client.
- Proxy UDP membuat thread baru untuk setiap datagram yang diterima.
- Operasi cache pada proxy memakai lock untuk mengurangi risiko race condition saat multi-client.

---

## 7. File Log CSV

Folder `logs/` dibuat otomatis saat program berjalan.

| File | Dibuat oleh | Isi utama |
|---|---|---|
| `webserver_tcp_log.csv` | `webserver.py` | request HTTP, status, byte, response time, thread |
| `webserver_udp_log.csv` | `webserver.py` | UDP echo, byte, response time |
| `proxy_tcp_log.csv` | `proxy.py` | URL, cache HIT/MISS, status, response time, thread |
| `proxy_udp_log.csv` | `proxy.py` | datagram UDP masuk/keluar, status, response time, thread |
| `client_http_log.csv` | `client.py` | status HTTP, byte response, response time |
| `client_qos_packet_log.csv` | `client.py` | log per paket UDP, RTT, timeout |
| `client_qos_summary_log.csv` | `client.py` | ringkasan QoS: RTT, packet loss, jitter, throughput |

---

## 8. Wireshark

Filter capture yang disarankan:

```text
tcp.port==8000 || tcp.port==8080 || udp.port==9000 || udp.port==9090
```

Yang perlu diverifikasi:

- HTTP client hanya menuju proxy `8080`.
- Proxy meneruskan HTTP ke web server `8000`.
- QoS UDP client menuju proxy `9090`.
- Proxy meneruskan UDP ke web server `9000`.
- TCP handshake terlihat pada port `8080` dan `8000`.
- Payload UDP berisi format `Ping <seq> <timestamp>`.
- Pada cache HIT, tidak ada request HTTP baru dari proxy ke web server untuk resource yang sama.

---

## 9. Skenario Pengujian Minimal

| No | Skenario | Perintah / Aksi | Output yang Diharapkan |
|---:|---|---|---|
| 1 | Start web server | `python webserver.py` | TCP 8000 dan UDP 9000 aktif |
| 2 | Start proxy | `python proxy.py --server-host 127.0.0.1` | TCP 8080 dan UDP 9090 aktif |
| 3 | HTTP 200 OK | client meminta `/index.html` | response HTML tampil |
| 4 | HTTP 404 | client meminta `/missing.html` | response `404 Not Found` |
| 5 | Cache MISS | request pertama `/index.html` | log proxy `MISS` |
| 6 | Cache HIT | request kedua `/index.html` | log proxy `HIT` |
| 7 | QoS UDP | `--mode qos --count 10` | RTT, packet loss, jitter, throughput tampil |
| 8 | Multi-client | `--concurrent 5` | 5 client mendapat response |
| 9 | Browser | buka `http://IP_PROXY:8080/` | halaman HTML tampil |
| 10 | Wireshark | pakai filter port | aliran paket sesuai topologi |

---

## 10. Troubleshooting Singkat

| Masalah | Penyebab Umum | Solusi |
|---|---|---|
| Connection refused | server/proxy belum jalan atau IP/port salah | jalankan urutan webserver -> proxy -> client |
| Browser tidak bisa membuka halaman | browser mengarah ke port salah | akses `http://IP_PROXY:8080/` |
| Cache selalu MISS | folder cache dihapus atau URL berbeda | ulangi request dengan path yang sama |
| UDP timeout | firewall memblokir UDP atau proxy/server UDP belum aktif | buka port UDP `9090` dan `9000` |
| Webserver tidak menemukan file | folder `HTML/` tidak sejajar dengan `webserver.py` | letakkan folder `HTML/` di folder project |
| Multi-client blocking | server berjalan mode single-thread | jalankan tanpa opsi `--single` |

Detail lengkap ada di folder `docs/`.

---

## 11. Cara Push ke GitHub

```bash
git init
git add .
git commit -m "Initial commit: client proxy server socket project"
git branch -M main
git remote add origin https://github.com/<username>/<nama-repo>.git
git push -u origin main
```

Sebelum push, pastikan tidak memasukkan file hasil runtime yang tidak diperlukan:

- `logs/`
- `cache/`
- `__pycache__/`
- `.venv/`

File tersebut sudah masuk `.gitignore`.

---

## 12. Referensi Materi

- Materi Tugas Besar Jaringan Komputer Modul 8
- Materi Socket Programming dengan Python
- Materi Web Server berbasis Socket
- Materi TCP
- Materi UDP
- Materi ICMP
