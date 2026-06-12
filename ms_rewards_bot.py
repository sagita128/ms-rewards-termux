#!/usr/bin/env python3
"""MS Rewards Bot for Termux — Playwright browser, multi-account, 24/7.
Optimized for Android/Termux: no proxy, simpler, Indonesian logging.
Just isi config.json, jalanin setup.sh, done."""
import time
import random
import re
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

# ─── Config ────────────────────────────────────────────────
BASE = Path(__file__).parent
CFG = BASE / "config.json"
LOG_FILE = BASE / "bot.log"
LOG_FILE_LAST = BASE / "last_run.log"

# ─── Logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE),
    ],
)
log = logging.getLogger("ms-rewards")

# ─── Search queries ─────────────────────────────────────────
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

TOPICS = [
    "teknologi", "kesehatan", "olahraga", "hiburan", "bisnis",
    "pendidikan", "wisata", "kuliner", "keuangan", "otomotif",
]

# Referral URL — pake referral sendiri biar dapet bonus poin buat akun baru
REFFERAL_URL = 'https://rewards.bing.com/welcome?rh=iQejxOqbtSA&ref=rafsrchae'

# ─── Helper functions ───────────────────────────────────────

def get_config():
    return json.loads(CFG.read_text())


def get_accounts():
    return get_config().get("accounts", [])


def get_settings():
    return get_config().get("settings", {})


def write_last_run(text):
    LOG_FILE_LAST.write_text(
        f"=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n{text}\n"
    )


# ─── Login ──────────────────────────────────────────────────

