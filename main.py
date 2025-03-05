from aiogram import Dispatcher

from constants import TOKEN, CHANNEL_ID
from section1.extendedcommands import asyncio, rt, Bot, send_accumulated_messages, check_users_periodically

#intializating bot with token
bot = Bot(token=TOKEN)
dp=Dispatcher()


async def main():
	#run message mailing
	asyncio.create_task(send_accumulated_messages(bot))
	asyncio.create_task(check_users_periodically(bot, str(CHANNEL_ID)))
	dp.include_router(rt)
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
