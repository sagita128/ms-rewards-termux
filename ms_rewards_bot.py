#!/data/data/com.termux/files/usr/bin/python3
"""MS Rewards Bot for Termux — HTTP requests version (no browser).
Cuma pake requests library. Butuh cookies dari browser sekali doang.
Cara dapetin cookies ada di README atau ketik: python get_cookies.py"""
import time
import random
import re
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

import requests

# ─── Config ────────────────────────────────────────────────
BASE = Path(__file__).parent
CFG = BASE / "config.json"
COOKIES_FILE = BASE / "cookies.json"
LOG_FILE = BASE / "bot.log"

# ─── Logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(LOG_FILE)],
)
log = logging.getLogger("ms-rewards")

# ─── Constants ──────────────────────────────────────────────
DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.6422.165 Mobile Safari/537.36"
)

QUERIES = [
    "python tutorial 2026", "best laptop coding", "AI news today",
    "linux vs windows", "docker containers guide", "react vs vue 2026",
    "stock market update", "crypto analysis", "weather forecast",
    "latest movies 2026", "football results", "mount everest height",
    "resep nasi goreng", "wisata banyuwangi", "harga emas hari ini",
    "chatgpt vs gemini", "machine learning 2026", "bitcoin prediction",
    "best gaming monitor", "samsung galaxy review", "javascript tutorial",
    "web development 2026", "data science guide", "cybersecurity tips",
    "healthy breakfast", "best anime 2026", "minecraft update",
    "f1 standings 2026", "how to invest", "space exploration",
    "climate change news", "coffee recipes", "guitar lessons",
    "netflix series 2026", "tiktok trending", "best spotify playlists",
    "world cup 2026", "best movies netflix", "top destinations 2026",
    "start business", "iphone 18 release", "nike air max sale",
    "facts about space", "puppy training tips", "how make coffee",
    "pembangunan IKN", "gunung bromo", "sejarah majapahit",
    "budaya indonesia", "wisata raja ampat", "resep rendang",
    "teknologi AI terbaru", "harga bitcoin hari ini", "tips diet sehat",
    "olahraga pagi", "manfaat minum air putih", "cara investasi saham",
    "lowongan kerja 2026", "pendaftaran cpns 2026", "beasiswa luar negeri",
    "kereta cepat whoosh", "makanan khas jember", "sejarah prambanan",
    "rekomendasi novel", "film indonesia 2026", "musik terbaru 2026",
]

# ─── Helpers ────────────────────────────────────────────────

def get_config():
    return json.loads(CFG.read_text())


def load_cookies():
    """Load cookies dari cookies.json. Return dict atau None."""
    if not COOKIES_FILE.exists():
        log.warning("  ❌ cookies.json belum ada!")
        log.warning("  📖 Baca README atau jalanin: python get_cookies.py")
        return None
    data = json.loads(COOKIES_FILE.read_text())
    if isinstance(data, list):
        # Convert list of dicts ke flat dict
        return {c["name"]: c["value"] for c in data if "name" in c and "value" in c}
    return data


def make_headers(ua):
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.bing.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
    }


def do_search(cookies, ua, query, retry=2):
    """Lakukan satu search via HTTP GET."""
    headers = make_headers(ua)
    url = f"https://www.bing.com/search?q={requests.utils.quote(query)}&form=QBLH"
    
    for attempt in range(retry):
        try:
            r = requests.get(
                url,
                headers=headers,
                cookies=cookies,
                timeout=15,
                allow_redirects=True,
            )
            if r.status_code == 200:
                return True
            elif r.status_code == 429:
                log.warning("  ⚠️ Rate limited (429), tunggu...")
                time.sleep(30)
                continue
            else:
                log.debug(f"  Status: {r.status_code}")
                time.sleep(5)
                continue
        except Exception as e:
            log.debug(f"  Search error: {e}")
            time.sleep(5)
            continue
    return False


def check_logged_in(cookies):
    """Cek apakah cookies masih valid dengan visit Bing."""
    try:
        r = requests.get(
            "https://www.bing.com/",
            headers=make_headers(DESKTOP_UA),
            cookies=cookies,
            timeout=10,
        )
        # Kalo ada 'id_n' di response, berarti udah login
        return 'id_n' in r.text or 'Sign out' in r.text or 'Profile' in r.text
    except:
        return False


