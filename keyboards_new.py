from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.types import CallbackQuery


keyboard_start = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_start.row('\U0001F3D9 Начать зарабатывать')


invest_button = InlineKeyboardButton("Вложить деньги", callback_data="invested")
game_button = InlineKeyboardButton("Начать получать деньги", callback_data="game_button")
markup_sity_info = InlineKeyboardMarkup().add(invest_button, game_button)

invest_button = InlineKeyboardButton("Вложить деньги", callback_data="invested")
markup_invested = InlineKeyboardMarkup().add(invest_button)
