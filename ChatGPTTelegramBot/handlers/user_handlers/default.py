# - *- coding: utf- 8 - *-
import asyncio

from loader import dp, bot
from keyboards.user_keyboard import *
from data.sqlite import *
from states.user_states import Chat
from config.config_file import *

from functions.check_subscribe import subscribed
from misc import rate_limit
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram import types
import openai
from keyboards.admin_keyboard import admin_menu
openai.api_key = "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"
model_engine = 'text-davinci-003'

@rate_limit(limit=2)
@dp.message_handler(commands=['start'], state="*")
async def start(message: types.message, state: FSMContext):
    me = await bot.get_me()
    await state.finish()
    user = await get_user(message.from_user.id)
    if user is None:
        if ' ad-' in message.text:
            codes = await get_codes_adlinks()
            code = message.text.replace('/start ', '').strip()
            if (code, ) in codes:
                await add_count_adlink(code)
                count = await get_count_adlink(code)
                ln = await user_link(message.from_user.id, 'Юзер')
                await bot.send_message(global_admins[0], f'<b>{ln} вступил по вашей ссылке с кодом:</b> <code>{code}</code>\n<i>Всего вступивших:</i> <code>{count[0]}</code>')
        await register_user(message.from_user.id)
        if await subscribed(message.from_user.id):
            await message.answer(text='<b>👋🏻 Добро пожаловать в ChatGPT!👋🏻</b> \n 👇🏻 Задавай свой вопрос ниже! 👇🏻 ', reply_markup=await user_menu(message.from_user.id))
        else:
            await message.answer(await dont_sub_message(), reply_markup=await sub())
    else:
        if await subscribed(message.from_user.id):
            await message.answer(text='<b>👋🏻 Добро пожаловать в ChatGPT!👋🏻</b> \n 👇🏻 Задавай свой вопрос ниже! 👇🏻 ', reply_markup=await user_menu(message.from_user.id))
        else:
            await message.answer(await dont_sub_message(), reply_markup=await sub())


@dp.callback_query_handler(lambda c: c.data == 'check_sub', state = '*')
async def check_sub_handler(c: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if await subscribed(c.from_user.id):
        await bot.delete_message(c.from_user.id, c.message.message_id)
        text = '''
        👋🏻 <b>Приветствую!</b>

<i><b>Советую прочитать полностью прежде чем начать писать различные вопросы</b></i>


1. Сложные вопросы рекомендуется задавать на английском языке, поскольку бот воспринимает его точнее и быстрее отвечает на вопросы

2. Будьте конкретны и ясны: задавая вопрос, предоставьте как можно больше релевантной информации, чтобы бот выдал то, что вам нужно.

3. Используйте правильную грамматику и орфографию: так боту будет легче понять сообщение и точнее ответить на него.

4. Избегайте использования аббревиатур или текстовой речи: это может затруднить боту понимание того, что вы пытаетесь донести.

5. Задавайте по одному вопросу за раз: Если у вас есть несколько вопросов, лучше задавать их по одному, чтобы бот дал четкий и целенаправленный ответ.

6. Укажите контекст: Если ваш вопрос связан с определенной темой, предоставьте некоторую справочную информацию, которая поможет боту понять, о чем вы спрашиваете.

7. Будьте терпеливы: бот является языковой моделью искусственного интеллекта, и ему может понадобиться некоторое время, чтобы обработать ваш запрос. Ответы на некоторые вопросы могут длиться до 2 минут.

Примеры вопросов:
Как вычислять интеграл?
Доклад на тему Александра Сергеевича Пушкина.
Напиши рецепт блинов.


Скорее пиши свой вопрос 👇🏻
 <b></b>
'''
        await bot.send_message(c.from_user.id, text=text, reply_markup=await user_menu(c.from_user.id))
    else:
        await bot.send_message(c.from_user.id, await dont_sub_message(), reply_markup=await sub())

async def text(txt: str):
    return txt

@rate_limit(limit=2)
@dp.message_handler()
async def Respond(message: types.Message):
    if await subscribed(message.from_user.id):
        answer = await bot.send_message(chat_id=message.from_user.id,
                                        text='⏳ Подождите, ваш запрос обрабатывается... ⏳ ')
        await text(answer)
        await asyncio.sleep(1)
        completion = openai.Completion.create(
            engine='text-davinci-003',
            prompt=message.text,
            max_tokens=1024,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)
        await bot.delete_message(chat_id=message.from_user.id, message_id=answer.message_id)
        await message.answer(completion.choices[0].text)
    else:
        await message.answer(await dont_sub_message(), reply_markup=await sub())

