import requests
import hashlib
import os

URL = "https://visas-it.tlscontact.com/it-it/country/by/vac/byMSQ2it/news"

def send_telegram(msg):
    token = os.environ["TG_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

response = requests.get(URL, timeout=30)
content = response.text
current_hash = hashlib.md5(content.encode()).hexdigest()

old_hash = os.environ.get("PAGE_HASH")

if old_hash and old_hash != current_hash:
    send_telegram("⚠️ TLSContact page changed!\nCheck now.")

print(f"PAGE_HASH={current_hash}")
