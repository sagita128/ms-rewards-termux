#!/data/data/com.termux/files/usr/bin/python3
"""MS Rewards Bot for Termux — Selenium + Chromium, multi-account, 24/7.
Optimized for Android/Termux (no proxy, Indonesian logging).
Ganti Playwright -> Selenium karena Playwright gak support Termux/aarch64."""
import time
import random
import re
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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

# Referral URL
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


def make_driver(device="desktop"):
    """Buat Chrome WebDriver. device='desktop' atau 'mobile'."""
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    # Unique user-data-dir biar gak tabrakan
    uid = f"selenium_{int(time.time())}_{random.randint(1000,9999)}"
    opts.add_argument(f"--user-data-dir=/tmp/{uid}")
    opts.add_argument("--remote-debugging-port=0")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # Chromium path untuk Termux
    ch_path = os.environ.get("MS_REWARDS_CHROMIUM_PATH")
    if ch_path:
        opts.binary_location = ch_path
    else:
        # Auto-detect chromium binary (Termux)
        for p in [
            "/data/data/com.termux/files/usr/bin/chromium",
            "/data/data/com.termux/files/usr/bin/chromium-browser",
            "/data/data/com.termux/files/usr/lib/chromium/chrome",
        ]:
            if os.path.isfile(p):
                opts.binary_location = p
                break

    # Deteksi chromedriver
    cd_path = os.environ.get("MS_REWARDS_CHROMEDRIVER_PATH")
    if not cd_path:
        for p in [
            "/data/data/com.termux/files/usr/bin/chromedriver",
            "/data/data/com.termux/files/usr/lib/chromium/chromedriver",
            "/data/data/com.termux/files/usr/bin/chromium-browser",
        ]:
            if os.path.isfile(p):
                cd_path = p
                break

    # Disable Selenium Manager (gak support android/arch64)
    os.environ["SE_SELENIUM_MANAGER"] = "0"

    if device == "mobile":
        opts.add_argument("--window-size=390,844")
        opts.add_argument(
            "--user-agent=Mozilla/5.0 (Linux; Android 14; SM-S928B) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.6422.165 Mobile Safari/537.36"
        )
    else:
        opts.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )

    if cd_path:
        service = Service(executable_path=cd_path)
        driver = webdriver.Chrome(service=service, options=opts)
    else:
        # Fallback: biar Selenium cari di PATH (works on normal Linux, maybe not Termux)
        driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(10)
    return driver


