from aiogram import Router, F, types, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import pandas as pd
import re
import section1.keyboards as kb
from section1.keyboards import timelist
from constants import THE_ID
import database.database as db

#initialization of router (instead of dispatcher)
rt = Router()

#info of current user in registr
usr_data = {}

#class for states
class Registr(StatesGroup):
	name = State()
	age = State()
	email = State()
	prfrd_time = State()
	hashtags = State()


#command start and restart
@rt.message(Command("start", "restart"))
async def strt(message: Message, state: FSMContext):
	await message.answer("""Բարև, նախ պետք է գրանցվել /reg հրամանով""")


#for registration
@rt.message(Command("reg"))
async def reg(message: Message, state: FSMContext):
	await state.set_state(Registr.name)
	await message.answer("Անուն Ազգանուն")
	
#taking name
@rt.message(Registr.name)
async def stepone(message: Message, state: FSMContext):
	await state.update_data(name=message.text)
	await state.set_state(Registr.age)
	await message.answer("Տարիք")

#taking age (only digits from 12 to 85)
@rt.message(Registr.age)
async def steptwo(message: Message, state: FSMContext):
	if not message.text.isdigit():
		await message.answer("Խնդրում եմ մուտքագրել միայն թվեր")
		return
	age = int(message.text)
	if 12 <= age <= 85:
		await state.update_data(age=age)
		await state.set_state(Registr.email)
		await message.answer("էլեկտրոնային հասցե «email»")
	else:
		await message.answer("Տարիքը պետք է լինի 12-85 միջակայքում։ Խնդրում եմ կրկին մուտքագրել:")

#take email (only @gmail.com #yahoo.com, @outlook.com, @mail.ru, @icloud.com)
@rt.message(Registr.email)
async def steptre(message: Message, state: FSMContext):
	email = message.text.strip()
	allowed_domains = ["gmail.com", "yahoo.com", "outlook.com", "mail.ru", "icloud.com"]
	email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(?:com|net|org|edu|gov|mil|biz|info|ru|am)$"
	if not re.match(email_pattern, email):
		await message.answer("Խնդրում եմ մուտքագրել վավեր email (օրինակ՝ example@gmail.com)")
		return
	domain = email.split("@")[-1]
	if domain not in allowed_domains:
		await message.answer(f"Email-ը պետք է ավարտվի {', '.join(allowed_domains)}-ով։ Փորձեք կրկին:")
		return
	await state.update_data(email=email)
	await state.set_state(Registr.prfrd_time)
	await message.answer("նախընտրելի ժամ՝ 8:00, 13:00, 21:00", reply_markup=kb.settime())


#callback for available times via inline kb
@rt.callback_query(F.data.in_(timelist))
async def stepfor(callback: CallbackQuery, state: FSMContext):
	await state.update_data(prfrd_time=callback.data)
	await callback.message.answer("Այժմ կարող եք ընտրել հեշթեգերը /tags")
	await callback.answer("ընտրությունը պահպանված է")


#choose hashtags
@rt.message(Command("tags"))
async def tags(message: Message, state: FSMContext):
	await state.set_state(Registr.hashtags)
	await state.update_data(tags=[])
	await message.answer("""
		Ընտրեք տարբերակներից մաքսիմւմ 3ը,
		սխալ հեշթեգ ընտրելու դեպքում կրկին սեղմեք /tags հրամանին 
		այնուհետև նորից ընտրեք անհրաժեշտները,
		ավարտելուց հետո օգտագործեք /finish հրամանը և
		ընտրված հեշթեգերը տեսնելու համար կիրառեք /list_tags հրամանը""", reply_markup=kb.inlinetags1())


#callback of inlinekb hashtags
@rt.callback_query()
async def handle_hashtags(callback: CallbackQuery, state: FSMContext):
	hashtag = callback.data
	usr_data = await state.get_data()
	tags = usr_data.get("tags", [])
	max_tags = 3
	if hashtag in tags:
		await callback.answer("❗ Դուք արդեն ընտրել եք այս հեշթեգը։")
		return
	
	if len(tags) >= max_tags:
		await callback.answer(f"❌ Կարող եք ընտրել առավելագույնը {max_tags} հեշթեգ։")
		return

	tags.append(hashtag)
	await state.update_data(tags=tags)
	await callback.answer(f"Դուք ընտրել եք {hashtag}-ը")


#save data in exel file
async def save_to_excel():
	x_files = db.get_user_data()
	df = pd.DataFrame(x_files)
	df.to_excel("userdata.xlsx", index=False, engine="openpyxl")


#finish registration
@rt.message(Command('finish'))
async def send_file(message: Message, state: FSMContext):
	usr_data = {"user_id": message.from_user.id}
	usr_data.update(await state.get_data())
	db.addtodb(usr_data)
	await state.clear()

	await message.answer("Տվյաները հաջողությամբ պահպանվել են")


#command for admin to get exel file
@rt.message(Command('getdata'))
async def send_excel(message: Message, bot: Bot):
	await save_to_excel()
	excel_file = "userdata.xlsx"
	input_file = FSInputFile(excel_file)
	nk_id = THE_ID
	await bot.send_document(chat_id=nk_id, document=input_file)


