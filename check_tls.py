import requests
import hashlib
import os
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://visas-it.tlscontact.com/en-us/country/by/vac/byMSQ2it/news"
LOG_FILE = "changes.log"

def send_telegram(msg):
    token = os.environ["TG_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def log_change(message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

response = requests.get(
    URL,
    timeout=30,
    headers={"User-Agent": "Mozilla/5.0"}
)

soup = BeautifulSoup(response.text, "html.parser")

# 🔍 Extract ONLY news text
news_section = soup.get_text(separator=" ", strip=True)

# Optional cleanup
news_text = " ".join(news_section.split())

current_hash = hashlib.md5(news_text.encode()).hexdigest()
old_hash = os.environ.get("PAGE_HASH")

if old_hash and old_hash != current_hash:
    message = "TLSContact NEWS updated\nhttps://visas-it.tlscontact.com/en-us/country/by/vac/byMSQ2it/news"
    log_change(message)
    send_telegram(
        f"📰 {message}\n"
        f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

print(f"PAGE_HASH={current_hash}")
