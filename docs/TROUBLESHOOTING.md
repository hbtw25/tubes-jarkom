# Troubleshooting

| Masalah | Penyebab Umum | Solusi |
|---|---|---|
| `Connection refused` | Webserver/proxy belum berjalan atau port salah | Jalankan `webserver.py`, lalu `proxy.py`, baru `client.py` |
| Browser tidak bisa membuka halaman | Browser mengakses port `8000`, bukan proxy | Buka `http://<IP_PROXY>:8080/` |
| Webserver tidak menemukan file | Folder `HTML/` tidak satu folder dengan `webserver.py` | Letakkan folder `HTML/` sejajar dengan `webserver.py` atau pakai `--web-root HTML` |
| Response `404 Not Found` | Path file salah atau file tidak ada | Cek nama file, contoh `/index.html`, `/qos.html`, `/tcpip.html` |
| Proxy selalu `MISS` | Cache belum terbentuk atau path berbeda | Jalankan request path yang sama dua kali |
| Cache tidak berubah | Folder `cache/` berisi cache lama | Hapus folder `cache/` lalu uji ulang |
| UDP `Request timed out` | Firewall memblokir UDP atau proxy/server UDP belum aktif | Izinkan UDP `9090` dan `9000`; pastikan proxy dan webserver berjalan |
| QoS tidak melewati proxy | Client diarahkan ke port `9000` | Untuk skenario dosen, arahkan client ke UDP proxy port `9090` |
| Multi-client lambat | Webserver dijalankan dengan `--single` | Jalankan `python webserver.py` tanpa `--single` |
| Port sudah digunakan | Ada proses lain memakai port yang sama | Matikan proses tersebut atau ubah port dengan argumen CLI |
| Wireshark tidak menangkap paket | Interface salah atau filter terlalu sempit | Pilih interface WiFi/LAN aktif dan gunakan filter `tcp.port==8000 || tcp.port==8080 || udp.port==9000 || udp.port==9090` |
| Log CSV tidak muncul | Program belum menerima request atau folder tidak bisa ditulis | Jalankan pengujian dan pastikan folder project dapat ditulis |

---

## Urutan Start yang Benar

```text
1. Jalankan webserver.py
2. Jalankan proxy.py
3. Jalankan client.py atau browser
```

---

## Port yang Harus Dibuka Firewall

| Port | Protokol | Fungsi |
|---:|---|---|
| 8000 | TCP | HTTP webserver |
| 9000 | UDP | UDP echo webserver |
| 8080 | TCP | HTTP proxy |
| 9090 | UDP | UDP proxy QoS |
