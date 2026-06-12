#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# install-service.sh — Install MS Rewards Bot sebagai service
# yang auto-start setiap kali Termux dibuka / HP restart.
# ============================================================

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================"
echo "  Install MS Rewards Service"
echo "======================================"

# 1. Pastikan termux-services terinstall
echo "[1/4] Cek termux-services..."
if ! command -v sv &>/dev/null; then
    echo "  📦 Install termux-services..."
    pkg install -y termux-services
fi

# 2. Setup runit service
echo "[2/4] Setup service directory..."
mkdir -p ~/.local/share/sv/ms-rewards/log

cat > ~/.local/share/sv/ms-rewards/run << 'SVEOF'
#!/data/data/com.termux/files/usr/bin/bash
exec 2>&1
cd /data/data/com.termux/files/home/ms-rewards-termux
exec python ms_rewards_bot.py
SVEOF
chmod +x ~/.local/share/sv/ms-rewards/run

cat > ~/.local/share/sv/ms-rewards/log/run << 'LOGEOF'
#!/data/data/com.termux/files/usr/bin/bash
exec svlogd -tt /data/data/com.termux/files/home/ms-rewards-termux/logs
LOGEOF
chmod +x ~/.local/share/sv/ms-rewards/log/run

# 3. Setup Termux:Boot (buat auto-start service pas boot)
echo "[3/4] Setup Termux:Boot..."

# Cek apakah Termux:Boot terinstall
if [ -d "/data/data/com.termux/files/home/.termux/boot/" ]; then
    BOOT_DIR="/data/data/com.termux/files/home/.termux/boot"
else
    # Fallback: pake termux-services langsung
    echo "  ℹ️ Termux:Boot ga terdeteksi, pake termux-services mode"
    BOOT_DIR=""
fi

if [ -n "$BOOT_DIR" ]; then
    cat > "$BOOT_DIR/ms-rewards" << 'BOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
# Auto-start MS Rewards service after boot
sleep 30
cd /data/data/com.termux/files/home/ms-rewards-termux
termux-wake-lock
bash run.sh &
BOOTEOF
    chmod +x "$BOOT_DIR/ms-rewards"
    echo "  ✅ Termux:Boot script dibuat"
fi

# 4. Enable service
echo "[4/4] Enable service..."
ln -sf ~/.local/share/sv/ms-rewards ~/.local/state/service/ms-rewards 2>/dev/null || true

echo ""
echo "======================================"
echo "  ✅ SERVICE TERINSTALL!"
echo "======================================"
echo ""
echo "START MANUAL:"
echo "  cd ~/ms-rewards-termux && bash run.sh"
echo ""
echo "CEK SERVICE:"
echo "  sv status ms-rewards"
echo ""
echo "STOP SERVICE:"
echo "  sv down ms-rewards"
echo ""
echo "LIHAT LOG:"
echo "  tail -f logs/current"
echo "  tail -f bot.log"
echo ""
