# Catatan Implementasi

Dokumen ini menjelaskan rancangan teknis program.

---

## 1. File Program

Project hanya menggunakan tiga file Python utama:

```text
client.py
proxy.py
webserver.py
```

Tidak ada file helper Python tambahan.

---

## 2. `webserver.py`

Fungsi utama:

- HTTP server TCP port `8000`.
- UDP echo server port `9000`.
- Parsing request HTTP GET.
- Menyajikan file statis dari folder `HTML/`.
- Mengirim response HTTP valid dengan status:
  - `200 OK`
  - `400 Bad Request`
  - `404 Not Found`
  - `500 Internal Server Error`
- Logging ke `logs/webserver_tcp_log.csv` dan `logs/webserver_udp_log.csv`.
- Mode default multithread.
- Mode single-thread tersedia dengan argumen `--single`.

Alur HTTP server:

```text
accept koneksi TCP
-> baca HTTP request
-> parse method dan path
-> validasi method GET
-> cari file di HTML/
-> bangun HTTP response
-> kirim response
-> tulis log CSV
```

Alur UDP echo:

```text
terima datagram UDP
-> kirim balik payload yang sama
-> tulis log CSV
```

---

## 3. `proxy.py`

Fungsi utama:

- TCP proxy port `8080` untuk HTTP.
- UDP proxy port `9090` untuk QoS.
- Forward request HTTP ke webserver TCP `8000`.
- Forward datagram UDP ke webserver UDP `9000`.
- Caching response HTTP status `200 OK`.
- Deteksi cache `HIT` dan `MISS`.
- Timeout upstream default `5` detik.
- Error handling:
  - `400 Bad Request`
  - `502 Bad Gateway`
  - `504 Gateway Timeout`
- Logging ke `logs/proxy_tcp_log.csv` dan `logs/proxy_udp_log.csv`.

Alur TCP proxy:

```text
accept koneksi client
-> baca HTTP request
-> parse URL
-> cek cache
   -> jika HIT: kirim response cache
   -> jika MISS: forward ke webserver
-> jika status 200: simpan response ke cache
-> kirim response ke client
-> tulis log CSV
```

Alur UDP proxy:

```text
terima datagram dari client
-> kirim ke webserver UDP 9000
-> tunggu echo dari webserver
-> kirim balik ke client
-> tulis log CSV
```

Strategi cache:

- Nama file cache dibentuk dari hash SHA-256 path URL.
- Response disimpan sebagai raw HTTP response.
- Penulisan cache memakai file temporary lalu `os.replace()` agar lebih aman.
- Operasi cache dilindungi `threading.Lock()`.

---

## 4. `client.py`

Fungsi utama:

- Mode HTTP/TCP.
- Mode QoS/UDP.
- Pengujian single client.
- Pengujian HTTP multi-client dengan `--concurrent 5`.
- Perhitungan QoS:
  - RTT minimum
  - RTT rata-rata
  - RTT maksimum
  - latency
  - jitter
  - packet loss
  - throughput
- Logging ke:
  - `logs/client_http_log.csv`
  - `logs/client_qos_packet_log.csv`
  - `logs/client_qos_summary_log.csv`

Alur HTTP client:

```text
buat TCP socket
-> connect ke proxy 8080
-> kirim HTTP GET
-> terima response sampai koneksi ditutup
-> tampilkan status/body
-> tulis log CSV
```

Alur QoS UDP:

```text
buat UDP socket
-> untuk setiap seq:
   -> kirim payload "Ping <seq> <timestamp>" ke proxy 9090
   -> tunggu echo sampai timeout
   -> hitung RTT jika reply diterima
   -> tulis log per paket
-> hitung summary QoS
-> tulis log summary
```

---

## 5. Perhitungan QoS

### RTT / Latency

```text
RTT = waktu_terima_echo - waktu_kirim
```

Latency pada output menggunakan rata-rata RTT.

### Packet Loss

```text
Packet Loss (%) = (paket_hilang / paket_dikirim) * 100
```

### Jitter

Jitter dihitung dari variasi selisih RTT antar paket berurutan.

```text
Delta RTT = |RTT_i - RTT_(i-1)|
Jitter = standar deviasi Delta RTT
```

### Throughput

```text
Throughput (kbps) = total_bit_payload_diterima / durasi_pengujian / 1000
```

---

## 6. Kesesuaian dengan Materi

Implementasi menggunakan konsep socket dasar:

- `socket.AF_INET` untuk IPv4.
- `socket.SOCK_STREAM` untuk TCP.
- `socket.SOCK_DGRAM` untuk UDP.
- `bind()` untuk server/proxy listener.
- `listen()` dan `accept()` untuk TCP server.
- `connect()` dan `sendall()` untuk TCP client.
- `sendto()` dan `recvfrom()` untuk UDP.
- `threading.Thread` untuk menangani koneksi konkuren.
- timeout socket untuk mencegah blocking tanpa batas.

