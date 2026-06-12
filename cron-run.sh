#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# cron-run.sh — Jalanin bot SEKALI (buat cron / manual)
# ============================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Auto-detect Chromium untuk Termux
if [ -f "$PREFIX/bin/chromium" ] && [ ! -f "$HOME/.cache/ms-playwright/chromium" ]; then
    export PLAYWRIGHT_BROWSERS_PATH=0
    export MS_REWARDS_CHROMIUM_PATH="$PREFIX/bin/chromium"
fi

echo "🚀 MS Rewards Bot — $(date '+%Y-%m-%d %H:%M:%S')"
python ms_rewards_bot.py
echo "✅ Selesai — $(date '+%Y-%m-%d %H:%M:%S')"
