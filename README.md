# MS Rewards Bot — Termux Edition

> **Versi standalone** — terpisah dari server bot yang jalan di openclaw.  
> Khusus dijalankan di **Termux (Android)**. Auto jalan 24/7.

---

## ✨ Fitur

- ✅ **Login otomatis** ke Microsoft Rewards (handle "Use your password", "Stay signed in")
- ✅ **Daily Set** (3 cards) — klik otomatis via JS dispatchEvent
- ✅ **Desktop search** (30 pencarian) + **Mobile search** (20 pencarian)
- ✅ **Auto Claim** — "Ready to claim" → "Claim points"
- ✅ **Cek poin** tiap selesai
- ✅ **Multi-akun** — support banyak akun sekaligus
- ✅ **Auto loop** — jalan setiap 24 jam otomatis
- ✅ **Wake lock** — HP tetap terjaga pas bot jalan
- ✅ **Service mode** — auto-start pas boot / Termux dibuka

---

## 📦 Yang Dibutuhkan

| Item | Keterangan |
|------|-----------|
| **HP Android** | Minimal Android 8+ |
| **Termux** | Dari F-Droid ([download](https://f-droid.org/packages/com.termux/)) |
| **Termux:Boot** *(opsional)* | Biar auto-start pas boot |
| **Koneksi Internet** | WiFi / data |
| **Akun Microsoft** | Yang udah join Microsoft Rewards |

---

## 🚀 Cara Install

### 1. Install Termux dari F-Droid

⚠️ **JANGAN** dari Play Store — versinya udah usang.  
Download dari [f-droid.org](https://f-droid.org/packages/com.termux/).

### 2. Clone repo

Buka Termux, ketik:

```bash
pkg update && pkg upgrade -y
pkg install -y git
git clone https://github.com/BintangBot/ms-rewards-termux
cd ms-rewards-termux
```

### 3. Jalankan setup

```bash
bash setup.sh
```

Ini akan:
- Install Python, Git, Chromium
- Install Playwright + Chromium browser
- Setup termux-services
- Buat `config.json` dari template

### 4. Edit config.json

```bash
nano config.json
```

Isi email & password akun Microsoft Rewards kamu.

Contoh:
```json
{
  "accounts": [
    {
      "email": "emailkamu@outlook.com",
      "password": "password123"
    }
  ],
  "settings": {
    "desktop_searches": 30,
    "mobile_searches": 20,
    "min_delay_sec": 10,
    "max_delay_sec": 20
  }
}
```

### 5. Test jalan

```bash
python ms_rewards_bot.py
```

Biarkan sampe selesai (kira-kira 15-30 menit untuk 1 akun, tergantung delay).

---

## ⏱️ Auto 24/7

Ada 2 mode:

### Mode A: Loop (simple)

```bash
bash run.sh
```

Bot jalan terus — stelah selesai, tunggu 24 jam, jalan lagi.  
Cocok buat ditinggal aja di Termux background.

### Mode B: Service (recommended)

```bash
bash install-service.sh
```

- Bisa di-`sv start` / `sv stop`
- Auto-start pas boot (kalo ada Termux:Boot)
- Tetap jalan walaupun Termux di-close (pake termux-services)

---

## 📊 Cek Log

```bash
# Log utama (semua run)
tail -f bot.log

# Log run terakhir
cat last_run.log

# Log service mode
tail -f logs/current
```

---

## 🧹 Commands

| Command | Fungsi |
|---------|--------|
| `python ms_rewards_bot.py` | Jalanin bot sekali |
| `bash run.sh` | Jalanin bot loop 24 jam |
| `bash cron-run.sh` | Jalanin sekali (buat cron job) |
| `sv start ms-rewards` | Start service |
| `sv stop ms-rewards` | Stop service |
| `sv status ms-rewards` | Cek status service |
| `tail -f bot.log` | Monitor log real-time |

---

## ⚠️ Catatan Penting

1. **Termux dari F-Droid** — Jangan dari Play Store!
2. **Wake lock** — Otomatis aktif pas bot jalan, HP ga tidur
3. **Baterai** — Colokan listrik kalo mau running 24/7
4. **Akun** — Pastikan akun udah join Microsoft Rewards (bisa dicek di rewards.bing.com)
5. **Delay antar akun** — 15 menit biar ga kena rate limit Microsoft
6. **HP tidur pas bot jalan?** — Masuk Settings > Apps > Termux > Battery > **Unrestricted**

---

## 📁 Struktur File

```
ms-rewards-termux/
├── ms_rewards_bot.py      # Bot utama
├── config.json            # Konfigurasi (email, password)
├── config.json.example    # Template config
├── setup.sh               # Setup sekali jalan
├── run.sh                 # Loop 24/7 mode
├── cron-run.sh            # Run sekali mode
├── install-service.sh     # Install as service
├── bot.log                # Log semua run
├── last_run.log           # Log run terakhir
└── logs/                  # Log service mode
```

---

## 🔄 Update

```bash
cd ~/ms-rewards-termux
git pull
```

---

Dibuat oleh [@BintangBot](https://github.com/BintangBot) — **Terpisah dari server bot.**  
Khusus Termux Android. Jalan otomatis 24/7 tanpa henti.
