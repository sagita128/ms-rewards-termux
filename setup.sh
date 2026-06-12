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
echo "[1/6] Update package list..."
pkg update -y && pkg upgrade -y

# 2. Install dependencies
echo "[2/6] Install Python & dependencies..."
pkg install -y python git binutils

# 3. Install Playwright Python
echo "[3/6] Install Playwright..."
pip install playwright 2>&1 | tail -5

# 4. Setup Chromium
echo "[4/6] Setup Chromium browser..."
# Cek apakah playwright bundled browser udah ada
CHROMIUM_DIR="$HOME/.cache/ms-playwright"
if [ -d "$CHROMIUM_DIR" ] && ls "$CHROMIUM_DIR"/chromium-*/chrome-linux/chrome 2>/dev/null | head -1 >/dev/null; then
    echo "  ✅ Playwright Chromium sudah terinstall"
else
    echo "  ⏳ Download Chromium via Playwright..."
    # Coba download, kalo gagal fallback ke pkg
    if python -m playwright install chromium 2>&1; then
        echo "  ✅ Playwright Chromium berhasil di-download"
    else
        echo "  ⚠️ Download gagal, install Chromium via pkg..."
        pkg install -y x11-repo 2>/dev/null
        pkg install -y chromium 2>&1 | tail -3
        
        # Cek path chromium
        if [ -f "$PREFIX/bin/chromium" ] || [ -f "$PREFIX/bin/chromium-browser" ]; then
            echo "  ✅ Chromium terinstall via pkg"
            echo ""
            echo "  ⚠️ SETELAH SETUP, jalanin ini:"
            echo '     export PLAYWRIGHT_BROWSERS_PATH=0'
            echo '     export MS_REWARDS_CHROMIUM_PATH=$PREFIX/bin/chromium'
            echo ""
            echo "  Atau tambahin ke ~/.bashrc biar permanent:"
            echo "   echo 'export PLAYWRIGHT_BROWSERS_PATH=0' >> ~/.bashrc"
            echo "   echo 'export MS_REWARDS_CHROMIUM_PATH=\$PREFIX/bin/chromium' >> ~/.bashrc"
        else
            echo "  ❌ Gagal install Chromium! Coba manual:"
            echo "     pkg install x11-repo"
            echo "     pkg install chromium"
            echo "     python -m playwright install chromium"
        fi
    fi
fi

# 5. Setup termux-services
echo "[5/6] Setup termux-services..."
pkg install -y termux-services 2>/dev/null
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
echo "========================================"
echo "  ✅ SETUP SELESAI!"
echo "========================================"
echo ""
echo "LANJUTAN:"
echo "  1. EDIT config.json:   nano config.json"
echo "  2. TEST JALAN:         python ms_rewards_bot.py"
echo "  3. SETUP AUTO-RUN:     bash install-service.sh"
echo ""
echo "CEK LOG:   tail -f bot.log"
echo ""
