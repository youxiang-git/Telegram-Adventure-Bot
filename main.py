import telegram
import asyncio
import constants_secrets as secrets

async def main():
    bot = telegram.Bot(secrets.TELEGRAM_API_KEY)
    async with bot:
        print(await bot.get_me())


if __name__ == '__main__':
    asyncio.run(main())