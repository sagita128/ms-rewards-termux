#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# cron-run.sh — Jalanin bot SEKALI (buat cron / manual)
# HTTP version — no browser needed
# ============================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "🚀 MS Rewards Bot (HTTP) — $(date '+%Y-%m-%d %H:%M:%S')"
python ms_rewards_bot.py
echo "✅ Selesai — $(date '+%Y-%m-%d %H:%M:%S')"
