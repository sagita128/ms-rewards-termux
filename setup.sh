#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# setup.sh — Setup MS Rewards Bot di Termux
# Jalanin ini SEKALI aja setelah clone repo
# ============================================================

echo "========================================"
echo "  MS Rewards Bot — Termux Setup"
echo "========================================"
echo ""

# 1. Update & upgrade pkg
echo "[1/5] Update package list..."
pkg update -y && pkg upgrade -y

# 2. Install dependencies
echo "[2/5] Install Python & dependencies..."
pkg install -y python git binutils

# 3. Install Selenium
echo "[3/5] Install Selenium..."
pip install selenium

# 4. Install Chromium + ChromeDriver
echo "[4/5] Install Chromium browser & ChromeDriver..."
pkg install -y x11-repo
pkg install -y chromium

# Cek chromedriver
if command -v chromedriver &>/dev/null; then
    echo "  ✅ ChromeDriver: $(which chromedriver)"
elif [ -f "$PREFIX/lib/chromium/chromedriver" ]; then
    echo "  ✅ ChromeDriver: $PREFIX/lib/chromium/chromedriver"
    ln -sf "$PREFIX/lib/chromium/chromedriver" "$PREFIX/bin/chromedriver" 2>/dev/null || true
else
    echo "  ⚠️ ChromeDriver tidak ditemukan, coba install manual:"
    echo "     pkg install chromium-chromedriver"
fi

# Auto-detect path
if [ -f "$PREFIX/bin/chromium" ]; then
    echo ""
    echo "  ✅ Chromium terinstall di: $PREFIX/bin/chromium"
    echo "  ⚠️ Tambahin ini ke ~/.bashrc biar permanent:"
    echo "   echo 'export MS_REWARDS_CHROMIUM_PATH=\$PREFIX/bin/chromium' >> ~/.bashrc"
    echo ""
fi

# 5. Setup termux-services
echo "[5/5] Setup termux-services..."
pkg install -y termux-services 2>/dev/null
mkdir -p ~/.termux/boot/ 2>/dev/null || true

# Buat config dari template
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
echo "  2. EXPORT Chromium path:   export MS_REWARDS_CHROMIUM_PATH=\$PREFIX/bin/chromium"
echo "  3. TEST JALAN:             python ms_rewards_bot.py"
echo "  4. SETUP AUTO-RUN:         bash install-service.sh"
echo ""
echo "CEK LOG:   tail -f bot.log"
echo ""
