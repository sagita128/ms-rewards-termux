#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# run.sh — Run MS Rewards Bot continuously (loop mode)
# Untuk 24/7 running di Termux.
# Jalanin: bash run.sh
# Atau via termux-services (lebih recommended)
# ============================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Auto-detect Chromium untuk Termux (Selenium)
if [ -f "$PREFIX/bin/chromium" ] && [ -z "$MS_REWARDS_CHROMIUM_PATH" ]; then
    export MS_REWARDS_CHROMIUM_PATH="$PREFIX/bin/chromium"
    echo "  📌 Chromium: $PREFIX/bin/chromium"
fi

echo "======================================"
echo "  MS Rewards Bot — Loop Mode"
echo "  PID: $$"
echo "  Cek log: tail -f bot.log"
echo "======================================"

# Wake lock biar HP ga tidur
termux-wake-lock 2>/dev/null || echo "⚠️ termux-wake-lock ga ada (skip)"

# Loop forever — jalan setiap 24 jam
while true; do
    echo ""
    echo "======================================"
    echo "  🚀 START: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "======================================"
    echo ""

    # Jalanin bot
    python ms_rewards_bot.py

    EXIT_CODE=$?
    echo ""
    echo "======================================"
    echo "  ✅ SELESAI: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "  Exit code: $EXIT_CODE"
    echo "======================================"
    echo ""

    # Cek apakah bot sukses atau error
    if [ $EXIT_CODE -ne 0 ]; then
        echo "⚠️ Bot error (exit=$EXIT_CODE), tunggu 5 menit lalu restart..."
        sleep 300
    else
        echo "⏳ Tunggu 24 jam sampe run berikutnya..."
        echo "   Next run: $(date -d '+24 hours' '+%Y-%m-%d %H:%M:%S')"
        sleep 86400  # 24 jam
    fi
done
