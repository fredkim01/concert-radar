"""Send an alert to your phone using ntfy.sh (free push notifications).

Run this file directly to send yourself a test notification:
    python notify.py
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def send_alert(message):
    print(f"ALERT: {message}\n")

    topic = os.getenv("NTFY_TOPIC")
    if not topic:
        print("(NTFY_TOPIC is not set in .env, so no notification was sent)")
        return

    response = requests.post(
        f"https://ntfy.sh/{topic}",
        data=message.encode("utf-8"),
        headers={"Title": "Concert Radar"},
        timeout=20,
    )
    response.raise_for_status()


if __name__ == "__main__":
    send_alert("Concert Radar test: if you see this on your phone, notifications work.")
