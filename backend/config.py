import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

COHERE_API_KEY = os.getenv(
    "COHERE_API_KEY"
)

N8N_WEBHOOK = os.getenv(
    "N8N_WEBHOOK"
)