#!/data/data/com.termux/files/usr/bin/python3
"""get_cookies.py — Bantu ambil cookies dari browser untuk MS Rewards Bot.
Jalanin: python get_cookies.py
Ikutin instruksinya."""
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent
COOKIES_FILE = BASE / "cookies.json"

print("=" * 50)
print("  🍪 AMBIL COOKIES BING")
print("  Buat MS Rewards Bot (HTTP version)")
print("=" * 50)
print()
print("Ikutin langkah ini:")
print()
print("1️⃣  BUKA Chrome/Edge di HP kamu")
print("2️⃣  Login ke Bing: https://www.bing.com/")
print("   (Pastikan udah login — foto profile muncul)")
print()
print("3️⃣  SETELAH login, buka link ini:")
print("   https://www.bing.com/search?q=test123")
print()
print("4️⃣  COPY cookies dengan salah satu cara:")
print()
print("   🔹 CARA A — Pake console (gampang):")
print("      Di browser, buka alamat:")
print("      javascript:prompt('Copy ini:',document.cookie)")
print("      ⚠️ Kalo gak work, coba paste manual ke URL bar")
print()
print("   🔹 CARA B — Pake chrome://settings:")
print("      Buka chrome://settings/siteData")
print("      Cari 'bing.com' -> expand -> copy semua cookies")
print()
print("   🔹 CARA C — Install 'Cookie-Editor' extension")
print("      (Kalo pake Kiwi Browser / Firefox)")
print()
print("5️⃣  Setelah dapet cookie string-nya, PASTE di sini:")
print()

if COOKIES_FILE.exists():
    existing = json.loads(COOKIES_FILE.read_text())
    if isinstance(existing, list) and len(existing) > 3:
        print(f"  ℹ️ cookies.json udah ada ({len(existing)} cookies)")
        yn = input("  Mau ambil ulang? (y/n): ").strip().lower()
        if yn != "y":
            print("  ✅ Pake cookies yang udah ada")
            sys.exit(0)

print("  Ketik atau paste cookie string-nya, lalu tekan Enter 2x:")
print()

lines = []
while True:
    try:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    except (EOFError, KeyboardInterrupt):
        break

cookie_str = " ".join(lines).strip()

if not cookie_str:
    print()
    print("  ❌ Gak ada input. Cookies gak berubah.")
    sys.exit(1)

# Parse cookie string jadi list of dicts (Netscape format)
cookies_list = []
for item in cookie_str.split(";"):
    item = item.strip()
    if "=" in item:
        name, value = item.split("=", 1)
        cookies_list.append({"name": name.strip(), "value": value.strip()})

# Pastiin ada cookie penting buat Bing
has_muid = any(c["name"] == "_MUID" for c in cookies_list)
has_mh = any("MUID" in c["name"] for c in cookies_list)

if not cookies_list:
    print("  ❌ Gak bisa parse cookies. Pastikan formatnya bener.")
    sys.exit(1)

# Simpan
COOKIES_FILE.write_text(json.dumps(cookies_list, indent=2))
print()
print(f"  ✅ Tersimpan {len(cookies_list)} cookies ke cookies.json")

if has_muid or has_mh:
    print("  ✅ Bing session cookies ada! Siap dipake.")
else:
    print("  ⚠️ Mungkin belum login ke Bing. Coba login dulu trus ulang.")

print()
print("  Test bot: python ms_rewards_bot.py")
print()
