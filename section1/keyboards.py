from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

#list of messages sending times
timelist = ["9:00", "12:00", "15:00", "18:00", "21:00", "00:00", "Realtime"]

#list of hashtags
hashtags = ["#Volunteering",
"#YouthProjects",
"#Education",
"#Career",
"#Internships",
"#Networking",
"#Scholarships",
"#ErasmusPlus",
"#Leadership",
"#Events",
"#PersonalDevelopment",
"#Community",
"#StudentLife",
"#NGO",
"#Workshops",
"#SoftSkills",
"#Teamwork",
"#Innovation",
"#Sustainability",
"#CulturalExchange",
"#Eco",
"#ArtAndCulture",
"#Language",
"#ClimateAction",
"#Europ"
]


#function to show available times to get messages
def settime():
	keyboard = InlineKeyboardBuilder()
	for elem in timelist:
		keyboard.add(InlineKeyboardButton(text=elem, callback_data=elem))
	return keyboard.adjust(1).as_markup()


#function to show available hashtags
def inlinetags1():
	keyboard = InlineKeyboardBuilder()
	for elem in hashtags:
		keyboard.add(InlineKeyboardButton(text=elem, callback_data=elem))
	return keyboard.adjust(2).as_markup()

