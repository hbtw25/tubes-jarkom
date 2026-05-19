# Laporan Sementara Tugas Besar - Progress 10%

## 1. Latar Belakang Singkat

Tugas besar ini membahas implementasi sistem jaringan dengan arsitektur Client–Proxy–Server. Sistem ini menggunakan socket programming Python untuk memahami komunikasi TCP dan UDP, mekanisme forwarding, caching, serta pengukuran Quality of Service.

Pada progress 10%, pengerjaan difokuskan pada pembentukan struktur dasar proyek dan skeleton kode tiga komponen utama, yaitu `client.py`, `proxy.py`, dan `webserver.py`.

## 2. Tujuan Progress 10%

Tujuan progress awal ini adalah:

1. Membuat struktur tiga file utama sesuai ketentuan.
2. Menyiapkan konfigurasi port dasar:
   - Web Server TCP: 8000
   - Proxy TCP: 8080
   - UDP Echo: 9000
3. Membuat koneksi TCP sederhana dari client ke proxy.
4. Membuat forwarding awal dari proxy ke web server.
5. Membuat web server sederhana yang dapat mengembalikan response HTTP.

## 3. Arsitektur Awal

Alur komunikasi yang mulai dibangun:

```text
Client -> Proxy Server -> Web Server
```

Pada tahap ini, client tidak berkomunikasi langsung dengan web server untuk request HTTP. Client mengirim request ke proxy pada port 8080, kemudian proxy meneruskan request tersebut ke web server pada port 8000.

## 4. Implementasi Sementara

### 4.1 Client

Client memiliki mode TCP sederhana untuk mengirim HTTP GET ke proxy. Mode UDP masih belum diimplementasikan dan diberi TODO.

### 4.2 Proxy Server

Proxy sudah dapat menerima request TCP dari client dan meneruskan request tersebut ke web server. Pada progress ini, proxy belum memiliki mekanisme cache HIT/MISS.

### 4.3 Web Server

Web server sudah dapat menerima request GET sederhana dan mengembalikan halaman HTML dasar. Jika path tidak dikenali, server mengembalikan response 404 Not Found.

## 5. Batasan Progress 10%

Beberapa fitur utama belum dikerjakan, yaitu:

- Caching pada proxy.
- UDP echo server.
- UDP pinger pada client.
- Perhitungan QoS.
- Pengujian multithreading 5 client.
- Capture dan analisis Wireshark.
- Laporan akhir lengkap dan slide presentasi.

## 6. Kesimpulan Sementara

Progress 10% telah menghasilkan kerangka awal sistem Client–Proxy–Server. Sistem belum lengkap, tetapi sudah memiliki dasar komunikasi TCP antara client, proxy, dan web server. Tahap selanjutnya adalah melengkapi static file handling, caching, UDP echo, dan pengukuran QoS.
