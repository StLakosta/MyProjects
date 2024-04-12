# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters.state import State, StatesGroup


class Chat(StatesGroup):
    chat_gpt = State()

