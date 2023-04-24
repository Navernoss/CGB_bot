import logging
import sqlite3
import datetime
import time
import string
import random

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, callback_query
from aiogram.types import CallbackQuery
from aiogram.utils import executor
from config_bot import *
from keyboards_new import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Connect to SQLite database
conn = sqlite3.connect('new.db')
cursor = conn.cursor()

# Create a 'cities' table if it doesn't exist
cursor.execute("""CREATE TABLE IF NOT EXISTS cities (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  city_name TEXT NOT NULL,
                  buisnes TEXT NOT NULL DEFAULT '',
                  money INTEGER NOT NULL DEFAULT 10000,
                  time TEXT NOT NULL
                )""")
conn.commit()

passj = None

@dp.message_handler(commands=['start'])
async def start_cmd_handler(message: types.Message):
        await message.answer('Добро пожаловать в CGB - City Game Bot! Введите /newcity, чтобы создать новый город.')


@dp.message_handler(commands=['newcity'])
async def new_city_cmd_handler(message: types.Message):
        # Check if user already has a city
        cursor.execute("SELECT * FROM cities WHERE user_id=?", (message.from_user.id,))
        city_exists = cursor.fetchone()

        username = message.from_user.username
        if city_exists:
            await message.answer('У вас уже есть город! Введите /cityinfo, чтобы увидеть статистику вашего города.')
        else:
            # Insert new city data into database
            cursor.execute("INSERT INTO cities (user_id, city_name, buisnes, time) VALUES (?, ?, '', CURRENT_TIMESTAMP)",
            (message.from_user.id, f'City {username}'))
            conn.commit()
            await message.answer('Создан новый город! Введите /cityinfo, чтобы увидеть статистику вашего города.')

@dp.message_handler(commands=['cityinfo'])
async def city_info_cmd_handler(message: types.Message):
        # Get the user's city data from the database
        cursor.execute("SELECT * FROM cities WHERE user_id=?", (message.from_user.id,))
        city_data = cursor.fetchone()

        if city_data:
            # Send the city data to the user
            city_info = f"Название города: {city_data[2]}\nБизнес: {city_data[3]}\nКазна: {city_data[4]}"
            await message.answer(city_info, parse_mode=ParseMode.MARKDOWN, reply_markup=markup_sity_info)
        else:
            await message.answer('У вас еще нет города! Введите /newcity, чтобы создать его.')


@dp.callback_query_handler(text='invested')
async def process_callback_button(callback_query: CallbackQuery):
        from_user_id = callback_query.from_user.id
        cursor.execute('SELECT money FROM cities WHERE user_id=?', (from_user_id,))
        balance = cursor.fetchone()
        new_balance = balance[0] - 500
        cursor.execute('UPDATE cities SET money=? WHERE user_id=?', (new_balance, from_user_id))
        conn.commit()

        cursor.execute('SELECT buisnes FROM cities WHERE user_id=?', (from_user_id,))
        name_buisnes = cursor.fetchone()
        my_nalogs = 0
        my_pribil = 0
        buisnes_info = f"Название бизнеса: {name_buisnes[0]}\nНалоги: {my_nalogs}/500\nПрибыль: {my_pribil}"
        await callback_query.message.answer(
            f"Вы вложили деньги в бизнес!\nПотрачено: 500 рублей\nКазна: {new_balance}\n\nВаш бизнес:\n{buisnes_info}")


@dp.callback_query_handler(text='game_button', state=None)
async def process_callback_button(callback_query: CallbackQuery, state: FSMContext):
    all_chars = string.ascii_letters + string.digits
    password = ''
    passj = password
    fake_password1 = ''
    fake_password2 = ''
    for i in range(5):
        password += random.choice(all_chars)
    for i in range(5):
        fake_password2 += random.choice(all_chars)
    for i in range(5):
        fake_password1 += random.choice(all_chars)
    three_password = [fake_password2, fake_password1, password]
    game_passwords = random.sample(three_password, k=3)
    game_button1 = InlineKeyboardButton(game_passwords[0], callback_data="gb1")
    game_button2 = InlineKeyboardButton(game_passwords[1], callback_data="gb2")
    game_button3 = InlineKeyboardButton(game_passwords[2], callback_data="gb3")
    markup_game = InlineKeyboardMarkup().add(game_button1, game_button2,game_button3)
    await callback_query.message.answer(f'Давай подзаработаем!nПеред тобой капча, снизу три кнопки. Нажми на верную капчу. Если угадаешь – получишь рандомное количество монет до 500nnn {password}', reply_markup=markup_game)
    async with state.proxy() as data:
        data['gbb1'] = game_button1
        data['gbb2'] = game_button2
        data['gbb3'] = game_button3
        data['ps'] = password

@dp.callback_query_handler(text=('gb1','gb2','gb3'), state='*')
async def process_game_button(callback_query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        game_button1 = data['gbb1']
        game_button2 = data['gbb2']
        game_button3 = data['gbb3']
        password = data['ps']
    print(callback_query.data)
    answer_user = None
    if callback_query.data == 'gb1':
        answer_user = game_button1
    elif callback_query.data == 'gb2':
        var = answer_user = game_button2
    elif callback_query.data == 'gb3':
        var = answer_user = game_button3
    print(answer_user)
    print(password)
    if answer_user['text'] == password:
        from_user_id = callback_query.from_user.id
        cursor.execute('SELECT money FROM cities WHERE user_id=?', (from_user_id,))
        balance = cursor.fetchone()
        random_sur = random.randint(100, 500)
        new_balance = balance[0] + random_sur
        cursor.execute('UPDATE cities SET money=? WHERE user_id=?', (new_balance, from_user_id))
        conn.commit()
        await callback_query.message.answer('Ты молодец!')
    else:
        await callback_query.message.answer('Ты не правильно!')
    await state.finish()


@dp.message_handler(commands=['buisnes'])
async def buisnes_start(message: types.Message):
    cursor.execute('SELECT buisnes FROM cities WHERE user_id=?', (message.from_user.id,))
    my_buis = cursor.fetchone()
    if my_buis[0]:
        await message.answer('У вас уже есть свой бизнес! Введите "мой бизнес"')
    else:
        username = message.from_user.username
        await message.answer('Вы успешно создали бизнес!')
        cursor.execute("UPDATE cities SET buisnes = ? WHERE user_id = ?", (f'Buisnes {username}', message.from_user.id))
        conn.commit()



@dp.message_handler(Text(equals='мой бизнес', ignore_case=True))
async def my_buisnes(message: types.Message):
        cursor.execute('SELECT buisnes FROM cities WHERE user_id=?', (message.from_user.id,))
        name_buisnes = cursor.fetchone()
        my_nalogs = 0
        my_pribil = 0
        if name_buisnes:
            buisnes_info = f"Название бизнеса: {name_buisnes[0]}\nНалоги: {my_nalogs}/500\nПрибыль: {my_pribil}"
            await message.answer(buisnes_info, parse_mode=ParseMode.MARKDOWN)
        else:
            await message.answer('У вас еще нет бизнеса! Введите /buisnes, чтобы создать его.')


@dp.message_handler(Text(equals='баланс', ignore_case=True))
async def balance(message: types.Message):
        cursor.execute('SELECT money FROM cities WHERE user_id=?', (message.from_user.id,))
        balance = cursor.fetchone()
        await message.answer(f'Баланс: {balance[0]}')




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

# salavat i ivan ne clone