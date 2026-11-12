"""Send a text message with Twilio.

Run this file directly to send yourself a test text:
    python send_text.py
"""
import os

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()


def send_sms(message):
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    result = client.messages.create(
        body=message,
        from_=os.getenv("TWILIO_FROM_NUMBER"),
        to=os.getenv("MY_PHONE_NUMBER"),
    )
    return result.sid


if __name__ == "__main__":
    sid = send_sms("Concert Radar test: if you can read this, Twilio is working.")
    print(f"Sent! Message ID: {sid}")
