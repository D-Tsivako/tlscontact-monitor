import requests
import hashlib
import os
from datetime import datetime
from bs4 import BeautifulSoup
import difflib

URL = "https://visas-it.tlscontact.com/it-it/country/by/vac/byMSQ2it/news"
LOG_FILE = "changes.log"
STATE_FILE = "last_news.txt"

def send_telegram(msg):
    token = os.environ["TG_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def extract_news_text(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())

def log_change(old, new):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}]\n")
        f.write("--- OLD ---\n")
        f.write(old + "\n")
        f.write("--- NEW ---\n")
        f.write(new + "\n")

def telegram_diff(old, new):
    diff = list(difflib.ndiff(old.split(), new.split()))
    added = [w[2:] for w in diff if w.startswith("+ ")]
    removed = [w[2:] for w in diff if w.startswith("- ")]

    def shorten(words, limit=40):
        return " ".join(words[:limit]) + ("..." if len(words) > limit else "")

    msg = (
        "📰 TLSContact NEWS updated\n\n"
        f"➖ Old:\n{shorten(old.split())}\n\n"
        f"➕ New:\n{shorten(new.split())}"
    )
    return msg

response = requests.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
news_text = extract_news_text(response.text)

# Load previous state
old_text = ""
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        old_text = f.read()

current_hash = hashlib.md5(news_text.encode()).hexdigest()
old_hash = os.environ.get("PAGE_HASH")

if old_hash and old_hash != current_hash:
    log_change(old_text, news_text)
    send_telegram(telegram_diff(old_text, news_text))

# Save current state
with open(STATE_FILE, "w", encoding="utf-8") as f:
    f.write(news_text)

print(f"PAGE_HASH={current_hash}")
