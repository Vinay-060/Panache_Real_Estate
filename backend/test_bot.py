import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio

load_dotenv()

async def main():

    bot = Bot(
        token=os.getenv(
            "TELEGRAM_BOT_TOKEN"
        )
    )

    me = await bot.get_me()

    print(me)

asyncio.run(main())