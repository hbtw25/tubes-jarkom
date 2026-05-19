# Tubes Jaringan Komputer - Progress 10%

## Judul
Implementasi dan Analisis Kinerja Sistem Client–Proxy–Server Berbasis Socket Python: Evaluasi Protokol TCP/UDP dan Parameter Quality of Service

## Status Progress
**Progress saat ini: 10%**

Progress ini baru berisi kerangka awal sistem agar struktur tugas besar sudah terbentuk, tetapi belum menjadi implementasi final.

## File yang Dibuat

1. `client.py`
   - Sudah ada mode TCP sederhana.
   - Bisa mengirim HTTP GET ke proxy.
   - Mode UDP masih berupa TODO.

2. `proxy.py`
   - Sudah listen pada port 8080.
   - Sudah menerima request dari client.
   - Sudah meneruskan request ke web server.
   - Caching belum diimplementasikan.

3. `webserver.py`
   - Sudah listen pada port 8000.
   - Sudah dapat membalas halaman HTML sederhana.
   - Sudah ada penanganan dasar 404.
   - UDP echo server belum diimplementasikan.

## Cara Menjalankan

Buka tiga terminal.

### Terminal 1 - Web Server
```bash
python webserver.py
```

### Terminal 2 - Proxy Server
```bash
python proxy.py
```

### Terminal 3 - Client
```bash
python client.py --mode tcp --path /index.html
```

## Fitur yang Sudah Selesai

| Komponen | Fitur | Status |
|---|---|---|
| Struktur file | 3 file Python utama | Selesai |
| Web Server | TCP server dasar port 8000 | Selesai |
| Web Server | Response HTML sederhana | Selesai |
| Proxy | Listen port 8080 | Selesai |
| Proxy | Forward request ke server | Selesai awal |
| Client | Kirim GET ke proxy | Selesai awal |

## Fitur yang Belum Selesai

| Fitur | Status |
|---|---|
| Cache HIT/MISS pada proxy | Belum |
| Simpan cache ke file lokal | Belum |
| UDP echo server | Belum |
| UDP pinger client | Belum |
| Statistik QoS RTT, packet loss, jitter, throughput | Belum |
| Pengujian 5 client konkuren | Belum |
| Wireshark capture | Belum |
| Laporan akhir lengkap | Belum |
| Slide presentasi | Belum |

## Rencana Progress Berikutnya

- Progress 20%: implementasi static file pada `webserver.py`.
- Progress 30%: implementasi cache MISS dan cache HIT pada `proxy.py`.
- Progress 40%: implementasi UDP echo server dan UDP pinger.
- Progress 50%: hitung statistik QoS dasar.
- Progress 60%: uji multithreading 5 client.
- Progress 70%: dokumentasi hasil pengujian.
- Progress 80%: analisis QoS dan cache.
- Progress 90%: laporan dan slide.
- Progress 100%: finalisasi, screenshot, Wireshark, dan pengumpulan.
