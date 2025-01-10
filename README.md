# MidasRWA BOT
MidasRWA BOT

Register Here : [MidasRWA](https://t.me/MidasRWA_bot/app?startapp=ref_b6243c03-25ae-43f0-9667-5defd6c43b9b)

## Fitur

  - Auto Get Account Information
  - Auto Claim Daily Check-In
  - Auto Claim Refferal
  - Auto Play Tap Tap
  - Auto Complete Task

## Prasyarat

Pastikan Anda telah menginstal Python3.9 dan PIP.

## Instalasi

1. **Kloning repositori:**
   ```bash
   git clone https://github.com/vonssy/MidasRWA-BOT.git
   ```
   ```bash
   cd MidasRWA-BOT
   ```

2. **Instal Requirements:**
   ```bash
   pip install -r requirements.txt #or pip3 install -r requirements.txt
   ```

## Konfigurasi

- **query.txt:** Anda akan menemukan file `query.txt` di dalam direktori proyek. Pastikan `query.txt` berisi data yang sesuai dengan format yang diharapkan oleh skrip. Berikut adalah contoh format file:

  ```bash
  query_id=
  user=
  ```

- **manual_proxy.txt:** Anda akan menemukan file `manual_proxy.txt` di dalam direktori proyek. Pastikan `manual_proxy.txt` berisi data yang sesuai dengan format yang diharapkan oleh skrip. Berikut adalah contoh format file:
  ```bash
    ip:port # Default Protcol HTTP.
    protocol://ip:port
    protocol://user:pass@ip:port
  ```

## Jalankan

```bash
python bot.py #or python3 bot.py
```

## Note
  1. If an error occurs during the first query processing, it means it was blocked by Cloudflare. restart again, again, and again.
  2. If an error occurs in other than the first query, then the query is invalid, replace it.

## Penutup

Terima kasih telah mengunjungi repository ini, jangan lupa untuk memberikan kontribusi berupa follow dan stars.
Jika Anda memiliki pertanyaan, menemukan masalah, atau memiliki saran untuk perbaikan, jangan ragu untuk menghubungi saya atau membuka *issue* di repositori GitHub ini.

**vonssy**