def login(pw, email, password):
    """Login ke Microsoft via Playwright. Returns (browser, context, page) or None."""
    log.info(f"  🔑 Login {email}...")
    try:
        launch_kwargs = dict(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        # Support Chromium path override via env var (untuk Termux)
        ch_path = os.environ.get("MS_REWARDS_CHROMIUM_PATH")
        if ch_path:
            launch_kwargs["executable_path"] = ch_path
            log.info(f"    📌 Chromium path: {ch_path}")
        browser = pw.chromium.launch(**launch_kwargs)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        page = context.new_page()
        page.set_default_timeout(30000)

        # Buka login page
        page.goto("https://login.live.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(6)

        # Email
        email_input = page.wait_for_selector(
            "#usernameEntry, input[name='loginfmt'], input[type='email']", timeout=15000
        )
        email_input.fill(email)
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(4)

        # "Use your password" link (klik kalo ada)
        try:
            if page.locator('text="Use your password"').is_visible(timeout=3000):
                page.click('text="Use your password"', timeout=6000)
                log.info("    📝 Klik 'Use your password'")
                time.sleep(3)
        except:
            pass

        # Password
        pwd_input = page.wait_for_selector(
            '#passwordEntry, input[name="passwd"], input[type="password"]', timeout=10000
        )
        pwd_input.fill(password)
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(6)

        # Handle post-login redirects
        for _ in range(6):
            title = page.title().lower()
            url = page.url
            if "stay" in title or "signed in" in title:
                page.evaluate(
                    """() => {
                        for (const b of document.querySelectorAll('button')) {
                            if (b.textContent.trim().toLowerCase() === 'no') { b.click(); break; }
                        }
                    }"""
                )
                log.info("    👋 Klik 'No' (stay signed in)")
                time.sleep(3)
            elif "copilot" in url or "sso" in url or "login.live.com" in url:
                page.goto("https://www.bing.com/", wait_until="domcontentloaded", timeout=30000)
                time.sleep(4)
                break
            else:
                break
            time.sleep(2)

        # Verifikasi login
        page.goto("https://www.bing.com/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        if "id_n" in page.content():
            log.info("  ✅ Login berhasil!")
            return browser, context, page
        else:
            log.warning("  ⚠️ Login tidak terverifikasi (id_n not found)")
            browser.close()
            return None

    except Exception as e:
        log.error(f"  ❌ Login gagal: {e}")
        try:
            browser.close()
        except:
            pass
        return None


# ─── Daily Set ─────────────────────────────────────────────

def do_daily_set(page):
    """Klik daily set cards di dashboard rewards."""
    log.info("  📋 Daily set...")
    try:
        page.goto("https://rewards.bing.com/", wait_until="domcontentloaded", timeout=45000)
        time.sleep(12)

        # Scroll untuk trigger lazy load
        for _ in range(4):
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(1)

        # Cari section daily set
        page.evaluate(
            "document.getElementById('dailyset')?.scrollIntoView({behavior:'smooth'})"
        )
        time.sleep(3)

        # Cari cards — retry beberapa kali
        cards = None
        for attempt in range(3):
            section = page.locator("#dailyset")
            cards = section.locator('a[href*="bing.com"]')
            if cards.count() > 0:
                break
            log.info(f"    ⏳ Menunggu daily set cards... ({attempt + 1}/3)")
            time.sleep(5)

        if not cards or cards.count() == 0:
            log.info("  ℹ️ Tidak ada daily set cards")
            return 0

        completed = 0
        for i in range(min(cards.count(), 3)):
            card = cards.nth(i)
            try:
                card.scroll_into_view_if_needed()
                time.sleep(1)
                # JS dispatchEvent — wajib untuk React handlers
                page.evaluate(
                    """(el) => {
                        el.removeAttribute('target');
                        el.dispatchEvent(
                            new MouseEvent('click', {bubbles: true, cancelable: true})
                        );
                    }""",
                    card.element_handle(),
                )
                log.info(f"  ✅ Daily task {i + 1} clicked")
                completed += 1
                time.sleep(8)

                # Tutup tab baru kalo ada
                if len(page.context.pages) > 1:
                    page.context.pages[-1].close()
                    time.sleep(2)

                # Kembali ke dashboard
                page.goto("https://rewards.bing.com/", wait_until="domcontentloaded", timeout=30000)
                time.sleep(10)

            except Exception as e:
                if "Execution context was destroyed" in str(e):
                    # Context destroyed = click SUCCESS (navigasi terjadi)
                    log.info(f"  ✅ Daily task {i + 1} clicked (navigasi terdeteksi)")
                    completed += 1
                    time.sleep(8)
                    page.goto(
                        "https://rewards.bing.com/", wait_until="domcontentloaded", timeout=30000
                    )
                    time.sleep(10)
                else:
                    log.warning(f"  ⚠️ Daily task {i + 1} error: {e}")

        log.info(f"  Daily set: {completed}/3")
        return completed
    except Exception as e:
        log.warning(f"  ⚠️ Daily set error: {e}")
        return 0


# ─── Bing Search ────────────────────────────────────────────

def do_browser_search(page, query):
    """Lakukan satu pencarian Bing via browser."""
    try:
        sb = page.wait_for_selector("#sb_form_q", timeout=10000)
        if not sb:
            raise Exception("Search box not found")
        sb.fill("")
        time.sleep(0.3)
        for ch in query:
            sb.type(ch, delay=random.randint(30, 80))
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(random.uniform(4, 7))
        try:
            page.evaluate("window.scrollBy(0, Math.random() * 400 + 100)")
        except:
            pass
        time.sleep(random.uniform(1, 3))
        return True
    except Exception as e:
        log.debug(f"  Search error: {e}")
        # Retry: reload Bing dan coba lagi
        try:
            page.goto("https://www.bing.com/", wait_until="load", timeout=30000)
            time.sleep(4)
            sb = page.wait_for_selector("#sb_form_q", timeout=8000)
            if sb:
                sb.fill("")
                time.sleep(0.3)
                for ch in query:
                    sb.type(ch, delay=random.randint(30, 80))
                time.sleep(0.5)
                page.keyboard.press("Enter")
                time.sleep(random.uniform(4, 7))
                return True
        except:
            pass
        return False


# ─── Claim Points ──────────────────────────────────────────

def claim_points(page):
    """Claim 'Ready to claim' points."""
    log.info("  🎁 Claim points...")
    try:
        page.goto("https://rewards.bing.com/", wait_until="load", timeout=45000)
        time.sleep(12)

        claimed = 0
        try:
            claim_card = page.locator("button", has_text="Ready to claim").first
            if claim_card.is_visible(timeout=5000):
                claim_card.click()
                log.info("  🖱️ Klik 'Ready to claim'")
                time.sleep(5)

                claim_btn = page.locator("button", has_text="Claim points").first
                if claim_btn.is_visible(timeout=5000):
                    claim_btn.click()
                    claimed += 1
                    log.info("  ✅ Points claimed!")
                    time.sleep(3)

                # Tutup modal
                try:
                    page.keyboard.press("Escape")
                    time.sleep(2)
                except:
                    pass
        except:
            pass

        if claimed == 0:
            log.info("  ℹ️ Tidak ada points to claim")
        return claimed
    except Exception as e:
        log.warning(f"  ⚠️ Claim error: {e}")
        return 0


# ─── Check Points ──────────────────────────────────────────

def check_rewards(page):
    """Cek poin yang tersedia."""
    try:
        page.goto("https://rewards.bing.com/", wait_until="load", timeout=45000)
        time.sleep(10)

        body = page.inner_text("body")
        # Cari angka standalone dengan class text-pageHeader
        try:
            pts_el = page.locator('[class*="text-pageHeader"]').first
            pts_text = pts_el.inner_text(timeout=3000)
            match = re.match(r"^(\d{1,4}(?:,\d{3})*)$", pts_text.strip())
            if match:
                pts = int(match.group(1).replace(",", ""))
                log.info(f"  💰 Points: {pts}")
                return pts
        except:
            pass

        # Fallback: cari angka di body text
        nums = re.findall(r"(\d{2,})", body)
        for n in nums:
            val = int(n)
            if 50 < val < 10000:
                log.info(f"  💰 Points (approx): {val}")
                return val

        log.info("  ℹ️ Points tidak ditemukan")
        return -1
    except Exception as e:
        log.warning(f"  ⚠️ Cek points error: {e}")
        return -1


# ─── Referral Enrollment ────────────────────────────────────

def enroll_or_skip(page):
    """Cek apakah akun udah enrolled di Rewards.
    Kalo belum, coba daftar via referral link biar dapet bonus poin.
    Returns True kalo sudah enrolled, False kalo belum."""
    try:
        page.goto('https://rewards.bing.com/', wait_until="load", timeout=45000)
        time.sleep(10)

        # Handle OAuth consent page dulu
        oauth_clicks = 0
        for attempt in range(15):
            cur = page.url
            cur_title = page.title()

            # Udah di dashboard rewards!
            if 'rewards.bing.com' in cur and 'welcome' not in cur.lower() and 'signin-oidc' not in cur.lower():
                has_points = page.locator('[class*="text-pageHeader"]').count() > 0
                if has_points:
                    log.info("  ✅ Udah di dashboard rewards (points visible)")
                else:
                    log.info("  ✅ Udah di dashboard rewards")
                return True

            # Di halaman OAuth — coba klik "Sign in"
            if 'login.live.com' in cur and ('oauth' in cur or 'authorize' in cur):
                try:
                    signin_link = page.locator('a:has-text("Sign in")').first
                    if signin_link.is_visible(timeout=2000):
                        log.info("  🔑 Klik 'Sign in' di halaman OAuth")
                        signin_link.click()
                        time.sleep(8)
                        oauth_clicks += 1
                        continue
                except:
                    pass
                if oauth_clicks >= 5:
                    log.info("  ⚠️ OAuth mentok 5x — coba referral enrollment...")
                    break
                # Coba button Accept/Continue
                for ct in ['Accept', 'Yes', 'Continue', 'Allow']:
                    try:
                        btn = page.locator(f'button:has-text("{ct}"), input[value*="{ct}"]').first
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            log.info(f"  ✅ Klik '{ct}' di consent page")
                            time.sleep(5)
                            oauth_clicks += 1
                            break
                    except:
                        continue
                time.sleep(3)
                continue

            time.sleep(5)

        # === REFERRAL ENROLLMENT ===
        log.info("  📝 Coba referral enrollment...")
        page.goto(REFFERAL_URL, wait_until="load", timeout=45000)
        time.sleep(10)

        for btn_text in ['Start earning', 'Join now', 'Join', 'Get started', 'Start', 'Sign up']:
            try:
                btn = page.locator(f'button:has-text("{btn_text}"), a:has-text("{btn_text}")').first
                if btn.is_visible(timeout=3000):
                    btn.click()
                    log.info(f"  ✅ Klik '{btn_text}' di halaman referral")
                    break
            except:
                continue

        # Tunggu OAuth chain setelah klik referral
        time.sleep(5)
        for i in range(15):
            time.sleep(4)
            cur = page.url
            if 'rewards.bing.com' in cur and 'welcome' not in cur.lower():
                time.sleep(2)
                if not page.url.lower().startswith('https://rewards.bing.com/'):
                    continue
                log.info("  ✅ Referral enrollment berhasil!")
                return True
            if 'login.live.com' in cur and ('oauth' in cur or 'authorize' in cur):
                try:
                    sl = page.locator('a:has-text("Sign in")').first
                    if sl.is_visible(timeout=2000):
                        sl.click()
                        time.sleep(8)
                        continue
                except:
                    pass
            log.info(f"  ⏳ Tunggu redirect referral... ({cur[:50]})")

        log.info("  ⚠️ Referral enrollment gagal — lanjut search aja")
        return False
    except Exception as e:
        log.warning(f"  Enrollment error: {e}")
        return False


# ─── Main ──────────────────────────────────────────────────

def run_bot():
    """Jalankan bot untuk semua akun — sekali run."""
    log.info(f"{'=' * 50}")
    log.info(f"🚀 MS REWARDS BOT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"{'=' * 50}")
    log.info(f"")

    config = get_config()
    accounts = config.get("accounts", [])
    settings = config.get("settings", {})
    desktop_target = settings.get("desktop_searches", 30)
    mobile_target = settings.get("mobile_searches", 20)
    delay_between = settings.get("delay_between_accounts_sec", 900)

    log.info(f"📊 Akun: {len(accounts)}")
    log.info(f"🔍 Desktop: {desktop_target} | Mobile: {mobile_target}")
    log.info(f"")

    summary = []

    with sync_playwright() as pw:
        for idx, acc in enumerate(accounts):
            email = acc["email"]
            password = acc["password"]
            log.info(f"{'─' * 45}")
            log.info(f"🎯 [{idx + 1}/{len(accounts)}] {email}")
            log.info(f"{'─' * 45}")

            # ── Login ──
            result = login(pw, email, password)
            if not result:
                summary.append(f"❌ {email} — Login gagal")
                continue

            browser, context, page = result
            acc_ok = True
            account_log = []

            try:
                # ── Cek enrollment ──
                enrolled = False
                try:
                    enrolled = enroll_or_skip(page)
                except Exception as e:
                    log.warning(f"  ⚠️ Enrollment check error: {e}")

                if not enrolled:
                    log.warning("  ⚠️ Akun belum enrolled — skip dashboard tasks, langsung search")
                    page.goto("https://www.bing.com/", wait_until="load", timeout=30000)
                    time.sleep(5)
                else:
                    account_log.append("Enrolled ✅")

                if enrolled:
                    # ── Daily set ──
                    try:
                        ds = do_daily_set(page)
                        account_log.append(f"Daily set: {ds}/3")
                    except Exception as e:
                        log.warning(f"  ⚠️ Daily set error: {e}")
                        account_log.append("Daily set: error")

                    # Recover page
                    page.goto("https://www.bing.com/", wait_until="load", timeout=30000)
                    time.sleep(5)

                # ── Desktop Searches ──
                log.info(f"  🔍 {desktop_target} DESKTOP searches...")
                desktop_ok = 0
                for i in range(desktop_target):
                    q = QUERIES[i % len(QUERIES)]
                    if do_browser_search(page, q):
                        desktop_ok += 1
                    if (i + 1) % 10 == 0:
                        log.info(f"  [{i + 1}/{desktop_target}] ✓ ({desktop_ok} ok)")
                    delay = random.uniform(settings.get("min_delay_sec", 10), settings.get("max_delay_sec", 20))
                    time.sleep(delay)
                log.info(f"  ✅ Desktop: {desktop_ok}/{desktop_target}")
                account_log.append(f"Desktop: {desktop_ok}/{desktop_target}")

                # ── Mobile Searches ──
                context.close()
                context = browser.new_context(
                    viewport={"width": 390, "height": 844},
                    user_agent=(
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 "
                        "Mobile/15E148 Safari/604.1"
                    ),
                    locale="en-US",
                    is_mobile=True,
                )
                page = context.new_page()
                page.set_default_timeout(30000)

                page.goto("https://www.bing.com/", wait_until="domcontentloaded", timeout=30000)
                time.sleep(4)

                log.info(f"  📱 {mobile_target} MOBILE searches...")
                mobile_ok = 0
                for i in range(mobile_target):
                    q = QUERIES[(i + desktop_target) % len(QUERIES)]
                    if do_browser_search(page, q):
                        mobile_ok += 1
                    if (i + 1) % 10 == 0:
                        log.info(f"  [{i + 1}/{mobile_target}] ✓ ({mobile_ok} ok)")
                    delay = random.uniform(
                        settings.get("min_delay_sec", 10), settings.get("max_delay_sec", 20)
                    )
                    time.sleep(delay)
                log.info(f"  ✅ Mobile: {mobile_ok}/{mobile_target}")
                account_log.append(f"Mobile: {mobile_ok}/{mobile_target}")

                # ── Claim ──
                if enrolled:
                    page.goto("https://www.bing.com/", wait_until="load", timeout=30000)
                    time.sleep(5)
                    try:
                        cp = claim_points(page)
                        account_log.append(f"Claim: {'✅' if cp > 0 else 'ℹ️ none'}")
                    except Exception as e:
                        log.warning(f"  ⚠️ Claim error: {e}")

                    # ── Cek Points ──
                    try:
                        pts = check_rewards(page)
                        account_log.append(f"Points: {pts}")
                    except:
                        pass

                summary.append(f"{'✅' if mobile_ok > 0 else '⚠️'} {email} — {' | '.join(account_log)}")

            except Exception as e:
                log.error(f"  ❌ Error akun {email}: {e}")
                summary.append(f"❌ {email} — Error: {e}")
            finally:
                try:
                    browser.close()
                except:
                    pass

            # ── Delay antar akun ──
            if idx < len(accounts) - 1:
                wait_min = delay_between // 60
                log.info(f"⏳ Tunggu {wait_min} menit ke akun berikutnya...")
                time.sleep(delay_between)

    # ── Selesai ──
    log.info(f"\n{'=' * 50}")
    log.info(f"📋 RINGKASAN — {datetime.now().strftime('%H:%M:%S')}")
    log.info(f"{'=' * 50}")
    for s in summary:
        log.info(f"  {s}")
    log.info(f"{'=' * 50}\n")

    # Simpan ke last_run.log
    write_last_run("\n".join(summary))


# ── Entry point ──────────────────────────────────────────

if __name__ == "__main__":
    run_bot()
