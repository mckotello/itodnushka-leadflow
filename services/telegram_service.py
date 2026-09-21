import os

import httpx
from dotenv import load_dotenv


load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

PROXY = os.getenv(
    "TELEGRAM_PROXY"
)


if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        "Не задан TELEGRAM_BOT_TOKEN в .env"
    )


if not TELEGRAM_CHAT_ID:
    raise RuntimeError(
        "Не задан TELEGRAM_CHAT_ID в .env"
    )


TELEGRAM_URL = (
    f"https://api.telegram.org/bot"
    f"{TELEGRAM_BOT_TOKEN}/sendMessage"
)


def send_telegram_message(message: str) -> None:
    with httpx.Client(
        proxy=PROXY,
        timeout=20.0,
    ) as client:

        response = client.post(
            TELEGRAM_URL,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
            },
        )

        response.raise_for_status()