from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


""" Создаём кнопки и меню с кнопками """
btn_info = KeyboardButton('ℹ Форматы')
btn_json = KeyboardButton('📗 JSON')
btn_csv = KeyboardButton('📚 CSV')
btn_again = KeyboardButton('🔁 Выбрать формат')
btn_all = KeyboardButton('💾 Получить все категории')
btn_cancel = KeyboardButton('❌ Отменить выбор формата')
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_info)
choice_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_json, btn_all, btn_csv)
all_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_cancel)
repeat_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_again, btn_all)
cancel_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_all, btn_again)
