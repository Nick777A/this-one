import asyncio
import datetime
from collections import deque
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from constants import CHANNEL_ID
from database.database import get_user_data, delete_user
from section1.commands import *

user_message_queues = {}  # {user_id: deque(["msg1", "msg2", ...])}

#print all users data
@rt.message(Command("pt"))
async def printme(message: Message):
	user1_data = get_user_data()
	print(user1_data)


#list users choosen hashtags
@rt.message(Command("list_tags"))
async def list_tags(message: Message, state: FSMContext):
	user_data = get_user_data()
	user_id = str(message.from_user.id)
	tags = next((item["tags"] for item in user_data if item["user_id"] == user_id),None)
	
	if not tags:
		await message.answer("Դուք դեռ հեշթեգեր չեք ընտրել")
	else:
		strtags = ", ".join(tags)
		await message.answer(f"Ձեր ընտրած հեշթեգերը հետևյալն են {strtags}")


#catch relevant posts from channel for users choosen hashtags
@rt.channel_post()
async def handle_channel_post(message: Message, bot: Bot):
	all_users = get_user_data()
	message_content = message.text or message.caption
	if not message_content:
		return	
	for user in all_users:
		user_id = int(user["user_id"])
		tags = user.get("tags", [])
		if any(tag in message_content for tag in tags):
			if user["prfrd_time"] == 'Realtime':
				await bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
			else:
				if user_id not in user_message_queues:
						user_message_queues[user_id] = deque()  # Create queue if not exists
				user_message_queues[user_id].append(message.message_id)


#keep posts into deque and send them in time user choosed
async def send_accumulated_messages(bot):
	while True:
		all_users = get_user_data()
		now = datetime.datetime.now().time()
		for user in all_users:
			user_id = int(user["user_id"])
			prfrd_time = user['prfrd_time']
			if prfrd_time == "Realtime":
				continue
			schedule_time = datetime.datetime.strptime(prfrd_time, "%H:%M").time()
			if now.hour == schedule_time.hour and now.minute == schedule_time.minute:  
				if user_message_queues.get(user_id):
					message_ids = list(user_message_queues[user_id])
					if message_ids:
						await bot.send_message(user_id, "📢 Daily Updates:")
						for msg_id in message_ids:
							await bot.forward_message(chat_id=user_id, from_chat_id=CHANNEL_ID, message_id=msg_id)
					user_message_queues[user_id].clear()  # Clear queue after sending
		await asyncio.sleep(15)  # Check time every 30 seconds


#show info of available commands for user
@rt.message(Command("help"))
async def gethelp(message: Message):
	await message.answer("""
		📌 Հասանելի Հրամաններ

		✅ /start – Սկսել բոտի աշխատանքը։
		✅ /reg – Գրանցվել բոտում՝ նշելով նախընտրած հեշթեգները։
		✅ /tags – Տեսնել կամ փոփոխել ձեր ընտրված հեշթեգները։
		✅ /list_tags ցուցադրել ընտրված հեշթեգերը:
		✅ /unsubscribe – Չեղարկել բաժանորդագրությունը և դադարեցնել հաղորդագրությունների ստացումը։
		✅ /restart – Վերագործարկել բոտը (օգտակար է տվյալները փոփոխելու և  խնդիրների դեպքում)։
		✅ /help – Ցուցադրել այս հրահանգները։

		📢 Ինչպես Օգտագործել
		1️⃣ Օգտագործեք /reg հրամանը՝ գրանցվելու համար։
		2️⃣ Ընտրեք հետաքրքրող հեշթեգները /tags հրամանով։
		3️⃣ Բոտը կուղարկի ձեզ համապատասխան հաղորդագրությունները։
		4️⃣ Կարող եք ցանկացած պահի չեղարկել բաժանորդագրությունը /unsubscribe հրամանով։

		🚀 Հարցերի դեպքում՝ օգտագործեք /help հրամանը։
		""")


#delede user from db (no longer will get messages)
@rt.message(Command("unsubscribe"))
async def deletemydata(message: Message):
	user_id = message.from_user.id
	delete_user(user_id)
	await message.answer("Դուք հաջողությամբ ապաբաժանորդագրվել եք")


async def is_user_in_channel(bot: Bot, user_id: int, channel_id: str) -> bool:
	"""Check if the user is still in the channel."""
	try:
		member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
		return member.status in ["member", "administrator", "creator"]
	except TelegramBadRequest:  # Handles case when user is not found
		return False
	except Exception as e:
		print(f"Error checking user {user_id}: {e}")
		return False


async def check_users_periodically(bot: Bot, channel_id: str):
	"""Runs every 2 days to check if users are still in the channel."""
	while True:
		all_users = get_user_data()  # Ensure this returns a list of user IDs
		for user in all_users:
			user_id = int(user["user_id"])
			in_channel = await is_user_in_channel(bot, user_id, channel_id)

			if not in_channel:
				delete_user(user_id)
				print(f"Removed {user_id} from mailing list (left channel)")

		await asyncio.sleep(172800)  # Wait 2 days
