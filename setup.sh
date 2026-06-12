#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# setup.sh — Setup MS Rewards Bot (HTTP version) di Termux
# Jalanin ini SEKALI aja setelah clone repo
# ============================================================

echo "========================================"
echo "  MS Rewards Bot — Termux Setup"
echo "  HTTP version (no browser needed)"
echo "========================================"
echo ""

# 1. Update & upgrade pkg
echo "[1/3] Update package list..."
pkg update -y && pkg upgrade -y

# 2. Install Python & dependencies
echo "[2/3] Install Python & requests..."
pkg install -y python git
pip install requests

# 3. Buat config dari template
echo "[3/3] Buat config.json..."
if [ ! -f "config.json" ]; then
    cp config.json.example config.json
    echo "  ✅ config.json dibuat dari template"
    echo "  ⚠️ EDIT dulu: nano config.json"
    echo "     Isi email & password akun Microsoft Rewards kamu"
else
    echo "  ℹ️ config.json sudah ada, skip"
fi

echo ""
echo "========================================"
echo "  ✅ SETUP SELESAI!"
echo "========================================"
echo ""
echo "LANJUTAN:"
echo "  1. EDIT config.json:       nano config.json"
echo "  2. AMBIL COOKIES:          python get_cookies.py"
echo "     (Ikutin instruksi — login Bing via browser HP)"
echo "  3. TEST JALAN:             python ms_rewards_bot.py"
echo "  4. AUTO-RUN LOOP:          bash run.sh"
echo ""
echo "CEK LOG:   tail -f bot.log"
echo ""
echo "⚡ LEBIH RINGAN — tanpa browser, cuma HTTP requests!"
echo ""
