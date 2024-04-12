# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup
from config import config_file
from data.sqlite import *

async def user_menu(user_id):
	keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	if user_id in config_file.global_admins:
		keyboard.add('🔧 Панель 🔧')
	else:
		pass

	return keyboard

async def sub():
	keyboard = InlineKeyboardMarkup(row_width=1)
	links = await get_links()
	for link in links:
		if link[2] == 'channel':
			keyboard.add(InlineKeyboardButton(f' {link[3]}', url=link[0]))
	for link in links:
		if link[2] == 'bot':
			keyboard.add(InlineKeyboardButton(f' {link[3]}', url=link[0]))

	

	keyboard.add(InlineKeyboardButton(f'✅ Проверить подписки ✅', callback_data='check_sub'))
	
	return keyboard

