import requests

# Replace with your bot token and chat ID
BOT_TOKEN = "7871812634:AAEueFv9sf9qRLfCDIhABXXsdzc-U2ww0fs"
CHAT_ID = "5344646197"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram alert sent!")
        else:
            print("❌ Failed to send alert:", response.text)
    except Exception as e:
        print("❌ Error:", e)
if __name__ == "__main__":
    send_telegram_alert("🚨 Test Alert: Vehicle overspeeding detected!")
