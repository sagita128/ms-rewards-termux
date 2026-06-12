#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# setup.sh — Setup MS Rewards Bot di Termux
# Jalanin ini SEKALI aja setelah clone repo
# ============================================================

set -e

echo "======================================"
echo "  MS Rewards Bot — Termux Setup"
echo "======================================"
echo ""

# 1. Update & upgrade pkg
echo "[1/6] Update package list..."
pkg update -y && pkg upgrade -y

# 2. Install dependencies
echo "[2/6] Install Python & dependencies..."
pkg install -y python git chromium

# 3. Install Playwright
echo "[3/6] Install Playwright Python..."
pip install playwright

# 4. Install Chromium browser untuk Playwright
echo "[4/6] Setup Playwright browsers..."
python -m playwright install chromium

# 5. Setup termux-services untuk auto-start
echo "[5/6] Setup termux-services..."
pkg install -y termux-services
mkdir -p ~/.termux/boot/ 2>/dev/null || true

# 6. Buat config dari template
echo "[6/6] Buat config.json..."
if [ ! -f "config.json" ]; then
    cp config.json.example config.json
    echo "  ✅ config.json dibuat dari template"
    echo "  ⚠️ EDIT dulu: nano config.json"
    echo "     Isi email & password akun Microsoft Rewards kamu"
else
    echo "  ℹ️ config.json sudah ada, skip"
fi

echo ""
echo "======================================"
echo "  ✅ SETUP SELESAI!"
echo "======================================"
echo ""
echo "LANJUTAN:"
echo "  1. EDIT config.json:  nano config.json"
echo "  2. TEST JALAN:        python ms_rewards_bot.py"
echo "  3. SETUP AUTO-RUN:    bash install-service.sh"
echo ""
echo "CEK LOG:   cat bot.log"
echo ""