def check_points(cookies):
    """Cek poin dari dashboard rewards."""
    try:
        r = requests.get(
            "https://rewards.bing.com/",
            headers=make_headers(DESKTOP_UA),
            cookies=cookies,
            timeout=15,
        )
        # Coba extract poin dari HTML
        pts_patterns = [
            r'id="userBalance"[^>]*>([^<]+)',
            r'class="pointBalance"[^>]*>([^<]+)',
            r'balanceValue[^>]*>([^<]+)',
            r'rewards-balance[^>]*>([^<]+)',
            r'"balance"[^:]*:\s*"(\d+)"',
            r'"availablePoints"[^:]*:\s*(\d+)',
        ]
        for pat in pts_patterns:
            m = re.search(pat, r.text)
            if m:
                pts = m.group(1).strip().replace(",", "")
                try:
                    return int(pts)
                except:
                    pass
        # Fallback: cari angka 4 digit
        nums = re.findall(r"(\d{3,5})", r.text)
        for n in nums:
            val = int(n)
            if 100 < val < 10000:
                return val
        return -1
    except:
        return -1


# ─── Main ──────────────────────────────────────────────────

def run_bot():
    log.info(f"{'=' * 50}")
    log.info(f"🚀 MS REWARDS BOT (HTTP) — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"{'=' * 50}")
    log.info("")

    config = get_config()
    accounts = config.get("accounts", [])
    settings = config.get("settings", {})
    desktop_target = settings.get("desktop_searches", 30)
    mobile_target = settings.get("mobile_searches", 20)
    delay_min = settings.get("min_delay_sec", 8)
    delay_max = settings.get("max_delay_sec", 15)

    # Load cookies (sama untuk semua akun — dari browser yg login)
    cookies = load_cookies()
    if not cookies:
        return

    # Cek login
    if not check_logged_in(cookies):
        log.warning("  ❌ Cookies expired! Jalanin ulang: python get_cookies.py")
        return
    log.info("  ✅ Cookies valid (session aktif)")

    log.info(f"📊 Akun: {len(accounts)}")
    log.info(f"🔍 Desktop: {desktop_target} | Mobile: {mobile_target}")
    log.info("")

    summary = []

    for idx, acc in enumerate(accounts):
        email = acc["email"]
        log.info(f"{'─' * 45}")
        log.info(f"🎯 [{idx + 1}/{len(accounts)}] {email}")
        log.info(f"{'─' * 45}")

        account_log = []

        # ── Desktop Searches ──
        log.info(f"  🔍 {desktop_target} DESKTOP searches...")
        desktop_ok = 0
        for i in range(desktop_target):
            q = QUERIES[i % len(QUERIES)]
            if do_search(cookies, DESKTOP_UA, q):
                desktop_ok += 1
            if (i + 1) % 10 == 0:
                log.info(f"  [{i + 1}/{desktop_target}] ✓ ({desktop_ok} ok)")
            delay = random.uniform(delay_min, delay_max)
            time.sleep(delay)
        log.info(f"  ✅ Desktop: {desktop_ok}/{desktop_target}")
        account_log.append(f"Desktop: {desktop_ok}/{desktop_target}")

        # ── Mobile Searches ──
        log.info(f"  📱 {mobile_target} MOBILE searches...")
        mobile_ok = 0
        for i in range(mobile_target):
            q = QUERIES[(i + desktop_target) % len(QUERIES)]
            if do_search(cookies, MOBILE_UA, q):
                mobile_ok += 1
            if (i + 1) % 10 == 0:
                log.info(f"  [{i + 1}/{mobile_target}] ✓ ({mobile_ok} ok)")
            delay = random.uniform(delay_min, delay_max)
            time.sleep(delay)
        log.info(f"  ✅ Mobile: {mobile_ok}/{mobile_target}")
        account_log.append(f"Mobile: {mobile_ok}/{mobile_target}")

        # ── Cek Points ──
        time.sleep(5)
        pts = check_points(cookies)
        if pts > 0:
            log.info(f"  💰 Points: {pts}")
            account_log.append(f"Points: {pts}")
        else:
            log.info(f"  ℹ️ Points: {pts} (gagal baca)")
            account_log.append(f"Points: ?")

        summary.append(
            f"{'✅' if desktop_ok + mobile_ok > 0 else '⚠️'} {email} — {' | '.join(account_log)}"
        )

    # ── Selesai ──
    log.info(f"\n{'=' * 50}")
    log.info(f"📋 RINGKASAN — {datetime.now().strftime('%H:%M:%S')}")
    log.info(f"{'=' * 50}")
    for s in summary:
        log.info(f"  {s}")
    log.info(f"{'=' * 50}\n")


if __name__ == "__main__":
    # Pastikan requests terinstall
    try:
        import requests
    except ImportError:
        print("Install dulu: pip install requests")
        sys.exit(1)
    run_bot()
