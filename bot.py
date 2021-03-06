from aiogram import Bot, Dispatcher, executor, types
from settings import TOKEN
import json
import markup as nav
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage


""" Задаём глобальные настройки для бота """
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


class DataInput(StatesGroup):
    """ Класс состояния """
    r = State()


class DataCSV(StatesGroup):
    """ Класс состояния """
    c = State()


with open('data/number_parser.txt', encoding='utf-8') as file:
    reader = int(file.read().count('0'))
    number = reader - 1


@dp.message_handler(commands='start')
async def start(message: types.Message):
    """ Функция приветствия """
    await message.answer('Чтобы выбрать формат .json или .csv, а затем выбрать нужную вам категорию, нажмите'
                         ' на кнопку "ℹ Форматы" и выберите нужный вам формат.',
                         reply_markup=nav.main_menu)


@dp.message_handler(Text(equals='ℹ Форматы'))
async def bot_message(message: types.Message):
    """ Функция просмотра форматов """
    await message.reply('Выберите нужный вам формат файла .json или .csv. Или выберите все товары сразу',
                        reply_markup=nav.choice_menu)


@dp.message_handler(Text(equals='📗 JSON'))
async def bot_message_json(message: types.Message):
    """ Функция, которая присылает категории и выбранный формат """
    with open('data/categories.json', encoding='utf-8') as file_0:
        products_dict = json.load(file_0)
    count = 0
    for k, v in products_dict.items():
        category = f"{count}. {v['category_name']}"
        await message.answer(category)
        count += 1
    await message.answer('Теперь напишите номер нужной вам категории.\nПример: "17" (ПИСАТЬ БЕЗ КАВЫЧЕК!!!).',
                         reply_markup=nav.all_menu)
    await DataInput.r.set()


@dp.message_handler(state=DataInput.r)
async def answer_json(message: types.Message, state: FSMContext):
    """ Функция присылающая нужный файл """
    r = message.text
    if r == '❌ Отменить выбор формата':
        await state.finish()
        await message.reply('Вы отменили выбранный вами формат', reply_markup=nav.cancel_menu)
    else:
        try:
            with open(f"data/{str(r)}.csv", 'rb') as file_0:
                await message.reply_document(file_0, reply_markup=nav.cancel_menu)
                await state.finish()
        except Exception as ex:
            print(ex)


@dp.message_handler(Text(equals='📚 CSV'))
async def bot_message_csv(message: types.Message):
    """ Функция, которая присылает категории и выбранный формат """
    with open('data/categories.json', encoding='utf-8') as file_0:
        products_dict = json.load(file_0)
    count = 0
    for k, v in products_dict.items():
        category = f"{count}. {v['category_name']}"
        await message.answer(category)
        count += 1
    await message.answer('Теперь напишите номер нужной вам категории.\nПример: "17" (ПИСАТЬ БЕЗ КАВЫЧЕК!!!).',
                         reply_markup=nav.all_menu)
    await DataCSV.c.set()


@dp.message_handler(state=DataCSV.c)
async def answer_json(message: types.Message, state: FSMContext):
    c = message.text
    if c == '❌ Отменить выбор формата':
        await state.finish()
        await message.reply('Вы отменили выбранный вами формат', reply_markup=nav.cancel_menu)
    else:
        try:
            with open(f"data/{str(c)}.csv", 'rb') as file_0:
                await message.reply_document(file_0, reply_markup=nav.cancel_menu)
                await state.finish()
        except Exception as ex:
            print(ex)


@dp.message_handler(Text(equals='🔁 Выбрать формат'))
async def bot_message_repeat(message: types.Message):
    """ Функция выбора формата """
    await message.reply('Выберите формат файла!', reply_markup=nav.choice_menu)


@dp.message_handler(Text(equals='💾 Получить все категории'))
async def bot_message_all(message: types.Message):
    """ Функция, которая присылает категории и выбранный формат """
    try:
        with open(f"data/{number}_all_products.json", 'rb') as file_send:
            await message.reply_document(file_send)
        with open(f"data/{number}_all_products.csv", 'rb') as file_send:
            await message.reply_document(file_send)
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    executor.start_polling(dp)
