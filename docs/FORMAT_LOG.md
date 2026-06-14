# Format Log CSV

Semua komponen menyimpan log otomatis ke folder `logs/`.

---

## 1. Log Client HTTP

File:

```text
logs/client_http_log.csv
```

Kolom:

| Kolom | Keterangan |
|---|---|
| `timestamp` | waktu eksekusi |
| `client_id` | nomor client, terutama saat concurrent |
| `proxy_host` | alamat proxy |
| `proxy_port` | port proxy HTTP |
| `path` | path resource |
| `status` | status line HTTP |
| `bytes_received` | total byte response |
| `response_time_ms` | waktu response dalam ms |
| `error` | pesan error jika ada |

---

## 2. Log Client QoS Packet

File:

```text
logs/client_qos_packet_log.csv
```

Kolom:

| Kolom | Keterangan |
|---|---|
| `timestamp` | waktu pengiriman paket |
| `seq` | nomor urut paket |
| `destination_host` | alamat tujuan UDP, biasanya proxy |
| `destination_port` | port tujuan UDP, default 9090 |
| `payload` | isi payload UDP |
| `status` | `REPLY`, `TIMEOUT`, atau `INVALID` |
| `bytes` | byte yang diterima |
| `rtt_ms` | round trip time |
| `error` | error jika ada |

---

## 3. Log Client QoS Summary

File:

```text
logs/client_qos_summary_log.csv
```

Kolom:

| Kolom | Keterangan |
|---|---|
| `sent` | jumlah paket dikirim |
| `received` | jumlah paket diterima kembali |
| `lost` | jumlah paket hilang |
| `packet_loss_percent` | persentase packet loss |
| `min_rtt_ms` | RTT minimum |
| `avg_rtt_ms` | RTT rata-rata |
| `max_rtt_ms` | RTT maksimum |
| `latency_ms` | latency, memakai nilai rata-rata RTT |
| `jitter_ms` | variasi delay antar paket |
| `throughput_kbps` | throughput payload UDP berhasil |
| `duration_s` | durasi pengujian |

---

## 4. Log Proxy TCP

File:

```text
logs/proxy_tcp_log.csv
```

Kolom:

| Kolom | Keterangan |
|---|---|
| `timestamp` | waktu request |
| `client_ip` | IP client |
| `client_port` | port ephemeral client |
| `target` | path URL |
| `cache` | `HIT`, `MISS`, atau `-` |
| `status` | status HTTP |
| `bytes_sent` | byte response ke client |
| `response_time_ms` | waktu proses proxy |
| `thread` | nama thread yang menangani request |

---

## 5. Log Proxy UDP

File:

```text
logs/proxy_udp_log.csv
```

Kolom:

| Kolom | Keterangan |
|---|---|
| `timestamp` | waktu datagram diterima |
| `client_ip` | IP client |
| `client_port` | port client |
| `upstream_host` | alamat webserver UDP |
| `upstream_port` | port webserver UDP, default 9000 |
| `status` | `OK`, `TIMEOUT`, atau `ERROR` |
| `bytes_in` | byte dari client |
| `bytes_out` | byte kembali ke client |
| `response_time_ms` | waktu proses proxy UDP |
| `thread` | nama thread UDP proxy |

---

## 6. Log Webserver TCP

File:

```text
logs/webserver_tcp_log.csv
```

Kolom:

| Kolom | Keterangan |
|---|---|
| `timestamp` | waktu request |
| `client_ip` | IP pengirim request, seharusnya IP proxy |
| `client_port` | port pengirim request |
| `target` | path resource |
| `status` | status HTTP |
| `bytes_sent` | byte response |
| `response_time_ms` | waktu proses server |
| `thread` | nama thread server |

---

## 7. Log Webserver UDP

File:

```text
logs/webserver_udp_log.csv
```

Kolom:

| Kolom | Keterangan |
|---|---|
| `timestamp` | waktu echo |
| `client_ip` | IP pengirim UDP, seharusnya IP proxy |
| `client_port` | port UDP proxy upstream |
| `bytes` | ukuran payload |
| `response_time_ms` | waktu echo server |
