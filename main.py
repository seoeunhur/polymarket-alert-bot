import os
import requests
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL_SECONDS = 1 * 60 * 60  # 1시간

KEYWORDS = [
    "Fed", "rate", "interest", "CPI", "inflation", "recession", "unemployment",
    "Nvidia", "Apple", "AI", "chip", "semiconductor", "NASDAQ", "China",
    "Taiwan", "tariff", "supply chain"
]

known_bets = {}

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

def simple_translate(text):
    translations = {
        "Fed": "연준", "rate": "금리", "interest": "이자율", "CPI": "소비자물가",
        "inflation": "인플레이션", "recession": "경기침체", "unemployment": "실업",
        "Nvidia": "엔비디아", "Apple": "애플", "AI": "인공지능", "chip": "칩",
        "semiconductor": "반도체", "NASDAQ": "나스닥", "China": "중국",
        "Taiwan": "대만", "tariff": "관세", "supply chain": "공급망"
    }
    for eng, kor in translations.items():
        text = text.replace(eng, kor)
    return text

def fetch_bets():
    try:
        response = requests.get("https://blue-sunset-f0d1.lovelycococo.workers.dev/")
        if response.status_code == 200:
            return response.json().get("markets", [])
    except Exception as e:
        send_telegram_message(f"⚠️ Polymarket API 에러: {e}")
    return []

def check_bets():
    global known_bets
    new_bets = []
    updated_bets = []
    bets = fetch_bets()

    for bet in bets:
        title = bet.get("title", "")
        bet_id = bet.get("id")
        updated = bet.get("lastUpdatedTimestamp", 0)
        if not bet_id:
            continue

        if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
            if bet_id not in known_bets:
                new_bets.append(title)
            elif known_bets[bet_id] != updated:
                updated_bets.append(title)

    message = ""
    if new_bets:
        message += "🆕 [새로운 베팅]\n"
        for title in new_bets:
            message += f"- {title}\n({simple_translate(title)})\n\n"

    if updated_bets:
        message += "♻️ [업데이트된 베팅]\n"
        for title in updated_bets:
            message += f"- {title}\n({simple_translate(title)})\n\n"

    if message:
        send_telegram_message(message.strip())

    known_bets = {bet.get("id"): bet.get("lastUpdatedTimestamp", 0) for bet in bets if bet.get("id")}

if __name__ == "__main__":
    send_telegram_message("✅ Railway 봇이 시작되었습니다.")
    while True:
        check_bets()
        time.sleep(CHECK_INTERVAL_SECONDS)