def safe_find(driver, selector, timeout=15, by=By.CSS_SELECTOR):
    """Wait untuk element, return element atau None."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    except (TimeoutException, NoSuchElementException):
        return None


def safe_click(driver, selector, timeout=10, by=By.CSS_SELECTOR):
    """Click element kalo ada, return True/False."""
    el = safe_find(driver, selector, timeout, by)
    if el:
        try:
            el.click()
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].click()", el)
                return True
            except:
                pass
    return False


def safe_click_text(driver, text, timeout=10):
    """Click element by visible text."""
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[text()='{text}']"))
        )
        el.click()
        return True
    except:
        pass
    # Fallback: partial text
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text}')]"))
        )
        el.click()
        return True
    except:
        return False


# ─── Login ──────────────────────────────────────────────────

def login(driver, email, password):
    """Login ke Microsoft via Selenium."""
    log.info(f"  🔑 Login {email}...")
    try:
        driver.get("https://login.live.com/")
        time.sleep(6)

        # Email
        email_input = safe_find(driver, "#usernameEntry, input[name='loginfmt'], input[type='email']", timeout=15)
        if not email_input:
            log.warning("  ❌ Email input not found")
            return False
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(1)
        email_input.send_keys(Keys.RETURN)
        time.sleep(4)

        # "Use your password" link
        safe_click_text(driver, "Use your password", timeout=3)

        # Password
        pwd_input = safe_find(driver, '#passwordEntry, input[name="passwd"], input[type="password"]', timeout=10)
        if not pwd_input:
            log.warning("  ❌ Password input not found")
            return False
        pwd_input.clear()
        pwd_input.send_keys(password)
        time.sleep(1)
        pwd_input.send_keys(Keys.RETURN)
        time.sleep(6)

        # Handle post-login redirects
        for _ in range(6):
            title = driver.title.lower()
            url = driver.current_url
            if "stay" in title or "signed in" in title:
                driver.execute_script("""
                    for (const b of document.querySelectorAll('button')) {
                        if (b.textContent.trim().toLowerCase() === 'no') { b.click(); break; }
                    }
                """)
                log.info("    👋 Klik 'No' (stay signed in)")
                time.sleep(3)
            elif "copilot" in url or "sso" in url or "login.live.com" in url:
                driver.get("https://www.bing.com/")
                time.sleep(4)
                break
            else:
                break
            time.sleep(2)

        # Verifikasi
        driver.get("https://www.bing.com/")
        time.sleep(5)
        if "id_n" in driver.page_source:
            log.info("  ✅ Login berhasil!")
            return True
        else:
            log.warning("  ⚠️ Login tidak terverifikasi (id_n not found)")
            return False

    except Exception as e:
        log.error(f"  ❌ Login gagal: {e}")
        return False


# ─── Daily Set ─────────────────────────────────────────────

def do_daily_set(driver):
    """Klik daily set cards di dashboard rewards."""
    log.info("  📋 Daily set...")
    try:
        driver.get("https://rewards.bing.com/")
        time.sleep(12)

        # Scroll
        for _ in range(4):
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(1)

        driver.execute_script(
            "document.getElementById('dailyset')?.scrollIntoView({behavior:'smooth'})"
        )
        time.sleep(3)

        # Cari cards
        cards = None
        for attempt in range(3):
            try:
                section = driver.find_element(By.ID, "dailyset")
                cards = section.find_elements(By.CSS_SELECTOR, 'a[href*="bing.com"]')
                if cards:
                    break
            except:
                pass
            log.info(f"    ⏳ Menunggu daily set cards... ({attempt + 1}/3)")
            time.sleep(5)

        if not cards or len(cards) == 0:
            log.info("  ℹ️ Tidak ada daily set cards")
            return 0

        completed = 0
        for i in range(min(len(cards), 3)):
            try:
                card = cards[i]
                driver.execute_script("arguments[0].scrollIntoView(true);", card)
                time.sleep(1)
                # JS click for React handlers
                driver.execute_script("""
                    arguments[0].removeAttribute('target');
                    arguments[0].dispatchEvent(
                        new MouseEvent('click', {bubbles: true, cancelable: true})
                    );
                """, card)
                log.info(f"  ✅ Daily task {i + 1} clicked")
                completed += 1
                time.sleep(8)

                # Kembali ke dashboard
                driver.get("https://rewards.bing.com/")
                time.sleep(10)

            except Exception as e:
                log.warning(f"  ⚠️ Daily task {i + 1} error: {e}")

        log.info(f"  Daily set: {completed}/3")
        return completed
    except Exception as e:
        log.warning(f"  ⚠️ Daily set error: {e}")
        return 0


# ─── Bing Search ────────────────────────────────────────────

def do_browser_search(driver, query):
    """Lakukan satu pencarian Bing via browser."""
    try:
        sb = safe_find(driver, "#sb_form_q", timeout=10)
        if not sb:
            raise Exception("Search box not found")
        sb.clear()
        time.sleep(0.3)
        for ch in query:
            sb.send_keys(ch)
            time.sleep(random.uniform(0.03, 0.08))
        time.sleep(0.5)
        sb.send_keys(Keys.RETURN)
        time.sleep(random.uniform(4, 7))
        try:
            driver.execute_script("window.scrollBy(0, Math.random() * 400 + 100)")
        except:
            pass
        time.sleep(random.uniform(1, 3))
        return True
    except Exception as e:
        log.debug(f"  Search error: {e}")
        # Retry
        try:
            driver.get("https://www.bing.com/")
            time.sleep(4)
            sb = safe_find(driver, "#sb_form_q", timeout=8)
            if sb:
                sb.clear()
                time.sleep(0.3)
                for ch in query:
                    sb.send_keys(ch)
                    time.sleep(random.uniform(0.03, 0.08))
                time.sleep(0.5)
                sb.send_keys(Keys.RETURN)
                time.sleep(random.uniform(4, 7))
                return True
        except:
            pass
        return False


# ─── Claim Points ──────────────────────────────────────────

def claim_points(driver):
    """Claim 'Ready to claim' points."""
    log.info("  🎁 Claim points...")
    try:
        driver.get("https://rewards.bing.com/")
        time.sleep(12)
        claimed = 0

        # Cari tombol "Ready to claim"
        try:
            claim_card = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ready to claim')]"))
            )
            claim_card.click()
            log.info("  🖱️ Klik 'Ready to claim'")
            time.sleep(5)

            claim_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Claim points')]"))
            )
            claim_btn.click()
            claimed += 1
            log.info("  ✅ Points claimed!")
            time.sleep(3)
        except:
            pass

        if claimed == 0:
            log.info("  ℹ️ Tidak ada points to claim")
        return claimed
    except Exception as e:
        log.warning(f"  ⚠️ Claim error: {e}")
        return 0


# ─── Check Points ──────────────────────────────────────────

def check_rewards(driver):
    """Cek poin yang tersedia."""
    try:
        driver.get("https://rewards.bing.com/")
        time.sleep(10)
        body = driver.find_element(By.TAG_NAME, "body").text

        # Cari angka dengan class tertentu
        try:
            pts_el = driver.find_element(By.CSS_SELECTOR, '[class*="text-pageHeader"]')
            pts_text = pts_el.text.strip()
            match = re.match(r"^(\d{1,4}(?:,\d{3})*)$", pts_text)
            if match:
                pts = int(match.group(1).replace(",", ""))
                log.info(f"  💰 Points: {pts}")
                return pts
        except:
            pass

        # Fallback
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

def enroll_or_skip(driver):
    """Cek apakah akun udah enrolled di Rewards."""
    try:
        driver.get('https://rewards.bing.com/')
        time.sleep(10)

        oauth_clicks = 0
        for attempt in range(15):
            cur = driver.current_url
            cur_title = driver.title()

            if 'rewards.bing.com' in cur and 'welcome' not in cur.lower() and 'signin-oidc' not in cur.lower():
                try:
                    pts = driver.find_elements(By.CSS_SELECTOR, '[class*="text-pageHeader"]')
                    if pts:
                        log.info("  ✅ Udah di dashboard rewards (points visible)")
                    else:
                        log.info("  ✅ Udah di dashboard rewards")
                except:
                    log.info("  ✅ Udah di dashboard rewards")
                return True

            if 'login.live.com' in cur and ('oauth' in cur or 'authorize' in cur):
                if safe_click_text(driver, "Sign in", timeout=2):
                    log.info("  🔑 Klik 'Sign in' di halaman OAuth")
                    time.sleep(8)
                    oauth_clicks += 1
                    continue
                if oauth_clicks >= 5:
                    log.info("  ⚠️ OAuth mentok 5x — coba referral enrollment...")
                    break
                for ct in ['Accept', 'Yes', 'Continue', 'Allow']:
                    if safe_click_text(driver, ct, timeout=2):
                        log.info(f"  ✅ Klik '{ct}' di consent page")
                        time.sleep(5)
                        oauth_clicks += 1
                        break
                time.sleep(3)
                continue

            time.sleep(5)

        # Referral enrollment
        log.info("  📝 Coba referral enrollment...")
        driver.get(REFFERAL_URL)
        time.sleep(10)

        for btn_text in ['Start earning', 'Join now', 'Join', 'Get started', 'Start', 'Sign up']:
            if safe_click_text(driver, btn_text, timeout=3):
                log.info(f"  ✅ Klik '{btn_text}' di halaman referral")
                break

        time.sleep(5)
        for i in range(15):
            time.sleep(4)
            cur = driver.current_url
            if 'rewards.bing.com' in cur and 'welcome' not in cur.lower():
                time.sleep(2)
                if not driver.current_url.lower().startswith('https://rewards.bing.com/'):
                    continue
                log.info("  ✅ Referral enrollment berhasil!")
                return True
            if 'login.live.com' in cur and ('oauth' in cur or 'authorize' in cur):
                if safe_click_text(driver, "Sign in", timeout=2):
                    time.sleep(8)
                    continue
            log.info(f"  ⏳ Tunggu redirect referral... ({cur[:50]})")

        log.info("  ⚠️ Referral enrollment gagal — lanjut search aja")
        return False
    except Exception as e:
        log.warning(f"  Enrollment error: {e}")
        return False


# ─── Main ──────────────────────────────────────────────────

def run_bot():
    log.info(f"{'=' * 50}")
    log.info(f"🚀 MS REWARDS BOT (Selenium) — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"{'=' * 50}")
    log.info("")

    config = get_config()
    accounts = config.get("accounts", [])
    settings = config.get("settings", {})
    desktop_target = settings.get("desktop_searches", 30)
    mobile_target = settings.get("mobile_searches", 20)
    delay_between = settings.get("delay_between_accounts_sec", 900)

    log.info(f"📊 Akun: {len(accounts)}")
    log.info(f"🔍 Desktop: {desktop_target} | Mobile: {mobile_target}")
    log.info("")

    summary = []

    for idx, acc in enumerate(accounts):
        email = acc["email"]
        password = acc["password"]
        log.info(f"{'─' * 45}")
        log.info(f"🎯 [{idx + 1}/{len(accounts)}] {email}")
        log.info(f"{'─' * 45}")

        # ── Desktop driver ──
        driver = make_driver("desktop")
        acc_ok = True
        account_log = []

        try:
            # ── Login ──
            if not login(driver, email, password):
                summary.append(f"❌ {email} — Login gagal")
                driver.quit()
                continue

            # ── Cek enrollment ──
            enrolled = False
            try:
                enrolled = enroll_or_skip(driver)
            except Exception as e:
                log.warning(f"  ⚠️ Enrollment check error: {e}")

            if not enrolled:
                log.warning("  ⚠️ Akun belum enrolled — skip dashboard tasks, langsung search")
                driver.get("https://www.bing.com/")
                time.sleep(5)
            else:
                account_log.append("Enrolled ✅")

            if enrolled:
                # ── Daily set ──
                try:
                    ds = do_daily_set(driver)
                    account_log.append(f"Daily set: {ds}/3")
                except Exception as e:
                    log.warning(f"  ⚠️ Daily set error: {e}")
                    account_log.append("Daily set: error")

                driver.get("https://www.bing.com/")
                time.sleep(5)

            # ── Desktop Searches ──
            log.info(f"  🔍 {desktop_target} DESKTOP searches...")
            desktop_ok = 0
            for i in range(desktop_target):
                q = QUERIES[i % len(QUERIES)]
                if do_browser_search(driver, q):
                    desktop_ok += 1
                if (i + 1) % 10 == 0:
                    log.info(f"  [{i + 1}/{desktop_target}] ✓ ({desktop_ok} ok)")
                delay = random.uniform(settings.get("min_delay_sec", 10), settings.get("max_delay_sec", 20))
                time.sleep(delay)
            log.info(f"  ✅ Desktop: {desktop_ok}/{desktop_target}")
            account_log.append(f"Desktop: {desktop_ok}/{desktop_target}")

            # ── Tutup desktop driver, buka mobile ──
            driver.quit()
            driver = make_driver("mobile")
            driver.get("https://www.bing.com/")
            time.sleep(4)

            # ── Mobile Searches ──
            log.info(f"  📱 {mobile_target} MOBILE searches...")
            mobile_ok = 0
            for i in range(mobile_target):
                q = QUERIES[(i + desktop_target) % len(QUERIES)]
                if do_browser_search(driver, q):
                    mobile_ok += 1
                if (i + 1) % 10 == 0:
                    log.info(f"  [{i + 1}/{mobile_target}] ✓ ({mobile_ok} ok)")
                delay = random.uniform(
                    settings.get("min_delay_sec", 10), settings.get("max_delay_sec", 20)
                )
                time.sleep(delay)
            log.info(f"  ✅ Mobile: {mobile_ok}/{mobile_target}")
            account_log.append(f"Mobile: {mobile_ok}/{mobile_target}")

            # ── Claim & Check ──
            if enrolled:
                driver.get("https://www.bing.com/")
                time.sleep(5)
                try:
                    cp = claim_points(driver)
                    account_log.append(f"Claim: {'✅' if cp > 0 else 'ℹ️ none'}")
                except Exception as e:
                    log.warning(f"  ⚠️ Claim error: {e}")

                try:
                    pts = check_rewards(driver)
                    account_log.append(f"Points: {pts}")
                except:
                    pass

            summary.append(f"{'✅' if mobile_ok > 0 else '⚠️'} {email} — {' | '.join(account_log)}")

        except Exception as e:
            log.error(f"  ❌ Error akun {email}: {e}")
            summary.append(f"❌ {email} — Error: {e}")
        finally:
            try:
                driver.quit()
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

    write_last_run("\n".join(summary))


if __name__ == "__main__":
    run_bot()
